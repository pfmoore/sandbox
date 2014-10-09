import xmlrpc.client as xmlrpclib
from urllib.request import urlopen
import json
import io

def get_json(name):
    with urlopen('https://pypi.python.org/pypi/{}/json'.format(name)) as f:
        ff = io.TextIOWrapper(f)
        data = json.load(ff)
    return sorted(data['releases'].keys())

def get_xml(name):
    proxy = xmlrpclib.ServerProxy( 'https://pypi.python.org/pypi')
    xv = proxy.package_releases(name)
    xvh = proxy.package_releases(name, True)
    return sorted(xv), sorted(xvh)

if __name__ == '__main__':
    import sys
    name = sys.argv[1]
    jv = get_json(name)
    xv, xvh = get_xml(name)
    print("XML = JSON" if jv == xvh else "XML != JSON")
    print("XML               for", name, ', '.join(xv))
    print("JSON              for", name, ', '.join(jv))
    print("XML (with hidden) for", name, ', '.join(xvh))
