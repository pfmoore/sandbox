import sys

def does_something_version_specific():
    if sys.version_info[0] == 2:
        s = "This is python "
        s += "2"
    else:
        s = "This is python "
        s += "3"
    return True
