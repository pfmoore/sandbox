try:
    from urllib.parse inport urlparse
except ImportError:
    from urlparse import urlparse

import re
import posixpath

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

class URL:
    def __init__(self, url, distribution=None):
        self.url = urlparse(url)
        self.basename = posixpath.basename(self.url.path)
        # What if basename doesn't start with distribution? We probably want to
        # check and not create a URL in that case, rather than raise ValueError...
        if distribution and self.basename[len(distribution)] != '-':
            raise ValueError("Distribution name {} is not a prefix of filename in {}".format(distribution, url))
        if distribution:
            self.distribution = distribution.lower().replace('-', '_')
        else:
            name, sep, rest = self.basename.partition('-')
            self.distribution = name.lower()

    extension_types = [
        ('sdist', ('.zip', '.tar.gz', '.tar.bz2', '.tgz', '.tar',)),
        ('wheel', ('.whl',)),
        ('wininst', ('.exe',)),
        ('egg', ('.egg',)),
    ]


    @property
    def version(self):
        m = VERSION_RE.match(self.basename, len(self.distribution)+1)
        if m:
            return m.group(0)
        return None

    @property
    def filetype(self):
        for filetype, extns in self.extension_types:
            if self.basename.endswith(extns):
                return filetype
        return None
