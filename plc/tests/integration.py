"""Real native Beremiz ST + UDP + Python machine integration tests.
Requires exclusive runtime ownership; do not run alongside HMI."""
import sys,time,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from hmi.backend.io_adapter import PLCLink,FRAME,MAPPING
from simulation.machine.model import Machine

class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.link=PLCLink(); cls.results=[]
    @classmethod
    def tearDownClass(cls):
        cls.link.close(); (ROOT/'logs').mkdir(exist_ok=True)
        (ROOT/'logs/integration_metrics.json').write_text(json.dumps(cls.results,indent=2))
    def setUp(self):
        self.m=Machine(); self.out={}; self.mode=2
        self.tick(stop=1); self.tick(cold=1); self.tick(); self.tick(reset=1); self.tick()
        self.assertEqual(self.out['Q_Alarm'],0)
    def tearDown(self): self.tick(stop=1)
    def tick(self,**commands):
        self.out=self.link.exchange(self.m.inputs(commands|{'mode':self.mode},.2,self.out)); self.m.step(self.out,.2); return self.out
    def run_seconds(self,seconds):
        for _ in range(round(seconds/.2)): self.tick()
    def start(self): self.tick(start=1); self.tick(); self.assertTrue(self.out['Q_Running'])
    def fault_case(self,name,alarm,max_seconds=35):
        self.start(); self.run_seconds(3); self.m.inject(name,True)
        for _ in range(round(max_seconds/.2)):
            self.tick()
            if self.out['Q_Alarm']: break
        self.assertEqual(int(self.out['Q_Alarm']),alarm)
        self.assertFalse(self.out['Q_Running']); self.assertFalse(self.out['Q_FilmFeedEnable'])
        self.tick(start=1); self.assertFalse(self.out['Q_Running'])
        self.results.append(dict(test=self._testMethodName,alarm=alarm,time=self.m.time))
    def test_01_normal_auto(self):
        self.start(); self.run_seconds(60); self.tick()
        self.assertEqual(self.out['Q_Alarm'],0); self.assertGreaterEqual(self.out['Q_Count'],9)
        self.assertEqual(self.out['Q_Reject'],0); self.assertEqual(self.out['Q_Count'],self.m.packages)
        self.assertTrue(any(p['packed'] for p in self.m.products))
        self.results.append(dict(test='normal_auto',sim_seconds=60,count=self.out['Q_Count'],reject=self.out['Q_Reject'],rate=10))
    def test_02_product_missing(self): self.fault_case('product_missing',1)
    def test_03_arrival_delay(self): self.fault_case('arrival_delay',1,55)
    def test_04_film_end(self): self.fault_case('film_end',4)
    def test_05_film_position_error(self): self.fault_case('film_position_error',5)
    def test_06_seal_zone(self): self.fault_case('product_in_seal_zone',6)
    def test_07_axis_following(self): self.fault_case('axis_following_error',7)
    def test_08_communication_timeout(self):
        self.start(); time.sleep(.75); self.tick()
        self.assertEqual(self.out['Q_Alarm'],10); self.assertFalse(self.out['Q_Running'])
        self.tick(); self.tick(reset=1); self.tick(); self.assertEqual(self.out['Q_Alarm'],0)
        self.assertFalse(self.out['Q_Running']); self.tick(start=1); self.assertTrue(self.out['Q_Running'])
    def test_09_stop_restart(self):
        self.start(); self.run_seconds(2); self.tick(stop=1); position=self.m.axes[1].position
        self.run_seconds(1); self.assertAlmostEqual(position,self.m.axes[1].position,places=3)
        self.assertEqual(self.out['Q_Mode'],4); self.tick(start=1); self.assertTrue(self.out['Q_Running'])
    def test_10_reset_denied(self):
        self.start(); self.m.inject('film_end',True); self.tick(); self.tick(reset=1)
        self.assertEqual(self.out['Q_Alarm'],4); self.assertFalse(self.out['Q_ResetAllowed'])
        self.tick(start=1); self.assertFalse(self.out['Q_Running'])
        self.m.inject('film_end',False); self.tick(); self.assertEqual(self.out['Q_Alarm'],4)
        self.tick(reset=1); self.assertEqual(self.out['Q_Alarm'],0); self.assertFalse(self.out['Q_Running']); self.assertEqual(self.out['Q_Mode'],4)
    def test_11_pitch_change(self):
        self.m=Machine(dict(product_length=60,bag_pitch=150,speed=10,film_offset=0,seal_offset=0))
        self.tick(cold=1); self.tick(); self.start(); self.run_seconds(18.5)
        self.assertEqual(self.out['Q_Pitch'],150); self.assertEqual(self.out['Q_Speed'],25)
        self.assertGreaterEqual(self.out['Q_Count'],3); self.assertEqual(self.out['Q_Alarm'],0)
    def test_12_speed_change(self):
        self.m.recipe['speed']=5; self.start(); self.run_seconds(36.5)
        self.assertEqual(self.out['Q_Speed'],10); self.assertGreaterEqual(self.out['Q_Count'],3); self.assertEqual(self.out['Q_Alarm'],0)
    def test_13_double_feed(self): self.fault_case('double_feed',3)
    def test_14_film_slip(self): self.fault_case('film_slip',5)
    def test_15_sensor_stuck_on(self): self.fault_case('sensor_stuck_on',2)
    def test_16_sensor_stuck_off(self): self.fault_case('sensor_stuck_off',1)
    def test_17_single_cycle(self):
        self.mode=3; self.start(); self.run_seconds(8)
        self.assertFalse(self.out['Q_Running']); self.assertEqual(self.out['Q_Count'],1); self.assertEqual(self.out['Q_Alarm'],0)
    def test_18_guard_and_estop(self):
        for fault in ['guard_open','estop']:
            self.m.inject(fault,True); self.tick(); self.assertEqual(self.out['Q_Alarm'],9)
            self.m.inject(fault,False); self.tick(); self.tick(reset=1); self.tick(); self.assertEqual(self.out['Q_Alarm'],0)
    def test_19_invalid_recipe(self):
        self.m.recipe['bag_pitch']=50; self.tick(); self.assertEqual(self.out['Q_Alarm'],11); self.tick(start=1); self.assertFalse(self.out['Q_Running'])
    def test_20_manual(self):
        self.mode=1; self.start(); self.run_seconds(2); self.assertEqual(self.out['Q_Mode'],1); self.assertGreater(self.m.axes[0].position,30)
    def test_21_duplicate_packet(self):
        # Replaying a frame must not execute the acknowledgement twice.
        self.m.ack=1; self.tick(); self.assertEqual(self.out['Q_Count'],1)
        self.link.sequence-=1; self.m.ack=1; self.tick(); self.assertEqual(self.out['Q_Count'],1)
    def test_22_sensor_reset_denied(self):
        self.fault_case('sensor_stuck_on',2)
        self.tick(reset=1); self.assertEqual(self.out['Q_Alarm'],2)
        self.m.inject('sensor_stuck_on',False); self.tick(); self.tick(reset=1)
        self.assertEqual(self.out['Q_Alarm'],0); self.assertFalse(self.out['Q_Running'])
    def test_23_jam(self): self.fault_case('jam',8)
    def test_24_replacement_client(self):
        self.start(); time.sleep(.65)
        replacement=PLCLink(); replacement.sequence=1
        try:
            out=replacement.exchange(self.m.inputs({'mode':2},.2,self.out))
            self.assertEqual(out['Q_Alarm'],10); self.assertFalse(out['Q_Running'])
        finally: replacement.close()
        time.sleep(.65); self.tick(); self.tick(reset=1); self.tick()
        self.assertEqual(self.out['Q_Alarm'],0)
if __name__=='__main__': unittest.main(verbosity=2)
