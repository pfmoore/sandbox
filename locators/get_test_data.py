from xmlrpc.client import ServerProxy
from urllib.request import urlopen
from urllib.error import HTTPError
import json
import io

def package_data_to_tests(data):
    name = data['info']['name']
    for ver, urls in data['releases'].items():
        for url in urls:
            filetype = url['packagetype']
            if filetype.startswith('bdist_'):
                filetype = filetype[6:]
            filename = url['filename']
            yield filename, filetype, name, ver

def get_package_data(dist):
    try:
        with urlopen('https://pypi.python.org/pypi/{}/json'.format(dist)) as f:
            ft = io.TextIOWrapper(f)
            return json.load(ft)
    except HTTPError:
        return None

def get_packages():
    pypi = ServerProxy('https://pypi.python.org/pypi')
    return pypi.list_packages()

def generate_data(filename, packages):
    with open(filename, 'w') as out:
        for i, pkg in enumerate(packages):
            print("\r{}/{}          ".format(i+1, len(packages)), end='', flush=True)
            data = get_package_data(pkg)
            if not data:
                print("\nNo data for", pkg)
                continue
            for filename, filetype, name, ver in package_data_to_tests(data):
                print(filename, filetype, name, ver, file=out, sep='\t')
    print("OK")

if __name__ == '__main__':
    import sys
    import random
    packages = random.sample(get_packages(), 100)
    generate_data(sys.argv[1], packages)
