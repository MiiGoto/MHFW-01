"""Transport only. PLC inputs/outputs are exchanged with native Beremiz ST."""
import socket,struct,json,time
from typing import Protocol
from pathlib import Path
MAPPING=json.loads((Path(__file__).resolve().parents[2]/'plc/io_mapping/signals.json').read_text())
FRAME=struct.Struct('<4sI64f')
class IOAdapter(Protocol):
    def exchange(self,inputs:dict)->dict: ...
    def close(self)->None: ...
class PLCLink:
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); self.sock.settimeout(.15)
        self.sequence=int(time.time()*1000)&0xffffffff
        self.pending=None
    def exchange(self,inputs):
        if self.pending is None:
            self.sequence+=1
            values=[float(inputs.get(n,0)) for n in MAPPING['inputs']]; values+=[0.]*(64-len(values))
            self.pending=FRAME.pack(b'MHF1',self.sequence,*values)
        packet=self.pending
        for _ in range(3):
            self.sock.sendto(packet,('127.0.0.1',15020))
            try:
                data,_=self.sock.recvfrom(2048)
                if len(data)!=FRAME.size: continue
                magic,seq,*v=FRAME.unpack(data)
                if magic==b'MHF1' and seq==self.sequence:
                    self.pending=None
                    return dict(zip(MAPPING['outputs'],v))
            except (socket.timeout,ConnectionResetError,ConnectionRefusedError):
                # Windows reports ICMP port-unreachable as WSAECONNRESET while
                # Beremiz is still starting. Retry; never kill the machine loop.
                pass
        raise TimeoutError('Beremiz runtime I/O did not reply on 127.0.0.1:15020')
    def close(self): self.sock.close()
