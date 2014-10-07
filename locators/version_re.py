import re
import json
from posixpath import basename, dirname
from collections import defaultdict
from urllib.parse import urlparse

VERSION_RE = re.compile(r'''
    \s*
    v?
    # Epoch segment
    (\d+!)?
    # Release segment
    \d+(\.\d+)*
    # Pre-release segment
    ([-._]?(a|alpha|b|beta|c|rc|pre|preview)([-._]?\d+)?)?
    # Post-release segment
    ([-._]?(post|rev|r)([-._]?\d+)?)?
    # Development release segment
    ([-._]?dev([-._]?\d+)?)?
    # Local version label
    (\+[a-zA-Z0-9]+([-._][a-zA-Z0-9]+)*)?
    \s*
    (\.tar\.gz|\.tar\.bz2|\.tar|\.tgz|\.zip)$

''', re.VERBOSE | re.IGNORECASE)

extensions = (
    '.tar.gz', '.tar.bz2', '.tar', '.tgz', '.zip',
#    '.egg',
#    '.whl',
#    '.exe',
)

with open('links.json') as f:
    # [(source, text, href), ...]
    links = json.load(f)

total = 0
errors = 0
for source, text, href in links:
    try:
        a = urlparse(href)
    except ValueError:
        # files['corrupt'].append((source, text, href))
        continue
    if not a.path.endswith(extensions):
        continue
    proj = basename(dirname(a.path))
    norm_proj = proj.lower().replace('-', '_')
    base = basename(a.path)
    norm_base = base.lower().replace('-', '_')
    if not norm_base.startswith(norm_proj):
        # pip won't recognise sdists that don't start with the project name
        continue
    total += 1
    m = VERSION_RE.match(base, len(proj)+1)
    if not m:
        errors += 1
        print('NO MATCH:', proj, source, base)
        continue

print("total =", total, "errors =", errors)
