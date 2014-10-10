from operator import itemgetter
import locators
import os
from pretend import stub

FILES = """\
project-0.1.0-py2.py3-none-any.whl
project-0.1.0.tar.gz
example-1.5.zip
""".strip().splitlines()

def test_listloc():
    loc = locators.ListLocator(FILES)
    assert loc.distributions() == ['project', 'example']
    assert loc.versions('project') == ['0.1.0']
    assert isinstance(loc.files('project', '0.1.0'), dict)
    assert loc.files('project', '0.1.0').keys() == {'wheel', 'sdist'}
    assert loc.files('project', '0.1.0')['sdist'] == ['project-0.1.0.tar.gz']

def test_listloc_with_key():
    loc = locators.ListLocator(zip(FILES, [1,2,3]), key=itemgetter(0))
    assert loc.distributions() == ['project', 'example']
    assert loc.versions('project') == ['0.1.0']
    assert isinstance(loc.files('project', '0.1.0'), dict)
    assert loc.files('project', '0.1.0').keys() == {'wheel', 'sdist'}
    assert loc.files('project', '0.1.0')['sdist'] == [2]

def test_listloc_with_key_2():
    loc = locators.ListLocator(FILES), key=lambda f: f[2:]))
    assert loc.distributions() == ['oject', 'ample']
    assert loc.versions('oject') == ['0.1.0']
    assert isinstance(loc.files('oject', '0.1.0'), dict)
    assert loc.files('oject', '0.1.0').keys() == {'wheel', 'sdist'}
    assert loc.files('oject', '0.1.0')['sdist'] == ['project-0.1.0.tar.gz']

def projfiles(key):
    assert key == 'project'
    return [
        'project-0.1.0-py2.py3-none-any.whl',
        'project-0.1.0.tar.gz',
    ]

def test_dictloc():
    loc = locators.DictLocator(stub(keys=lambda: ['project', 'example']))
    assert set(loc.distributions()) == {'project', 'example'}
    loc = locators.DictLocator(stub(__getitem__=projfiles))
    assert set(loc.versions('project')) == {'0.1.0'}
    assert isinstance(loc.files('project', '0.1.0'), dict)
    assert loc.files('project', '0.1.0').keys() == {'wheel', 'sdist'}
    assert set(loc.files('project', '0.1.0')['sdist']) == {'project-0.1.0.tar.gz'}
    # What to do with loc.versions('unknown') and loc.files('unknown', '???')
    # Or other error handling...
