#!/bin/bash
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
b=/var/tmp/pitalk-image-alpha
loop=$(losetup --read-only --find --show --partscan "$b/PiTalk-Pro-alpha-1.img")
mkdir -p "$b/verify-root" "$b/verify-boot"
cleanup() { mountpoint -q "$b/verify-root" && umount "$b/verify-root" || true; mountpoint -q "$b/verify-boot" && umount "$b/verify-boot" || true; losetup -d "$loop"; }
trap cleanup EXIT
mount -o ro,noload "${loop}p2" "$b/verify-root"
mount -o ro "${loop}p1" "$b/verify-boot"
python3 - "$b" "${loop}p2" <<'PY'
import pathlib,sys,subprocess,json,stat
b=pathlib.Path(sys.argv[1]);r=b/'verify-root';boot=b/'verify-boot'
part=subprocess.check_output(['blkid','-s','PARTUUID','-o','value',sys.argv[2]],text=True).strip()
assert 'root=PARTUUID='+part in (boot/'cmdline.txt').read_text()
assert 'PARTUUID='+part in (r/'etc/fstab').read_text()
for name in ['start.elf','fixup.dat','kernel8.img','bcm2710-rpi-3-b.dtb','config.txt','pitalk-setup.json']:
 assert (boot/name).is_file(),name
assert (boot/'overlays/pitft22.dtbo').is_file()
assert not (r/'etc/machine-id').read_text().strip()
assert not list((r/'etc/NetworkManager/system-connections').glob('*'))
assert not list((r/'etc/ssh').glob('ssh_host_*key*'))
assert not (r/'etc/sqlink-web/key.pem').exists()
assert not (r/'var/swap').exists()
assert not (r/'home/OWNER_USER').exists()
accounts={line.split(':')[0]:line.split(':')[1] for line in (r/'etc/shadow').read_text().splitlines()}
assert accounts['root']=='!' and accounts['sqlink']=='!'
assert not json.loads((boot/'pitalk-setup.json').read_text())['system_password']
assert (r/'etc/systemd/system/multi-user.target.wants/pitalk-firstboot.service').is_symlink()
assert (r/'usr/local/sbin/pitalk-firstboot.py').stat().st_mode & stat.S_IXUSR
assert (r/'home/sqlink').stat().st_uid==1002
for p in ['usr/local/bin/sqlink-screen.py','opt/sqlink-web/server.py','usr/local/sbin/pitalk-firstboot.py']:
 compile((r/p).read_text(),p,'exec')
print('PASS: read-only image inspection; boot files, PARTUUID references, provisioning, account locks, identity removal and Python syntax.')
print('No physical boot test performed.')
PY
