Locators Library
================

A locator is an object that lets you find Python distribution files. Each
locator manages a single "source" of files, and provides the following
methods:

    * loc.distributions()
      Returns a list of distribution names.
    * loc.versions(dist)
      Returns a list of versions for the given distribution.
      Versions that do not conform to PEP 440 will be silently ignored.
    * loc.get(dist, ver)
      Get the files for a specific version of a distribution.
      The result is a dictionary, with keys for each type of file (sdist,
      wheel, egg, wininst). Unknown types of file will be silently ignored.
      The values in the dictionary are lists of files. (Note: what constitutes
      a "file" is locator-specific, it is typically either a filename or a
      URL. This is still subject to change).

Locators are all subclasses of a base Locator class. Subclasses should
implement the following methods:

    * loc.distributions()
      The base class implementation returns an empty list.
    * loc._versions(dist)
      The base class versions() method transforms the distribution name to
      canonical form (all lower case, dashes replaced with underscores) and
      calls this method.
      TODO: Should the base class check that dist is in distributions()?
      We don't want to validate everything, as it's duplication of effort.
      But we might need to do this because of the next point...
      TODO: Should the canonical form match what distributions() returns?
      The key issue here is XMLRPC which works off registered name, not
      canonical name.
    * loc._get(dist, ver)
      The base class get() method calls this method.
      Distribution name normalisation is done as for _versions.
