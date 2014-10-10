from locators import SimpleLocator

def test_latest_source():
    loc = SimpleLocator()
    proj = 'pip'
    latest = max(loc.versions(proj))
    # We want the first item in the following list
    assert len(loc.get(proj, latest)['sdist']) != 0

def test_has_wheels():
    loc = SimpleLocator()
    proj = 'pip'
    latest = max(loc.versions(proj))
    # This will fail if there is no 'wheel' key.
    # Maybe require all keys to be present?
    assert len(loc.get(proj, latest)['wheel']) != 0

def test_has_old_wheels():
    loc = SimpleLocator()
    proj = 'pip'
    versions = sorted(loc.versions(proj))
    older = any(len(loc.get(proj, v)['wheel']) > 0 for v in versions[:-1])
    current = len(loc.get(proj, versions[-1])['wheel']) != 0

def test_no_released_versions():
    loc = SimpleLocator()
    [d for d in loc.distributions() if not loc.versions(d)]
