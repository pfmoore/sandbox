from locators import parse_filename
import json
from urllib.parse import urlparse
import posixpath
from collections import defaultdict

with open('links.json') as f:
    # [(source, text, href), ...]
    links = json.load(f)

files = defaultdict(list)

for source, text, href in links:
    try:
        a = urlparse(href)
    except ValueError:
        files['corrupt'].append((source, text, href))
        continue
    base = posixpath.basename(a.path)
    filetype, name, version = parse_filename(base)
    if filetype is None:
        filetype = 'unknown'
    files[filetype].append((base, name, version))

for filetype in sorted(files):
    print(filetype, len(files[filetype]))

for source, text, href in files['corrupt']:
    print(source, text, href)
