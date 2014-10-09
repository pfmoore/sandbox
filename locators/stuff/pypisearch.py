import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, 'lib'))

from packaging.version import Version, Specifier
import re
from locators import SimpleLocator

REQ_RE = re.compile(r'([a-zA-Z0-9]([-a-zA-Z0-9_.]*[a-zA-Z0-9])?)\s*(.*)', re.I)

req = sys.argv[1]
m = REQ_RE.match(req)

if not m:
    raise ValueError("Invalid requirement: " + sys.argv[1])

name = m.group(1).lower().replace('-', '_')
spec = Specifier(m.group(3))

print("name is", name)
print("spec is", spec)

loc = SimpleLocator()

versions = [Version(v) for v in loc.versions(name)]

for v in sorted(versions):
    if spec.contains(v):
        print(name, v)
