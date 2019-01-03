
def assertEqual(a, b):
    if a != b:
        raise AssertionError("{} != {}".format(
            repr(a), repr(b)))

def assertNotEqual(a, b):
    if a == b:
        raise AssertionError("{} == {}".format(
            repr(a), repr(b)))

def assertIn(a, b):
    if a not in b:
        raise AssertionError("{} not in {}".format(
            repr(a), repr(b)))

def assertNotIn(a, b):
    if a in b:
        raise AssertionError("{} in {}".format(
            repr(a), repr(b)))

def assertTrue(a):
    if not a:
        raise AssertionError("not {}".format(
            repr(a)))

def assertFalse(a):
    if a:
        raise AssertionError("{}".format(
            repr(a)))
