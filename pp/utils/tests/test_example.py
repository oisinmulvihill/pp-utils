# -*- coding: utf-8 -*-
import unittest

import nose


class MyTestCase(unittest.TestCase):
    def setUp(self):
       	pass

    def tearDown(self):
        pass

    def test_my_code(self):
    	raise nose.SkipTest("Tests needed for: pp.utils")
