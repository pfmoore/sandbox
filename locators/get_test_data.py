from random import choice
from urllib.parse import urlparse
from xmlrpc.client import ServerProxy
PYPI_XMLRPC_URL = 'https://pypi.python.org/pypi'

pypi = ServerProxy(PYPI_XMLRPC_URL)
dists = pypi.list_packages()

testcases = []
while len(testcases) < 200:
    dist = choice(dists)
    versions = pypi.package_releases(dist, True)
    if len(versions) == 0:
        continue
    ver = choice(versions)
    urls = pypi.release_urls(dist, ver)
    urls = [u['url'] for u in urls if 'url' in u]
    if len(urls) == 0:
        continue
    testcases.append((dist, ver, choice(urls)))
    print('+' if len(testcases) % 10 == 0 else '.', end='', flush=True)

print("\nOK")

with open('testdata.txt', 'w') as f:
    for dist, ver, url in testcases:
        filename = urlparse(url).path.split('/')[-1]
        print("{}\t{}\t{}".format(dist, ver, filename), file=f)
