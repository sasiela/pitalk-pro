#!/bin/bash
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
build=/var/tmp/pitalk-image-alpha
image="$build/PiTalk-Pro-alpha-1.img"
# Only create a regular file; never write to the source SD card device.
test ! -e "$image"
python3 - "$build/audit.json" <<'PY'
import sys,json
v=json.load(open(sys.argv[1]));assert not v['private_data_matches'];assert all(x for k,x in v.items() if k not in ('files_scanned','private_data_matches'))
PY
signature=$(openssl rand -hex 4)
python3 - "$build" "$signature" <<'PY'
import pathlib,re,sys
b=pathlib.Path(sys.argv[1]);id=sys.argv[2]
p=b/'root/etc/fstab';s=p.read_text();s=re.sub(r'PARTUUID=[0-9a-fA-F]+-01','PARTUUID='+id+'-01',s);s=re.sub(r'PARTUUID=[0-9a-fA-F]+-02','PARTUUID='+id+'-02',s);p.write_text(s)
p=b/'boot/cmdline.txt';s=p.read_text();s=re.sub(r'root=PARTUUID=\S+','root=PARTUUID='+id+'-02',s);p.write_text(s)
PY
truncate -s 6G "$image"
sfdisk "$image" <<EOF
label: dos
label-id: 0x$signature
unit: sectors

start=8192, size=1048576, type=c, bootable
start=1056768, type=83
EOF
loop=$(losetup --find --show --partscan "$image")
mountpoint="$build/boot-mount"
cleanup() { mountpoint -q "$mountpoint" && umount "$mountpoint" || true; losetup -d "$loop"; }
trap cleanup EXIT
for i in {1..30}; do [ -b "${loop}p2" ] && break; sleep 1; done
mkfs.vfat -F 32 -n bootfs "${loop}p1"
mkfs.ext4 -F -m 1 -L rootfs -d "$build/root" "${loop}p2"
mkdir -p "$mountpoint"
mount "${loop}p1" "$mountpoint"
cp -a "$build/boot/." "$mountpoint/"
sync
umount "$mountpoint"
e2fsck -fn "${loop}p2" >"$build/ext4-check.txt" 2>&1
fsck.vfat -n "${loop}p1" >"$build/fat-check.txt" 2>&1
sfdisk --dump "$image" >"$build/partition-table.txt"
lsblk -o NAME,SIZE,FSTYPE,LABEL,PARTUUID "$loop" >"$build/image-layout.txt"
losetup -d "$loop"
trap - EXIT
printf 'IMAGE_FILESYSTEM_CHECKS_PASSED\n'
gzip -1 -c "$image" >"$image.gz"
gzip -t "$image.gz"
cd "$build"
sha256sum PiTalk-Pro-alpha-1.img.gz >SHA256SUMS
printf 'COMPRESSED_IMAGE_READY\n'
ls -lh PiTalk-Pro-alpha-1.img.gz
