#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mincostflow


class TestMinCostFlow(unittest.TestCase):
    """Test cases for mincostflow module"""

    def practice2_e(self, n, k, A, ans):
        BIG = 10**9
        g = mincostflow.mcf_graph(2 * n + 2)
        s = 2 * n
        t = 2 * n + 1
        g.add_edge(s, t, n * k, BIG)
        for i in range(n):
            g.add_edge(s, i, k, 0)
            g.add_edge(n + i, t, k, 0)
        for i in range(n):
            for j in range(n):
                g.add_edge(i, n + j, 1, BIG - A[i][j])
        result = g.flow(s, t, n * k)
        res = n * k * BIG - result[1]
        self.assertEqual(res, ans)

    def test_practice2_e_1(self):
        self.practice2_e(3, 1, [[5, 3, 2], [1, 4, 8], [7, 6, 9]], 19)

    def test_practice_e_2(self):
        self.practice2_e(3, 2, [[10, 10, 1], [10, 10, 1], [1, 1, 10]], 50)

    def test_simple_flow(self):
        """Test simple min cost flow"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, 2)  # capacity 5, cost 2
        g.add_edge(1, 2, 3, 1)  # capacity 3, cost 1

        flow, cost = g.flow(0, 2, 3)
        self.assertEqual(flow, 3)
        self.assertEqual(cost, 9)  # 3 * (2 + 1) = 9

    def test_no_path(self):
        """Test when there's no path"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, 2)
        # No path from 0 to 2
        flow, cost = g.flow(0, 2, 10)
        self.assertEqual(flow, 0)
        self.assertEqual(cost, 0)

    def test_zero_flow_demand(self):
        """Test with zero flow demand"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, 2)
        g.add_edge(1, 2, 3, 1)

        flow, cost = g.flow(0, 2, 0)
        self.assertEqual(flow, 0)
        self.assertEqual(cost, 0)

    def test_capacity_limit(self):
        """Test flow limited by capacity"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 2, 1)  # bottleneck capacity 2
        g.add_edge(1, 2, 10, 1)

        flow, cost = g.flow(0, 2, 5)  # demand 5 but capacity allows only 2
        self.assertEqual(flow, 2)
        self.assertEqual(cost, 4)  # 2 * (1 + 1) = 4

    def test_multiple_paths_different_costs(self):
        """Test multiple paths with different costs"""
        g = mincostflow.mcf_graph(4)
        # Path 1: 0 -> 1 -> 3 (cost = 1 + 1 = 2)
        g.add_edge(0, 1, 3, 1)
        g.add_edge(1, 3, 3, 1)
        # Path 2: 0 -> 2 -> 3 (cost = 2 + 3 = 5)
        g.add_edge(0, 2, 3, 2)
        g.add_edge(2, 3, 3, 3)

        # Should use cheaper path first
        flow, cost = g.flow(0, 3, 4)
        self.assertEqual(flow, 4)
        # First 3 units use path 1 (cost 6), next 1 unit uses path 2 (cost 5)
        self.assertEqual(cost, 11)

    def test_negative_cost_edges(self):
        """Test edges with negative costs"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, -2)  # negative cost
        g.add_edge(1, 2, 5, 1)

        flow, cost = g.flow(0, 2, 3)
        self.assertEqual(flow, 3)
        self.assertEqual(cost, -3)  # 3 * (-2 + 1) = -3

    def test_edge_operations(self):
        """Test edge addition and retrieval"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, 3)

        # Get edge (add_edge doesn't return edge id in this implementation)
        edge = g.get_edge(0)  # First edge has index 0
        self.assertEqual(edge["from"], 0)
        self.assertEqual(edge["to"], 1)
        self.assertEqual(edge["cap"], 5)
        self.assertEqual(edge["flow"], 0)
        self.assertEqual(edge["cost"], 3)

    def test_edges_after_flow(self):
        """Test edge states after running min cost flow"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 10, 2)  # First edge
        g.add_edge(1, 2, 5, 1)  # Second edge

        flow, cost = g.flow(0, 2, 5)
        self.assertEqual(flow, 5)

        # Check edge flow
        edge = g.get_edge(0)  # First edge
        self.assertEqual(edge["flow"], 5)

    def test_all_edges(self):
        """Test getting all edges"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, 2)
        g.add_edge(1, 2, 3, 1)

        edges = g.edges()
        self.assertEqual(len(edges), 2)

        self.assertEqual(edges[0]["from"], 0)
        self.assertEqual(edges[0]["to"], 1)
        self.assertEqual(edges[1]["from"], 1)
        self.assertEqual(edges[1]["to"], 2)

    def test_complex_network(self):
        """Test complex min cost flow network"""
        g = mincostflow.mcf_graph(5)
        g.add_edge(0, 1, 3, 1)
        g.add_edge(0, 2, 2, 2)
        g.add_edge(1, 2, 1, 1)
        g.add_edge(1, 3, 2, 2)
        g.add_edge(2, 3, 1, 1)
        g.add_edge(2, 4, 2, 3)
        g.add_edge(3, 4, 3, 1)

        flow, cost = g.flow(0, 4, 4)
        self.assertGreaterEqual(flow, 0)
        self.assertGreaterEqual(cost, 0)
        self.assertIsInstance(flow, int)
        self.assertIsInstance(cost, int)

    def test_self_loop_with_cost(self):
        """Test self-loop with cost (should not affect flow)"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 0, 10, 5)  # Self-loop
        g.add_edge(0, 1, 5, 2)
        g.add_edge(1, 2, 5, 1)

        flow, cost = g.flow(0, 2, 3)
        self.assertEqual(flow, 3)
        self.assertEqual(cost, 9)  # Should ignore self-loop

    def test_zero_cost_edges(self):
        """Test edges with zero cost"""
        g = mincostflow.mcf_graph(3)
        g.add_edge(0, 1, 5, 0)  # zero cost
        g.add_edge(1, 2, 5, 0)  # zero cost

        flow, cost = g.flow(0, 2, 3)
        self.assertEqual(flow, 3)
        self.assertEqual(cost, 0)


if __name__ == "__main__":
    unittest.main()
