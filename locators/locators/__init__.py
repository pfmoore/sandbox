# -*- coding: utf-8 -*-

__author__ = 'Paul Moore'
__email__ = 'p.f.moore@gmail.com'
__version__ = '0.1.0'

try:
    from xmlrpclib import ServerProxy
except ImportError:
    from xmlrpc.client import ServerProxy

import re
from xml.etree import ElementTree
from urllib.parse import urlparse
from urllib.request import urlopen
import posixpath
from pathlib import Path
from collections import defaultdict
from wheel.install import WheelFile, BadWheelFile

try:
    import requests
except ImportError:
    requests = None

try:
    from cachecontrol import CacheControl
except ImportError:
    CacheControl = None

PYPI_XMLRPC_URL = 'https://pypi.python.org/pypi'
PYPI_JSON_URL = 'https://pypi.python.org/pypi' # /<dist>/json or /<dist>/<ver>/json
PYPI_SIMPLE_URL = 'https://pypi.python.org/simple/' # /<dist>

# Matches a PEP 440 version (taken from packaging/version.py)
VERSION_RE = re.compile(
    r"""
    \s*
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
    \s*
    """,
    re.VERBOSE | re.IGNORECASE,
)

session = None

def open_url(url):
    # if requests:
    #     global session
    #     if session is None:
    #         session = requests.session()
    #         if CacheControl:
    #             session = CacheControl(session)
    #     rsp = session.get(url, stream=True)
    #     return rsp.raw

    return urlopen(url)

def scrape_links(url):
    with open_url(url) as f:
        try:
            tree = ElementTree.parse(f)
        except ElementTree.ParseError:
            raise RuntimeError("Invalid content in "+url)
    return [a.attrib['href'] for a in tree.iter('a') if a.attrib.get('rel') == 'internal']

# Filename utilities
extensions = (
    ('sdist', ('.zip', '.tar.gz', '.tar.bz2', '.tgz', '.tar',)),
    ('egg', ('.egg',)),
    ('wheel', ('.whl',)),
    ('wininst', ('.exe',)),
)

def url_basename(url):
    u = urlparse(url)
    return posixpath.basename(u.path)

def parse_filename(filename, distname=None):
    print("Parsing", filename, distname)
    if distname is None:
        distname = filename.partition('-')[0]
    dist_norm = distname.lower().replace('-', '_')
    file_norm = filename.lower().replace('-', '_')

    # Check file is for this distribution
    if not file_norm.startswith(dist_norm):
        print("Wrong distribution")
        return None, None, None

    # Check it is a known file type
    for filetype, ext in extensions:
        if file_norm.endswith(ext):
            ftype = filetype
            break
    else:
        print("Unknown file type")
        return None, None, None

    if ftype == 'wheel':
        try:
            wf = WheelFile(filename)
        except BadWheelFile as e:
            print("Bad wheel file", e)
            return None, None, None
        return ftype, wf.parsed_filename.group('name'), wf.parsed_filename.group('ver')

    # Check the version is valid
    m = VERSION_RE.match(filename, len(distname)+1)
    if not m:
        print("Invalid version")
        return None, None, None

    print("OK:", ftype, m.group(0))
    return ftype, dist_norm, m.group(0)

class Locator:
    def distributions(self):
        return list(self._name_map.keys())
    def versions(self, distribution):
        raise NotImplemented
    def get(self, distribution, version):
        raise NotImplemented

    # Internal support functions
    def _normalise(self, name):
        return name.lower().replace('-', '_')

    @property
    def _name_map(self):
        if not hasattr(self, '_name_map_internal'):
            self._name_map_internal = dict((self._normalise(name), name)
                    for name in self._get_distributions())
        return self._name_map_internal

    # Functions to be implemented by subclasses
    def _get_distributions(self):
        """Return a list of all distribution names"""
        raise NotImplemented
    def _get_urls(self, distribution):
        """Return a list of URLs for a given distribution"""
        raise NotImplemented

