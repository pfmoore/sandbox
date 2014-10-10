import re
import wheel.egg2wheel
from wheel.install import WheelFile, BadWheelFile

#### Regular expressions
# Groups name, ver, pyver, arch
EGG_RE = wheel.egg2wheel.egg_info_re
# Matches a PEP 440 version (taken from packaging/version.py)
VERSION_RE_STR = r"""
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
"""
VERSION_RE = re.compile(VERSION_RE_STR, re.VERBOSE | re.IGNORECASE)
SDIST_RE = re.compile(r'''
    ^
    (?P<name>.*?)
    -
    (?P<ver>''' + VERSION_RE_STR + r''')
    \.(zip|tar\.gz|tar\.bz2|tgz|tar)
    $
''', re.VERBOSE | re.IGNORECASE)
########################

def parse_wheel_filename(filename):
    try:
        wf = WheelFile(filename)
    except BadWheelFile:
        raise ValueError("Wheel filename {} is not valid".format(filename))
    return (
        wf.parsed_filename.group('name'),
        wf.parsed_filename.group('ver'),
        wf.parsed_filename.group('pyver'),
        wf.parsed_filename.group('plat')
    )

def parse_wininst_filename(filename):
    # Parse the wininst filename
    #   name-ver.arch(-pyver).exe
    if filename.lower().endswith('.exe'):
        # Strip '.exe'
        filename = filename[:-4]
    else:
        raise ValueError("Installer filename {} is not valid".format(filename))

    # 1. Distribution name (up to the first '-')
    w_name, sep, rest = filename.partition('-')
    if not sep:
        raise ValueError("Installer filename {} is not valid".format(filename))
    # 2. Python version (from the last '-', must start with 'py')
    rest2, sep, w_pyver = rest.rpartition('-')
    if sep and w_pyver.startswith('py'):
        rest = rest2
        w_pyver = w_pyver.replace('.', '')
    else:
        # Not version specific
        w_pyver = ''
    # 3. Version and architecture
    w_ver, sep, w_arch = rest.rpartition('.')
    if not sep:
        raise ValueError("Installer filename {} is not valid".format(filename))

    return w_name, w_ver, w_pyver, w_arch

def parse_egg_filename(filename):
    m = EGG_RE.match(filename)
    if not m or m.end(0) != len(filename):
        raise ValueError("Egg filename {} is not valid".format(filename))
    return m.group('name'), m.group('ver'), m.group('pyver'), m.group('arch')

def parse_sdist_filename(filename):
    m = SDIST_RE.match(filename)
    if not m:
        raise ValueError("Sdist filename {} is not valid".format(filename))
    return m.group('name'), m.group('ver'), '', ''

file_types = [
    ('wheel', '.whl', parse_wheel_filename),
    ('wininst', '.exe', parse_wininst_filename),
    ('egg', '.egg', parse_egg_filename),
    ('sdist', ('.zip', '.tar.gz', '.tar.bz2', '.tgz', '.tar'),
              parse_sdist_filename),
]

def parse_filename(filename):
    for filetype, exts, parser in file_types:
        if filename.lower().endswith(exts):
            name, ver, pyver, arch = parser(filename)
            return filetype, name, ver, pyver, arch
    return None, '', '', '', ''
