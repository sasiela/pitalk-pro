import importlib.util,tempfile,unittest,json,hashlib
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('updater',Path(__file__).resolve().parents[1]/'rootfs/usr/local/sbin/pitalk-update.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
class Tests(unittest.TestCase):
 def test_manifest_rejects_path_and_tag(self):
  with self.assertRaises(ValueError):u.manifest('../main')
  m={'format':1,'tag':'pitalk-v0.1.0','files':{'etc/shadow':'0'*64}}
  with patch.object(u,'download',return_value=json.dumps(m).encode()):
   with self.assertRaises(ValueError):u.manifest(m['tag'])
 def test_manifest_valid(self):
  m={'format':1,'tag':'pitalk-v0.1.0','files':{n:'0'*64 for n in u.ALLOWED}}
  with patch.object(u,'download',return_value=json.dumps(m).encode()):self.assertEqual(u.manifest(m['tag']),m)
 def test_legacy_manifest_still_supported(self):
  m={'format':1,'tag':'pitalk-v0.1.2','files':{n:'0'*64 for n in u.LEGACY}}
  with patch.object(u,'download',return_value=json.dumps(m).encode()):self.assertEqual(u.manifest(m['tag']),m)
 def test_partial_web_manifest_rejected(self):
  m={'format':1,'tag':'pitalk-v0.1.3','files':{n:'0'*64 for n in u.LEGACY|{'opt/sqlink-web/server.py'}}}
  with patch.object(u,'download',return_value=json.dumps(m).encode()):
   with self.assertRaises(ValueError):u.manifest(m['tag'])
 def test_atomic(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'file';p.write_bytes(b'old');u.atomic(p,b'new',0o640)
   self.assertEqual(p.read_bytes(),b'new');self.assertEqual(p.stat().st_mode&0o777,0o640)
 def transaction(self,fail):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'state';root.mkdir();dest=Path(d)/'app';dest.write_bytes(b'old')
   # Absolute temporary path keeps tests isolated from the live filesystem.
   name=str(dest);allow={name}
   with patch.object(u,'ROOT',root),patch.object(u,'ALLOWED',allow),patch.object(u,'guard'),patch.object(u,'restart'),patch.object(u,'healthy',side_effect=[False,True] if fail else [True]):
    u.save('installed.json',{'tag':'old'})
    # Backup path must be relative in production; remap only this test path.
    orig_atomic=u.atomic
    def atomic(p,data,mode=0o644):orig_atomic(p,data,mode)
    # Replace Path('/') resolution by relative allowed name using a temporary root wrapper.
    realPath=Path
    relative='app'
    u.ALLOWED={relative}
    def paths(value):return Path(d) if value=='/' else realPath(value)
    with patch.object(u,'Path',side_effect=paths):
     if fail:
      with self.assertRaises(RuntimeError):u.apply({'tag':'new'},{relative:b'new'})
     else:u.apply({'tag':'new'},{relative:b'new'})
    self.assertEqual(dest.read_bytes(),b'old' if fail else b'new')
    self.assertEqual(u.read('installed.json')['tag'],'old' if fail else 'new')
    self.assertFalse((root/'pending.json').exists())
 def test_install(self):self.transaction(False)
 def test_rollback(self):self.transaction(True)
if __name__=='__main__':unittest.main()
