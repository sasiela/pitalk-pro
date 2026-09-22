import importlib,sys,types,pathlib,unittest,tempfile
from unittest.mock import patch
from PIL import ImageFont
root=pathlib.Path(__file__).resolve().parents[1];pkg=types.ModuleType('sqlink');pkg.__path__=[str(root/'rootfs/usr/lib/sqlink')];sys.modules['sqlink']=pkg
from sqlink import user_ui,api,profile_state
font=ImageFont.truetype
class UI(unittest.TestCase):
 def setUp(self):
  self.patch=patch.object(ImageFont,'truetype',side_effect=lambda path,size,*a,**kw:font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf' if pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf').exists() else '/System/Library/Fonts/Supplemental/Arial.ttf',size));self.patch.start()
  self.u=user_ui.UserMenu();self.u.data=dict(active='sqlink',default='sqlink',active_name='SQLink',revision='test',profiles=[dict(id='sqlink',name='SQLink',host='example.org',port='5300',login='TEST',password_set=True,ready=True,default_tg='260',monitored='260,999',timeout='30',directory='sqlink'),dict(id='fala',name='Fala',host='fala.zasieg.pl',port='',login='',password_set=False,ready=False,default_tg='0',monitored='',timeout='30',directory='none')])
 def tearDown(self):self.patch.stop()
 def test_render_and_keyboard(self):
  for page in ('list','detail','form','keyboard','confirm','error'):
   self.u.page=page;self.u.profile_id='fala';self.u.draft=self.u.data['profiles'][1].copy();self.u.edit_key='host';self.u.buffer='fala.zasieg.pl';self.u.confirm_label='Activate and reconnect?';self.u.message='Server port is required.'
   img=self.u.render();self.assertEqual(img.size,(240,320))
 def test_navigation_and_discard(self):
  self.u.button('DOWN');self.u.button('ENTER');self.assertEqual(self.u.profile_id,'fala');self.u.button('ENTER');self.assertEqual(self.u.page,'form')
  self.u.button('DOWN');self.u.button('ENTER');self.assertEqual(self.u.page,'keyboard');self.u.button('BACK');self.assertEqual(self.u.page,'form')
  self.u.dirty=True;self.u.button('BACK');self.assertEqual(self.u.page,'confirm');self.u.button('DOWN');self.u.button('ENTER');self.assertEqual(self.u.page,'list')
 def test_fala_never_fetches_sqlink(self):
  with patch.object(profile_state,'current',return_value=dict(id='fala',directory='none',default_tg='9',monitored='10')),patch.object(api,'_get_json',side_effect=AssertionError('Network leak')):
   self.assertEqual(api.get_status()['statusNodes'],{});self.assertEqual(api.get_talkgroups(),[{'id':9,'name':'TG 9'},{'id':10,'name':'TG 10'}])
if __name__=='__main__':unittest.main()
