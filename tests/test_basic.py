#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicImports(unittest.TestCase):
    """Basic import tests for all ACL modules"""
    
    def test_convolution_import(self):
        """Test convolution module import"""
        import convolution
        self.assertTrue(hasattr(convolution, 'FFT'))
    
    def test_dsu_import(self):
        """Test DSU module import"""
        import dsu
        self.assertTrue(hasattr(dsu, 'dsu'))
    
    def test_fenwicktree_import(self):
        """Test Fenwick Tree module import"""
        import fenwicktree
        self.assertTrue(hasattr(fenwicktree, 'fenwick_tree'))
    
    def test_fps_import(self):
        """Test FPS module import"""
        import fps
        # Check for any common FPS functions or classes
        module_attrs = dir(fps)
        self.assertTrue(len(module_attrs) > 0)
    
    def test_lazysegtree_import(self):
        """Test Lazy Segment Tree module import"""
        import lazysegtree
        self.assertTrue(hasattr(lazysegtree, 'lazy_segtree'))
    
    def test_math_import(self):
        """Test acl_math module import"""
        import acl_math
        # Check for common mathematical functions
        self.assertTrue(hasattr(acl_math, 'inv_mod') or 
                       hasattr(acl_math, 'crt') or
                       hasattr(acl_math, 'inv_gcd'))
    
    def test_maxflow_import(self):
        """Test Max Flow module import"""
        import maxflow
        self.assertTrue(hasattr(maxflow, 'mf_graph'))
    
    def test_mincostflow_import(self):
        """Test Min Cost Flow module import"""
        import mincostflow
        self.assertTrue(hasattr(mincostflow, 'mcf_graph'))
    
    def test_prime_fact_import(self):
        """Test prime factorization module import"""
        import prime_fact
        # Check for common prime factorization functions
        self.assertTrue(hasattr(prime_fact, 'prime_fact') or 
                       hasattr(prime_fact, 'is_probable_prime'))
    
    def test_scc_import(self):
        """Test SCC module import"""
        import scc
        self.assertTrue(hasattr(scc, 'scc'))
    
    def test_segtree_import(self):
        """Test Segment Tree module import"""
        import segtree
        self.assertTrue(hasattr(segtree, 'segtree'))
    
    def test_string_import(self):
        """Test acl_string module import"""
        import acl_string
        # Check for common string algorithms
        self.assertTrue(hasattr(acl_string, 'string'))
    
    def test_two_sat_import(self):
        """Test 2-SAT module import"""
        import two_sat
        self.assertTrue(hasattr(two_sat, 'two_sat'))






if __name__ == '__main__':
    unittest.main()