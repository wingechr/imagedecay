# coding: utf-8

import os
import doctest
import unittest


# find all modules in source path

modules = []
for r, ds, fs in os.walk('src'):
    r_ = '.'.join(os.path.split(r)[1:])  # remove leading src, replace
    for f in fs:
        if f.endswith('.py') and f != '__init__.py':
            f = r_ + '.' + f.replace('.py', '')
            modules.append(f)


# load doctests for modules

def load_tests(loader, tests, ignore):
    """
    Loads doctests for all specified modules.
    """
    for m in modules:
        tests.addTests(doctest.DocTestSuite(m))
    return tests


# add additional tests

class TestTemplate(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # EXAMPLE
    #def test_TEMPLATE(self):
    #    expected_result = 0
    #    actual_result = (lambda: 0)()
    #    self.assertEqual(actual_result, expected_result, "ERROR_MESSAGE")
