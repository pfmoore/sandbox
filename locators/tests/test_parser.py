from locators import parser
import pytest
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'data', 'filenames.txt')) as f:
    tests = [line.strip().split('\t') for line in f]

def norm(txt):
    return txt.lower().replace('-','_')

@pytest.mark.parametrize("filename, filetype, name, version", tests)
def test_parser(filename, filetype, name, version):
    t, n, v, _, _ = parser.parse_filename(filename)
    assert filetype == t, (t,n,v)
    assert norm(name) == norm(n), (t,n,v)
    assert norm(version) == norm(v), (t,n,v)
