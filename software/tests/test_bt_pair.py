import ast,json,pathlib,time,unittest
from unittest.mock import Mock
class PairTests(unittest.TestCase):
 def check_pair(self,transport,sink,source):
  path=pathlib.Path(__file__).resolve().parents[1]/'rootfs/usr/local/sbin/sqlink-bluetooth-helper.py'
  tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='select_transport')
  st=dict(sinks=[{'name':sink}],sources=[{'name':source}],sink='old-sink',source='old-source',cards=[])
  route=Mock();audio=Mock(side_effect=AssertionError('Unexpected profile change'))
  env=dict(json=json,time=time,idle_audio=lambda:None,audio_status=lambda:st,PREFERENCES={},set_route=route,save=lambda:None,audio=audio)
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'helper','exec'),env)
  env['select_transport'](transport)
  self.assertEqual([c.args for c in route.call_args_list],[('sink',sink,False),('source',source,False)])
  self.assertEqual(env['PREFERENCES']['source'],source)
 def test_colon_source(self):self.check_pair('bluetooth','bluez_output.AA_BB_CC_DD_EE_FF.1','bluez_input.AA:BB:CC:DD:EE:FF')
 def test_underscore_source(self):self.check_pair('bluetooth','bluez_output.AA_BB_CC_DD_EE_FF.1','bluez_input.AA_BB_CC_DD_EE_FF.0')
 def test_usb(self):self.check_pair('usb','alsa_output.usb-device.analog-stereo','alsa_input.usb-device.mono-fallback')
if __name__=='__main__':unittest.main()
