PiTalk Pro alpha-1 — TEST IMAGE, 2026-09-16

Hardware target: Raspberry Pi 3 Model B Rev 1.2, PiTFT 2.2-inch
240x320 SPI display (pitft22), buttons GPIO17/22/23/27,
PTT input GPIO26, USB audio card. Other boards/screens are untested.
Use a spare microSD of at least 8 GB.

1. Raspberry Pi Imager: Use Custom -> PiTalk-Pro-alpha-1.img.gz.
2. Skip Imager OS customization for this test image.
3. After writing, reinsert the card and open the visible bootfs partition.
4. Edit pitalk-setup.json with a plain-text editor, keeping valid JSON.
   Required: system_password, 12-128 characters (no colon).
   Login is sqlink. There is NO shared/default password.
   Empty hostname generates a unique pitalk-xxxxxx hostname.
   Set wifi_country for your country. Wi-Fi is optional if using Ethernet.
   For Wi-Fi fill wifi_ssid and wifi_password (WPA personal only).
   Reflector fields may remain empty. Configure them later in Menu -> User.
   For automatic reflector login supply BOTH callsign and reflector_password.
   These are your own reflector credentials, not the system password.
5. Eject the card safely, insert it in the target Raspberry Pi, and power on.
6. The first boot creates SSH host keys and a unique HTTPS certificate,
   sets your system password, applies network settings, and attempts to
   expand the root partition to fill the card. Allow several minutes.
7. Read PITALK-STATUS.txt on bootfs if setup fails. Edit the JSON and reboot.
   A successful setup overwrites and removes the supplied JSON file.
8. Find the IP in Menu -> WiFi or in your router's DHCP list.
   Open https://DEVICE-IP:8443 or https://HOSTNAME.local:8443.
   The local self-signed certificate produces a browser warning; verify
   that the address belongs to your device. Login: sqlink.
   SSH is available for sqlink, with the system password; root login is off.
   sudo requires the same system password.

Current software: device menus, PTT, Wi-Fi, Bluetooth, display settings,
user settings, SvxLink reflector client, HTTPS web panel, browser live audio.
No original Wi-Fi profiles, Bluetooth pairings, reflector credentials,
SSH keys, password hashes, personal logs, backups, or temporary sudo access
are intentionally included. The live source device is not reset.

This is a local integration-test image, NOT a public release. It has not
been boot-tested from a physical card. Check first boot, credentials,
network, display/buttons, USB/Bluetooth audio, PTT, and web audio before
sharing. Public release also requires a source/license and dependency audit.
Do not enable RF transmission until you have checked the hardware wiring.
