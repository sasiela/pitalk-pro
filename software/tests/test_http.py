import http.client,json,pathlib,sys,threading,time,types,unittest
sys.dont_write_bytecode = True
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'rootfs/opt/sqlink-web'))
sys.modules['sqlink']=types.SimpleNamespace(reflector=types.SimpleNamespace(),api=types.SimpleNamespace(get_talkgroups=lambda:[]),gpio=types.SimpleNamespace())
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
 def call(self,method='GET',auth=True,csrf=True,body=None):
  c=http.client.HTTPConnection('127.0.0.1',self.server.server_port);h={}
  if auth:h['Cookie']='session=test'
  if csrf:h['X-CSRF-Token']='csrf'
  if body is not None:h['Content-Type']='application/json'
  c.request(method,'/api/audio-test',json.dumps(body) if body is not None else None,h);r=c.getresponse();status=r.status;obj=json.loads(r.read());c.close();return status,obj
 def test_unauthenticated(self):self.assertEqual(self.call(auth=False)[0],401)
 def test_csrf(self):self.assertEqual(self.call('POST',csrf=False,body={'action':'start','mode':'output'})[0],403)
 def test_status(self):self.assertEqual(self.call()[0],200)
 def test_bad_action(self):self.assertEqual(self.call('POST',body={'action':'bad'})[0],400)
 def test_start_stop(self):
  with patch.object(server.audio_test,'start',return_value={'active':True}) as start:
   self.assertEqual(self.call('POST',body={'action':'start','mode':'microphone'})[0],200);start.assert_called_once_with('test','microphone')
  with patch.object(server.audio_test,'stop') as stop:
   self.assertEqual(self.call('POST',body={'action':'stop','id':'job'})[0],200);stop.assert_called_once_with('test','job')
if __name__=='__main__':unittest.main()
