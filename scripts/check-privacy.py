#!/usr/bin/env python3
from pathlib import Path
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    b"ufi_tools_report",
    b"api.kanokano.cn",
    b"UniqueDeviceIDManager",
    b"getRemoteDeviceRegisterItem",
    b"runnableRPT",
    b"initMessage",
)
failures = []


def check(name, data):
    for marker in FORBIDDEN:
        if marker in data:
            failures.append(f"{name}: {marker.decode()}")


for directory in ("app/src/main/java", "app/frontEnd/public"):
    for path in (ROOT / directory).rglob("*"):
        if path.suffix in (".kt", ".js", ".html"):
            check(path.relative_to(ROOT), path.read_bytes())

for apk in sys.argv[1:]:
    with ZipFile(apk) as archive:
        required = {"assets/index.html", "assets/script/main.js", "assets/script/requests.js"}
        missing = required.difference(archive.namelist())
        failures.extend(f"{apk}: missing {name}" for name in sorted(missing))
        for name in archive.namelist():
            if name.endswith((".dex", ".js", ".html")):
                check(name, archive.read(name))

if failures:
    sys.exit("Privacy check failed:\n" + "\n".join(failures))
print("Privacy check passed")
