from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
import argparse,json,threading,time,collections
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from simulation.machine.model import Machine
from simulation.faults.catalog import FAULTS
from hmi.backend.io_adapter import PLCLink

class Application:
    def __init__(self,accelerated=False,adapter=None):
        self.machine=Machine(); self.out={}; self.mode=2; self.accelerated=accelerated
        self.lock=threading.RLock(); self.queue=collections.deque([{'cold':1}]); self.error='Connecting to Beremiz'; self.quit=False
        self.connected=False; self.comm_until=0.; self.link=adapter or PLCLink(); self.log_count=0
        (ROOT/'logs').mkdir(exist_ok=True)
    def state(self):
        with self.lock:
            return self.machine.state()|dict(plc=self.out,connection=self.connected,error=self.error,accelerated=self.accelerated,fault_catalog=FAULTS)
    def command(self,c):
        with self.lock:
            op=c.get('action')
            if op=='mode':
                if self.out.get('Q_Running'): raise ValueError('STOP before changing mode')
                mode=int(c['value'])
                if mode not in [1,2,3]: raise ValueError('Invalid mode')
                self.mode=mode
            elif op in ['start','stop','reset']: self.queue.append({op:1})
            elif op=='fault':
                name=c['name']; on=bool(c['on'])
                if not on and self.out.get('Q_Running'): raise ValueError('STOP before virtual fault clearing/reloading')
                self.machine.inject(name,on)
                if name=='communication_timeout': self.comm_until=time.monotonic()+.8 if on else 0.
            elif op=='recipe':
                if self.out.get('Q_Running'): raise ValueError('STOP before recipe changes')
                r={k:float(c['recipe'][k]) for k in self.machine.recipe}
                if not (10<=r['product_length']<=100 and r['product_length']+30<=r['bag_pitch']<=300 and 5<=r['speed']<=10 and abs(r['film_offset'])<=5 and abs(r['seal_offset'])<=.03):
                    raise ValueError('Length 10..100, pitch length+30..300, speed 5..10, film offset +/-5 mm, seal offset +/-0.03 cycles')
                self.machine.recipe=r
                # An actual recipe change restarts the virtual batch at a known phase.
                self.machine=Machine(r); self.queue.append({'cold':1})
            elif op=='speedup':
                if self.out.get('Q_Running'): raise ValueError('STOP before changing time mode')
                self.accelerated=bool(c['value'])
            else: raise ValueError('Unknown action')
    def run(self):
        try:
            with (ROOT/'logs/session.jsonl').open('a',encoding='utf-8') as log:
                while not self.quit:
                    begin=time.monotonic()
                    if begin<self.comm_until:
                        with self.lock: self.connected=False; self.error='Injected communication timeout; model frozen'
                        time.sleep(.02); continue
                    with self.lock:
                        dt=.2 if self.accelerated else .02
                        command=self.queue[0] if self.queue else {}
                        inputs=self.machine.inputs(command|{'mode':self.mode},dt,self.out)
                    try: output=self.link.exchange(inputs)
                    except TimeoutError as e:
                        with self.lock: self.connected=False; self.error=str(e)
                        time.sleep(.1); continue
                    with self.lock:
                        self.connected=True; self.error=''
                        if command: self.queue.popleft()
                        self.out=output; self.machine.step(output,dt)
                        if self.machine.events:
                            for event in self.machine.events: log.write(json.dumps(event)+'\n')
                            self.machine.events=[]; log.flush()
                    time.sleep(max(0,.02-(time.monotonic()-begin)))
        except Exception as e:
            with self.lock: self.connected=False; self.error=f'Machine worker stopped: {type(e).__name__}: {e}'
            raise
        finally: self.link.close()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--accelerated',action='store_true'); parser.add_argument('--port',type=int,default=8080); args=parser.parse_args()
    app=Application(args.accelerated)
    class Handler(BaseHTTPRequestHandler):
        def respond(self,status,data,content='application/json'):
            body=json.dumps(data).encode() if content=='application/json' else data
            self.send_response(status); self.send_header('Content-Type',content); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            if self.path=='/api/state': self.respond(200,app.state())
            elif self.path in ['/','/index.html']: self.respond(200,(ROOT/'hmi/frontend/index.html').read_bytes(),'text/html; charset=utf-8')
            else: self.respond(404,{'error':'Not found'})
        def do_POST(self):
            if self.path!='/api/command': return self.respond(404,{'error':'Not found'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if size>8192: raise ValueError('Request too large')
                app.command(json.loads(self.rfile.read(size))); self.respond(200,{'ok':True})
            except (ValueError,KeyError,TypeError) as e: self.respond(400,{'error':str(e)})
        def log_message(self,*args): pass
    worker=threading.Thread(target=app.run,daemon=True); worker.start()
    http=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'MHFW-01 HMI: http://127.0.0.1:{args.port}',flush=True)
    try: http.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        app.command({'action':'stop'}); time.sleep(.15); app.quit=True; http.server_close(); worker.join(1)
if __name__=='__main__': main()
