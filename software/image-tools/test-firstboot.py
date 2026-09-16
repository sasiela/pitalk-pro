import importlib.util,json,pathlib,tempfile,types,os
spec=importlib.util.spec_from_file_location('provision',str(pathlib.Path(__file__).with_name('firstboot.py')));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=pathlib.Path
with tempfile.TemporaryDirectory() as temp:
 root=P(temp)
 def mapped(value):
  value=str(value)
  if value.startswith(temp):return P(value)
  return root/value.lstrip('/')
 m.pathlib=types.SimpleNamespace(Path=mapped)
 m.BOOT=root/'boot/firmware';m.BOOT.mkdir(parents=True);m.STATE=root/'var/lib/pitalk'
 for d in ('etc/svxlink','etc/ssh','etc/modprobe.d','etc/NetworkManager/system-connections'):(root/d).mkdir(parents=True)
 (root/'etc/machine-id').write_text('1'*32);(root/'etc/svxlink/svxlink.conf').write_text('[SimplexLogic]\nCALLSIGN=NOCALL\n[ReflectorLogic]\nCALLSIGN=NOCALL\nAUTH_KEY=\nHOSTS=sqlink.pl\nDEFAULT_TG=0\nMONITOR_TGS=\nTG_SELECT_TIMEOUT=30\n')
 (m.BOOT/'cmdline.txt').write_text('root=PARTUUID=12345678-02 rootwait\n')
 c=json.load(open(pathlib.Path(__file__).with_name('pitalk-setup.json')));c.update(system_password='synthetic-test-password',callsign='TEST1',reflector_password='synthetic-radio-password',wifi_ssid='TEST-NET',wifi_password='synthetic-wifi-password')
 (m.BOOT/'pitalk-setup.json').write_text(json.dumps(c));calls=[]
 def fake_run(args,**kw):
  calls.append(args[0])
  if args[0]=='openssl':
   mapped(args[args.index('-keyout')+1]).write_text('test key');mapped(args[args.index('-out')+1]).write_text('test cert')
  return types.SimpleNamespace(returncode=0)
 m.run=fake_run;m.subprocess=types.SimpleNamespace(run=fake_run,DEVNULL=-3);m.expand=lambda:None
 m.os=types.SimpleNamespace(chown=lambda *a:None,chmod=os.chmod,fsync=os.fsync,sync=lambda:None)
 m.main()
 assert (m.STATE/'initialized').exists() and not (m.BOOT/'pitalk-setup.json').exists()
 cfg=(root/'etc/svxlink/svxlink.conf').read_text();assert 'CALLSIGN=TEST1' in cfg and 'AUTH_KEY="synthetic-radio-password"' in cfg
 net=root/'etc/NetworkManager/system-connections/pitalk.nmconnection';assert net.stat().st_mode&0o777==0o600
 assert 'synthetic' not in (m.BOOT/'PITALK-STATUS.txt').read_text()
 n=len(calls);m.main();assert calls[n:]==['ssh-keygen']
 print('PASS: simulated provisioning, radio configuration, protected Wi-Fi file, secret-file removal, idempotent reboot')
