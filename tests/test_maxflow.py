#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import maxflow


class TestMaxFlow(unittest.TestCase):
    """Test cases for maxflow module"""

    def tessoku_book_A68(self, N, M, query, ans):
        self.assertEqual(len(query), M)
        G = maxflow.mf_graph(N)
        for a, b, c in query:
            a -= 1
            b -= 1
            G.add_edge(a, b, c)

        res = G.flow(0, N - 1)
        self.assertEqual(ans, res)

    def test_tessoku_book_A68(self):
        self.tessoku_book_A68(
            6,
            7,
            [
                (1, 2, 5),
                (1, 4, 4),
                (2, 3, 4),
                (2, 5, 7),
                (3, 6, 3),
                (4, 5, 3),
                (5, 6, 5),
            ],
            8,
        )

    def practice2_d(self, N, M, S, ans):
        S = [list(s) for s in S]
        G = maxflow.mf_graph(N * M + 2)
        for i in range(N):
            for j in range(M):
                if S[i][j] == "#":
                    continue
                v = i * M + j
                if (i + j) % 2 == 0:
                    G.add_edge(N * M, v, 1)
                else:
                    G.add_edge(v, N * M + 1, 1)
        for i in range(N):
            for j in range(M):
                if (i + j) % 2 or S[i][j] == "#":
                    continue
                v0 = i * M + j
                if i > 0 and S[i - 1][j] == ".":
                    v1 = (i - 1) * M + j
                    G.add_edge(v0, v1, 1)
                if j > 0 and S[i][j - 1] == ".":
                    v1 = i * M + (j - 1)
                    G.add_edge(v0, v1, 1)
                if i + 1 < N and S[i + 1][j] == ".":
                    v1 = (i + 1) * M + j
                    G.add_edge(v0, v1, 1)
                if j + 1 < M and S[i][j + 1] == ".":
                    v1 = i * M + (j + 1)
                    G.add_edge(v0, v1, 1)

        res = G.flow(N * M, N * M + 1)
        self.assertEqual(ans, res)

    def test_practice2_d(self):
        self.practice2_d(3, 3, ["#..", "..#", "..."], 3)

    def test_simple_flow(self):
        """Test simple max flow"""
        # Simple path: 0 -> 1 -> 2
        g = maxflow.mf_graph(3)
        g.add_edge(0, 1, 10)
        g.add_edge(1, 2, 5)
        flow = g.flow(0, 2)
        self.assertEqual(flow, 5)

    def test_no_path(self):
        """Test when there's no path from source to sink"""
        g = maxflow.mf_graph(3)
        g.add_edge(0, 1, 10)
        # No edge from 1 to 2
        flow = g.flow(0, 2)
        self.assertEqual(flow, 0)

    def test_single_node(self):
        """Test max flow with source same as sink (should be invalid)"""
        g = maxflow.mf_graph(2)
        g.add_edge(0, 1, 10)
        # Source and sink must be different in this implementation
        with self.assertRaises(AssertionError):
            g.flow(0, 0)

    def test_parallel_edges(self):
        """Test parallel edges between same vertices"""
        g = maxflow.mf_graph(2)
        g.add_edge(0, 1, 3)
        g.add_edge(0, 1, 5)
        g.add_edge(0, 1, 2)
        flow = g.flow(0, 1)
        self.assertEqual(flow, 10)  # 3 + 5 + 2

    def test_multiple_paths(self):
        """Test multiple paths from source to sink"""
        # Diamond graph: 0 -> {1,2} -> 3
        g = maxflow.mf_graph(4)
        g.add_edge(0, 1, 10)
        g.add_edge(0, 2, 8)
        g.add_edge(1, 3, 6)
        g.add_edge(2, 3, 9)
        flow = g.flow(0, 3)
        self.assertEqual(flow, 14)  # min(10,6) + min(8,8) = 6 + 8

    def test_bottleneck(self):
        """Test bottleneck in the middle"""
        # 0 -> 1 -> 2 -> 3 with bottleneck at 1->2
        g = maxflow.mf_graph(4)
        g.add_edge(0, 1, 100)
        g.add_edge(1, 2, 1)  # Bottleneck
        g.add_edge(2, 3, 100)
        flow = g.flow(0, 3)
        self.assertEqual(flow, 1)

    def test_zero_capacity_edges(self):
        """Test edges with zero capacity"""
        g = maxflow.mf_graph(3)
        g.add_edge(0, 1, 0)
        g.add_edge(1, 2, 10)
        flow = g.flow(0, 2)
        self.assertEqual(flow, 0)

    def test_edge_operations(self):
        """Test edge addition and retrieval"""
        g = maxflow.mf_graph(3)
        edge_id = g.add_edge(0, 1, 5)

        # Get edge before flow
        edge = g.get_edge(edge_id)
        self.assertEqual(edge.From, 0)
        self.assertEqual(edge.To, 1)
        self.assertEqual(edge.Cap, 5)
        self.assertEqual(edge.Flow, 0)

    def test_edges_after_flow(self):
        """Test edge states after running max flow"""
        g = maxflow.mf_graph(3)
        edge_id = g.add_edge(0, 1, 10)
        g.add_edge(1, 2, 5)

        flow = g.flow(0, 2)
        self.assertEqual(flow, 5)

        # Check edge flow
        edge = g.get_edge(edge_id)
        self.assertEqual(edge.Flow, 5)

    def test_complex_network(self):
        """Test complex network with multiple sources and sinks"""
        # Create a more complex flow network
        g = maxflow.mf_graph(6)
        g.add_edge(0, 1, 16)
        g.add_edge(0, 2, 13)
        g.add_edge(1, 2, 10)
        g.add_edge(1, 3, 12)
        g.add_edge(2, 1, 4)
        g.add_edge(2, 4, 14)
        g.add_edge(3, 2, 9)
        g.add_edge(3, 5, 20)
        g.add_edge(4, 3, 7)
        g.add_edge(4, 5, 4)

        flow = g.flow(0, 5)
        self.assertGreater(flow, 0)
        self.assertIsInstance(flow, int)

    def test_flow_with_limit(self):
        """Test max flow with flow limit"""
        g = maxflow.mf_graph(3)
        g.add_edge(0, 1, 100)
        g.add_edge(1, 2, 100)

        # Test flow with limit
        limited_flow = g.flow(0, 2, 50)
        self.assertEqual(limited_flow, 50)

        # Check remaining capacity
        total_flow = g.flow(0, 2)
        self.assertEqual(total_flow, 50)  # Should be 50 more

    def test_self_loop(self):
        """Test handling of self-loops"""
        g = maxflow.mf_graph(2)
        g.add_edge(0, 0, 10)  # Self-loop
        g.add_edge(0, 1, 5)

        flow = g.flow(0, 1)
        self.assertEqual(flow, 5)


if __name__ == "__main__":
    unittest.main()
