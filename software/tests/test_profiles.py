import copy,importlib.util,json,pathlib,tempfile,unittest
from unittest.mock import patch
MODULE=pathlib.Path(__file__).resolve().parents[1]/'rootfs/usr/local/sbin/sqlink_profiles.py'
spec=importlib.util.spec_from_file_location('profiles',MODULE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
RAW=b'''[SimplexLogic]\nCALLSIGN=TEST\nRX=Rx1\n[ReflectorLogic]\nTYPE=Reflector\nHOSTS=example.org\nHOST_PORT=5300\nCALLSIGN=TEST\nAUTH_KEY="test-secret"\nDEFAULT_TG=260\nMONITOR_TGS=260,999\nTG_SELECT_TIMEOUT=30\n[Rx1]\nAUDIO_DEV=alsa:pipewire\n'''
class Profiles(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();root=pathlib.Path(self.tmp.name);self.patches=[]
  for key,sub in [('BASE','private'),('PUBLIC','public/active.json'),('CONFIG','config'),('BACKUPS','backups'),('PTT','ptt'),('RADIO','radio'),('PID','pid'),('LOG','log')]:
   p=patch.object(m,key,root/sub);p.start();self.patches.append(p)
  m.CONFIG.write_bytes(RAW);m.LOG.write_text('');m.PTT.write_text('1');m.PID.write_text('42');m.RADIO.write_text('42 0 0')
  self.db=self.call('profiles_snapshot')
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.tmp.cleanup()
 def call(self,action,**kw):return m.dispatch(dict(action=action,revision=getattr(self,'db',{}).get('revision'),confirm=True,**kw))
 def fala(self):return copy.deepcopy(next(p for p in self.db['profiles'] if p['id']=='fala'))
 def ready_fala(self):
  p=self.fala();p.update(port='5300',login='FALATEST',password='different-secret');self.db=self.call('profiles_save',id='fala',settings=p);self.assertTrue(self.db['ok'])
 def test_migration_private_and_no_cross_credentials(self):
  self.assertNotIn('test-secret',json.dumps(self.db));self.assertFalse(self.fala()['password_set']);self.assertEqual(self.db['active'],'sqlink')
  self.assertEqual((m.BASE/'profiles.json').stat().st_mode&0o777,0o600);self.assertEqual(m.BASE.stat().st_mode&0o777,0o700)
  self.assertNotIn('password',m.PUBLIC.read_text())
 def test_incomplete_saved_not_activated(self):
  self.db=self.call('profiles_save',id='fala',settings=self.fala());self.assertTrue(self.db['ok'])
  self.assertFalse(self.call('profiles_activate',id='fala')['ok']);self.assertEqual(m.CONFIG.read_bytes(),RAW)
 def test_invalid_and_duplicate(self):
  for change in [{'host':'https://example.org'},{'host':'x\nAUTH_KEY=bad'},{'port':'65536'},{'monitored':'4294967296'},{'password':'bad\nvalue'},{'directory':'evil'},{'name':'SQLink'}]:
   p=self.fala();p.update(change);self.assertFalse(self.call('profiles_save',id='fala',settings=p)['ok'])
 def test_stale_revision(self):
  stale=self.db;p=self.fala();p['name']='Fala updated';self.db=self.call('profiles_save',id='fala',settings=p)
  r=m.dispatch(dict(action='profiles_delete',id='fala',confirm=True,revision=stale['revision']));self.assertFalse(r['ok'])
 def test_active_and_default_protected(self):
  self.assertFalse(self.call('profiles_delete',id='sqlink')['ok']);self.assertFalse(self.call('profiles_default',id='fala')['ok'])
 def test_ptt_and_rx_guard(self):
  self.ready_fala()
  for ptt,radio in [('0','42 0 0'),('1','42 260 1'),('1','43 0 0')]:
   m.PTT.write_text(ptt);m.RADIO.write_text(radio);self.assertFalse(self.call('profiles_activate',id='fala')['ok'])
  self.assertEqual(m.CONFIG.read_bytes(),RAW)
 def test_activation_and_scoped_credentials(self):
  self.ready_fala()
  with patch.object(m,'restart') as restart,patch.object(m,'authenticated',return_value=True):self.db=self.call('profiles_activate',id='fala')
  self.assertTrue(self.db['ok']);self.assertEqual(self.db['active'],'fala');restart.assert_called_once()
  c=m.parse(m.CONFIG.read_bytes());self.assertEqual(c['ReflectorLogic']['auth_key'],'"different-secret"');self.assertEqual(c['Rx1']['audio_dev'],'alsa:pipewire');self.assertEqual(json.loads(m.PUBLIC.read_text())['directory'],'none')
  self.assertNotIn('different-secret',json.dumps(self.db))
 def test_failed_activation_rolls_back(self):
  self.ready_fala();before=(m.BASE/'profiles.json').read_bytes()
  with patch.object(m,'restart') as restart,patch.object(m,'authenticated',return_value=False):r=self.call('profiles_activate',id='fala')
  self.assertFalse(r['ok']);self.assertEqual(m.CONFIG.read_bytes(),RAW);self.assertEqual((m.BASE/'profiles.json').read_bytes(),before);self.assertEqual(restart.call_count,2);self.assertFalse((m.BASE/'pending.json').exists())
 def test_default_does_not_switch_until_boot(self):
  self.ready_fala();self.db=self.call('profiles_default',id='fala');self.assertEqual(self.db['active'],'sqlink');self.assertEqual(m.CONFIG.read_bytes(),RAW)
  with m.locked() as db,patch.object(m,'restart') as restart:m.activate(db,next(p for p in db['profiles'] if p['id']=='fala'),boot=True)
  restart.assert_not_called();self.assertIn(b'fala.zasieg.pl',m.CONFIG.read_bytes())
 def test_blank_password_preserved(self):
  p=self.db['profiles'][0];p=dict(p,password='');self.db=self.call('profiles_save',id='sqlink',settings=p)
  private=json.loads((m.BASE/'profiles.json').read_text());self.assertEqual(private['profiles'][0]['password'],'test-secret')
 def test_create_delete(self):
  p=self.fala();p['name']='Another';p.pop('id');self.db=self.call('profiles_save',settings=p);new=self.db['profiles'][-1]['id'];self.db=self.call('profiles_delete',id=new);self.assertEqual(len(self.db['profiles']),2)
 def test_render_inserts_port_keeps_comments(self):
  p=self.fala();p.update(port='5300',login='T',password='x');raw=RAW.replace(b'HOST_PORT=5300\n',b'# preserved\n');result=m.render_config(raw,p);self.assertIn(b'HOST_PORT=5300',result);self.assertIn(b'# preserved',result)
if __name__=='__main__':unittest.main()