class DictLocator(Locator):
    def __init__(self, dct):
        self.dct = dct
        self.dists = {}
    def add_dist(self, dist):
        ret = defaultdict(lambda: defaultdict(list))
        for filename in self.dct[dist]:
            ftype, d, ver = parse_filename(filename, dist)
            if ftype:
                ret[ver][ftype].append(filename)
        self.dists[dist] = ret
    def distributions(self):
        return self.dct.keys()
    def versions(self, dist):
        if not dist in self.dists:
            try:
                self.add_dist(dist)
            except KeyError:
                return []
        return self.dists[dist].keys()
    def files(self, dist, ver):
        if not dist in self.dists:
            try:
                self.add_dist(dist)
            except KeyError:
                return []
        return self.dists[dist][ver]

class DirectoryLocator(Locator):
    def __init__(self, path, recurse=False):
        self.path = Path(path)
        self.recurse = recurse
        self._filemap = None
    @property
    def filemap(self):
        """dist -> ver -> path mapping"""
        if self._filemap is None:
            self._filemap = defaultdict(lambda: defaultdict(list))
            if self.recurse:
                files = self.path.rglob("*")
            else:
                files = self.path.glob("*")
            for f in files:
                filetype, dist, ver = parse_filename(f.name)
                self._filemap[dist][ver].append(str(f.resolve()))
        return self._filemap
    def distributions(self):
        return sorted(self.filemap.keys())
    def versions(self, distribution):
        return sorted(self.filemap[distribution.lower().replace('-','_')].keys())
    def get(self, distribution, version):
        # Reformat the data...
        return self.filemap[distribution.lower().replace('-','_')][version]

class XMLRPCLocator(Locator):
    def __init__(self, url=PYPI_XMLRPC_URL):
        self.url = url
        self._proxy = None

    @property
    def proxy(self):
        if self._proxy is None:
            self._proxy = ServerProxy(self.url)
        return self._proxy

    def distributions(self):
        return self.proxy.list_packages()
    def versions(self, distribution, include_hidden=False):
        return self.proxy.package_releases(distribution, include_hidden)
    def get(self, distribution, version):
        # Reformat the data...
        return self.proxy.release_urls(distribution, version)

class JSONLocator(Locator):
    def __init__(self, url=PYPI_JSON_URL):
        self.url = url
        self.session = CacheControl(requests.session())
    def versions(self, distribution):
        url = "{}/{}/json".format(self.url, distribution)
        response = self.session.get(url)
        ret = []
        j = response.json()['releases']
        return [v for v, d in j.items() if len(d) > 0]
    def get(self, distribution, version):
        url = "{}/{}/json".format(self.url, distribution)
        response = self.session.get(url)
        # Reformat the data...
        return response.json()['releases'][version]

class SimpleLocator(Locator):
    def __init__(self, url=PYPI_SIMPLE_URL):
        self.url = url
    def distributions(self):
        links = scrape_links(self.url)
        return links
    def versions(self, distribution):
        links = scrape_links(self.url + distribution)
        ret = []
        for url in links:
            filename = url_basename(url)
            filetype, name, version = parse_filename(filename, distribution)
            if filetype:
                ret.append(version)
        return sorted(set(ret))
    def get(self, distribution, ver):
        links = scrape_links(self.url + distribution)
        ret = defaultdict(list)
        for url in links:
            filename = url_basename(url)
            filetype, name, version = parse_filename(filename, distribution)
            if version != ver:
                continue
            ret[filetype].append(url)
        return ret

# XMLRPC doesn't normalise names
# django and requests have versions with no urls

def dirfiles(dirname, recurse=False):
    if recurse:
        for dirpath, dirnames, filenames in os.walk(dirname):
            dirpath = os.path.abspath(dirpath)
            for filename in filenames:
                fullname = os.path.join(dirpath, filename)
                yield fullname
    else:
        for filename in os.listdir(dirname):
            filename = os.path.join(dirname, filename)
            if not os.path.isdir(filename):
                yield os.path.abspath(filename)
