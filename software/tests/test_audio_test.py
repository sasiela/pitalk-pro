import importlib.util
import io
import pathlib
import sys
import threading
import unittest
sys.dont_write_bytecode = True
from unittest.mock import patch, Mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'rootfs/opt/sqlink-web'))
import audio_test as a

class AudioTests(unittest.TestCase):
 def setUp(self): a.JOB=None
 def job(self,mode='microphone'):
  return dict(id='test',owner='owner',mode=mode,active=True,cancel=threading.Event(),db=-60,peak=0,seconds=0)
 def test_levels_silence_and_full_scale(self):
  self.assertEqual(a.levels(b'\0'*3200),(-60,0))
  db,peak=a.levels(b'\xff\x7f'*1600)
  self.assertAlmostEqual(db,0);self.assertGreater(peak,.99)
 def test_start_validates_radio_and_mode(self):
  with self.assertRaises(ValueError):a.start('x','anything')
  with patch.object(a,'radio_idle',return_value=False),self.assertRaises(ValueError):a.start('x','output')
 def test_busy_owner_and_cancel(self):
  a.JOB=self.job();a.JOB['message']='Testing'
  self.assertNotIn('owner',a.snapshot('owner'));self.assertNotIn('id',a.snapshot('other'))
  a.stop('other');self.assertFalse(a.JOB['cancel'].is_set())
  a.stop('owner','wrong');self.assertFalse(a.JOB['cancel'].is_set())
  with patch.object(a,'radio_idle',return_value=True),self.assertRaises(ValueError):a.start('owner','output')
  a.stop('owner','test');self.assertTrue(a.JOB['cancel'].is_set())
 def test_missing_and_muted_device(self):
  for items in ('[]','[{"name":"source","mute":true}]'):
   with patch.object(a,'pactl',side_effect=['source',items]),self.assertRaises(ValueError):a.device('source')
 def test_cancelled_before_capture(self):
  job=self.job();job['cancel'].set()
  with patch.object(a,'device',return_value=('source','Mic')),patch.object(a.subprocess,'Popen') as popen:a.worker(job)
  popen.assert_not_called();self.assertFalse(job['active'])
 def run_worker(self,radio=True,route='source',mode='microphone'):
  job=self.job(mode);proc=Mock();proc.poll.return_value=None;proc.stdout=io.BytesIO(b'\0\x20'*100000)
  clock=iter(i*.1 for i in range(1000))
  with patch.object(a,'device',return_value=('source','Mic')),patch.object(a,'radio_idle',side_effect=radio if isinstance(radio,list) else None,return_value=radio),patch.object(a,'pactl',return_value=route),patch.object(a.subprocess,'Popen',return_value=proc),patch.object(a.time,'monotonic',side_effect=lambda:next(clock)),patch.object(a.select,'select',return_value=([proc.stdout],[],[])):
   a.worker(job)
  self.assertFalse(job['active']);proc.terminate.assert_called_once();proc.wait.assert_called()
  return job
 def test_radio_interrupts_capture(self):self.assertIn('radio activity',self.run_worker(radio=[True,False])['message'])
 def test_route_change_stops_capture(self):self.assertIn('routing changed',self.run_worker(route='different')['message'])
 def test_microphone_finishes_and_detects_signal(self):self.assertIn('signal detected',self.run_worker()['message'])
 def test_no_data_timeout(self):
  with patch.object(a.select,'select',return_value=([],[],[])):
   # Separate context because run_worker supplies a readable stream.
   job=self.job();proc=Mock();proc.poll.return_value=None;proc.stdout=io.BytesIO()
   clock=iter(i*.5 for i in range(30))
   with patch.object(a,'device',return_value=('source','Mic')),patch.object(a,'radio_idle',return_value=True),patch.object(a,'pactl',return_value='source'),patch.object(a.subprocess,'Popen',return_value=proc),patch.object(a.time,'monotonic',side_effect=lambda:next(clock)):a.worker(job)
   self.assertIn('unavailable',job['message']);proc.terminate.assert_called_once()

if __name__=='__main__':unittest.main()
