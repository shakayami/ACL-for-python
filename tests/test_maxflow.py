#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import maxflow


class TestMaxFlow(unittest.TestCase):
    """Test cases for maxflow module"""
    
    def test_placeholder(self):
        """Placeholder test - add your test cases here"""
        pass


if __name__ == '__main__':
    unittest.main()