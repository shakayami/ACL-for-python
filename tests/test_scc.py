#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scc


class TestSCC(unittest.TestCase):
    """Test cases for scc module"""

    def practice2_g(self, N, M, edges, ans):
        res = scc.scc(N, edges)
        self.assertEqual(res, ans)

    def test_practice2_g(self):
        self.practice2_g(
            6,
            7,
            [(1, 4), (5, 2), (3, 0), (5, 5), (4, 1), (0, 3), (4, 2)],
            [[5], [1, 4], [2], [0, 3]],
        )

    def test_single_node_no_edges(self):
        """Test single node with no edges"""
        result = scc.scc(1, [])
        self.assertEqual(result, [[0]])

    def test_multiple_nodes_no_edges(self):
        """Test multiple nodes with no edges"""
        result = scc.scc(3, [])
        self.assertEqual(result, [[2], [1], [0]])

    def test_simple_cycle(self):
        """Test simple cycle: 0 -> 1 -> 2 -> 0"""
        edges = [(0, 1), (1, 2), (2, 0)]
        result = scc.scc(3, edges)
        self.assertEqual(result, [[0, 1, 2]])

    def test_chain_no_cycle(self):
        """Test chain with no cycle: 0 -> 1 -> 2"""
        edges = [(0, 1), (1, 2)]
        result = scc.scc(3, edges)
        self.assertEqual(result, [[0], [1], [2]])

    def test_two_separate_cycles(self):
        """Test two separate cycles: (0->1->0) and (2->3->2)"""
        edges = [(0, 1), (1, 0), (2, 3), (3, 2)]
        result = scc.scc(4, edges)
        # Sort each component and the components list for consistent comparison
        result_sorted = [sorted(component) for component in result]
        result_sorted.sort()
        expected = [[0, 1], [2, 3]]
        self.assertEqual(result_sorted, expected)

    def test_self_loop(self):
        """Test node with self-loop"""
        edges = [(0, 0)]
        result = scc.scc(1, edges)
        self.assertEqual(result, [[0]])

    def test_complex_graph(self):
        """Test complex graph with multiple SCCs"""
        # Graph: 0->1->2->3->1, 4->5->4, 6 (isolated)
        edges = [(0, 1), (1, 2), (2, 3), (3, 1), (4, 5), (5, 4)]
        result = scc.scc(7, edges)

        # Find components by checking which nodes are in the same component
        result_dict = {}
        for i, component in enumerate(result):
            for node in component:
                result_dict[node] = i

        # Check that nodes 1, 2, 3 are in the same component
        self.assertEqual(result_dict[1], result_dict[2])
        self.assertEqual(result_dict[2], result_dict[3])

        # Check that nodes 4, 5 are in the same component
        self.assertEqual(result_dict[4], result_dict[5])

        # Check that 0 and 6 are in separate components
        self.assertNotEqual(result_dict[0], result_dict[1])
        self.assertNotEqual(result_dict[6], result_dict[0])
        self.assertNotEqual(result_dict[6], result_dict[1])
        self.assertNotEqual(result_dict[6], result_dict[4])

    def test_star_graph(self):
        """Test star graph (one node connected to all others)"""
        # 0 -> 1, 0 -> 2, 0 -> 3 (no cycles)
        edges = [(0, 1), (0, 2), (0, 3)]
        result = scc.scc(4, edges)
        self.assertEqual(result, [[0], [1], [2], [3]])

    def test_complete_graph(self):
        """Test complete graph (all nodes connected to each other)"""
        edges = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
        result = scc.scc(3, edges)
        self.assertEqual(result, [[0, 1, 2]])

    def test_empty_graph(self):
        """Test empty graph (no nodes)"""
        result = scc.scc(0, [])
        self.assertEqual(result, [])

    def test_large_chain(self):
        """Test large chain graph"""
        n = 10
        edges = [(i, i + 1) for i in range(n - 1)]
        result = scc.scc(n, edges)
        # Each node should be in its own component in forward order
        expected = [[i] for i in range(n)]
        self.assertEqual(result, expected)

    def test_multiple_self_loops(self):
        """Test multiple nodes with self-loops"""
        edges = [(0, 0), (1, 1), (2, 2)]
        result = scc.scc(3, edges)
        self.assertEqual(result, [[2], [1], [0]])

    def test_bidirectional_edges(self):
        """Test graph with bidirectional edges"""
        # 0 <-> 1, 2 <-> 3, 0 -> 2
        edges = [(0, 1), (1, 0), (2, 3), (3, 2), (0, 2)]
        result = scc.scc(4, edges)

        # Check that 0,1 are in same component and 2,3 are in same component
        result_dict = {}
        for i, component in enumerate(result):
            for node in component:
                result_dict[node] = i

        self.assertEqual(result_dict[0], result_dict[1])
        self.assertEqual(result_dict[2], result_dict[3])
        self.assertNotEqual(result_dict[0], result_dict[2])

    def test_weakly_connected_components(self):
        """Test graph that is weakly connected but has multiple SCCs"""
        # 0 -> 1 -> 2 -> 3, 3 -> 4 -> 5 -> 3 (cycle in 3,4,5)
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 3)]
        result = scc.scc(6, edges)

        # Find which nodes are in the same components
        result_dict = {}
        for i, component in enumerate(result):
            for node in component:
                result_dict[node] = i

        # Nodes 3, 4, 5 should be in the same component
        self.assertEqual(result_dict[3], result_dict[4])
        self.assertEqual(result_dict[4], result_dict[5])

        # Nodes 0, 1, 2 should be in separate components
        self.assertNotEqual(result_dict[0], result_dict[1])
        self.assertNotEqual(result_dict[1], result_dict[2])
        self.assertNotEqual(result_dict[0], result_dict[3])

    def test_topological_order(self):
        """Test that SCCs are returned in topological order"""
        # DAG of SCCs: SCC{0} -> SCC{1,2} -> SCC{3}
        edges = [(0, 1), (1, 2), (2, 1), (1, 3), (2, 3)]
        result = scc.scc(4, edges)

        # Find positions in the result
        position = {}
        for i, component in enumerate(result):
            for node in component:
                position[node] = i

        # Check topological order: 0 should come before 1,2 which should come before 3
        self.assertLess(position[0], position[1])
        self.assertLess(position[0], position[2])
        self.assertLess(position[1], position[3])
        self.assertLess(position[2], position[3])

        # 1 and 2 should be in the same component
        self.assertEqual(position[1], position[2])


if __name__ == "__main__":
    unittest.main()
