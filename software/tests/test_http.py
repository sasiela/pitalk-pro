import http.client,json,pathlib,sys,threading,time,types,unittest
sys.dont_write_bytecode = True
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'rootfs/opt/sqlink-web'))
sys.modules['sqlink']=types.SimpleNamespace(reflector=types.SimpleNamespace(),api=types.SimpleNamespace(get_talkgroups=lambda:[]),gpio=types.SimpleNamespace(),profile_state=types.SimpleNamespace(current=lambda:{},key=lambda:"test"))
import server
class H(server.Handler):
 def local_access(self):return True
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=server.ThreadingHTTPServer(('127.0.0.1',0),H)
  threading.Thread(target=cls.server.serve_forever,daemon=True).start()
  server.SESSIONS['test']=dict(csrf='csrf',expires=time.time()+100)
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
 def call(self,method='GET',auth=True,csrf=True,body=None,path='/api/audio-test'):
  c=http.client.HTTPConnection('127.0.0.1',self.server.server_port);h={}
  if auth:h['Cookie']='session=test'
  if csrf:h['X-CSRF-Token']='csrf'
  if body is not None:h['Content-Type']='application/json'
  c.request(method,path,json.dumps(body) if body is not None else None,h);r=c.getresponse();status=r.status;obj=json.loads(r.read());c.close();return status,obj
 def test_unauthenticated(self):self.assertEqual(self.call(auth=False)[0],401)
 def test_csrf(self):self.assertEqual(self.call('POST',csrf=False,body={'action':'start','mode':'output'})[0],403)
 def test_status(self):self.assertEqual(self.call()[0],200)
 def test_bad_action(self):self.assertEqual(self.call('POST',body={'action':'bad'})[0],400)
 def test_start_stop(self):
  with patch.object(server.audio_test,'start',return_value={'active':True}) as start:
   self.assertEqual(self.call('POST',body={'action':'start','mode':'microphone'})[0],200);start.assert_called_once_with('test','microphone')
  with patch.object(server.audio_test,'stop') as stop:
   self.assertEqual(self.call('POST',body={'action':'stop','id':'job'})[0],200);stop.assert_called_once_with('test','job')
 def test_update_auth_and_confirmation(self):
  with patch.object(server,'bridge') as bridge:
   self.assertEqual(self.call(auth=False,path='/api/update')[0],401)
   self.assertEqual(self.call('POST',csrf=False,body={'action':'install','confirm':True},path='/api/update')[0],403)
   for body in ({'action':'install'},{'action':'install','confirm':'true'},{'action':'arbitrary'}):
    self.assertEqual(self.call('POST',body=body,path='/api/update')[0],400)
   bridge.assert_not_called()
 def test_update_status_and_commands(self):
  with patch.object(server,'bridge',return_value={'ok':True,'busy':False,'installed':'pitalk-v0.1.2'}) as bridge:
   self.assertEqual(self.call(path='/api/update')[0],200)
   bridge.assert_called_with('update',{'action':'status'})
   for action in ('check','install'):
    self.assertEqual(self.call('POST',body={'action':action,'confirm':True,'url':'untrusted'},path='/api/update')[0],200)
    bridge.assert_called_with('update',{'action':action,'confirm':True})
 def test_update_helper_unavailable(self):
  with patch.object(server,'bridge',side_effect=OSError('socket missing')):
   self.assertEqual(self.call(path='/api/update')[0],503)
if __name__=='__main__':unittest.main()
