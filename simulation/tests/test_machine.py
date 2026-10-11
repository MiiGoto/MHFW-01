import unittest
from unittest.mock import Mock
from simulation.physics.axis import Axis
from simulation.machine.model import Machine
class MachineUnit(unittest.TestCase):
    def test_acceleration_and_freeze(self):
        a=Axis(max_velocity=20,max_acceleration=100); a.step(100,.02)
        self.assertAlmostEqual(a.velocity,2); self.assertAlmostEqual(a.acceleration,100)
        p=a.position; a.step(100,.02,True); self.assertEqual(p,a.position); self.assertGreater(a.error,90)
    def test_product_collision_sensor(self):
        m=Machine(); m.inject('double_feed',True)
        self.assertTrue(m.inputs({},.02,{})['I_DoubleFeed'])
    def test_kinematic_determinism(self):
        a,b=Machine(),Machine()
        for i in range(100):
            output=dict(Q_InfeedTarget=i*.4,Q_FilmTarget=i*.4,Q_CenterTarget=i*.4,Q_DischargeTarget=i*.4,Q_EndSealTarget=40,Q_InfeedRun=1)
            a.step(output,.02); b.step(output,.02)
        self.assertEqual(a.state(),b.state())
    def test_udp_startup_port_unreachable(self):
        from hmi.backend.io_adapter import PLCLink
        link=PLCLink(); link.sock.close(); link.sock=Mock()
        link.sock.recvfrom.side_effect=ConnectionResetError('Windows startup ICMP response')
        with self.assertRaises(TimeoutError): link.exchange({})
        self.assertEqual(link.sock.sendto.call_count,3)
        pending=link.pending
        with self.assertRaises(TimeoutError): link.exchange({'I_PackagedAck':1})
        self.assertEqual(pending,link.pending)
if __name__=='__main__': unittest.main(verbosity=2)
