Functional Tests
================

We need some functional tests here, to show examples of using the library
in real-world scripts and to ensure that the design works in practice.

Use Cases
---------

1. Get the latest source distribution for a project.
2. Check if a project distributes wheels for its latest version.
3. Check a project to see if it has older wheels, but not for the latest
   version.
4. Report wininst and egg files that can usefully be converted into wheels
   for a project (i.e., there is no corresponding wheel)
5. Report projects with no released versions.

Extensions
----------

This covers possible uses that are not possible with the API as currently
defined. This may be for a number of reasons - the API needs to be more
flexible, the necessary data isn't available either via the API or from the
expected underlying dataset (the simple index is particularly limited).

1. Report when a project last released a file. (Needs upload time)
2. Report approximate time between releases. (Need upload time)

Interesting additional data
---------------------------

The following data (when available) might be useful for certain types of
query:

- Upload time (file creation time)
- File size
- Number of downloads

Maybe needs a ```get_extra_data()``` API?
