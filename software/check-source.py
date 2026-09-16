"""Static checks only: no imports of hardware modules and no deployment."""
from pathlib import Path
import re,json,hashlib
base=Path(__file__).resolve().parent
count=0
for p in base.rglob('*.py'):
    compile(p.read_bytes(),str(p),'exec');count+=1
for p in (base/'rootfs').rglob('*'):
    if not p.is_file():continue
    text=p.read_text()
    if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text):raise SystemExit(f'Private key found: {p}')
    if re.search(r'^\s*(?:AUTH_KEY|PSK)\s*=\s*["\']?[^\s"\']',text,re.M):raise SystemExit(f'Credential-like assignment: {p}')
manifest=json.loads((base/'manifest.json').read_text())
for name,entry in manifest['files'].items():
    p=base/'rootfs'/name
    if hashlib.sha256(p.read_bytes()).hexdigest()!=entry['export_sha256']:
        print(f'Changed since export: {name}')
print(f'PASS: {count} Python files compile; source secret-pattern checks passed. No hardware test.')
