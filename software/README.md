# PiTalk Pro software snapshot

Start with [the project handoff](../docs/handoff/START-HERE.md) and [AGENTS.md](../AGENTS.md).

`rootfs/` mirrors installation paths for the current Python application, web assets, systemd units and supporting scripts. It is an exported source snapshot, not a complete Raspberry Pi filesystem or automatic installer. Owner identifiers were scrubbed; the web LAN filter contains example addresses and requires adjustment before deployment. `manifest.json` records source/export hashes and original permissions.

`examples/` contains credential-free configuration examples. Never overwrite an active configuration with these templates. `image-tools/` contains experimental alpha image tooling and its limitations. Read its README before use.

Run `python3 software/check-source.py` from the repository root for static checks. These do not test actual hardware. The repository does not establish a new license for bundled upstream service files; preserve their existing notices and review licensing before distribution.
