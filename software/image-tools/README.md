# Experimental alpha image tooling

Read `../../docs/handoff/IMAGE-AND-BACKUPS.md` and `IMAGE-INSTALL-PL.md`.

These scripts document a staged Linux image-building process; they are not a portable one-command build. `sanitize.py` assumes `/var/tmp/pitalk-image-alpha/root`, `boot`, and `payload` already exist. Owner-specific strings are now placeholders. `build-image.sh` also requires a separately generated successful privacy audit. Do not execute either against your development computer or production filesystem.

`firstboot.py` belongs inside a new image. Do not execute it on your existing installation. `test-firstboot.py` is a simulated test with temporary files and mocked system actions; run with Python 3. No hardware boot test was performed.

The example hostname is `pitalk-pro`. The .img.gz itself is intentionally outside Git; see the owner's ignored LOCAL-ACCESS.md for its location. SHA256SUMS identifies that local artifact after the hostname update.
