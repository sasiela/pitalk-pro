"""Credential-free metadata for the actually applied reflector profile."""
import json,pathlib
PATH=pathlib.Path('/var/lib/sqlink-profile-state/active.json')
def current():
 try:return json.loads(PATH.read_text())
 except (OSError,ValueError):return dict(id='unknown',name='Unknown',host='',directory='none',default_tg='0',monitored='')
def key():return json.dumps(current(),sort_keys=True)
def local_groups():
 p=current();ids=set()
 for s in (str(p.get('default_tg','0'))+','+str(p.get('monitored',''))).split(','):
  try:
   n=int(s.strip().rstrip('+'))
   if n>0:ids.add(n)
  except ValueError:pass
 return [dict(id=n,name='TG '+str(n)) for n in sorted(ids)]
