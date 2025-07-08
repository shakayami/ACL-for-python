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


if __name__ == "__main__":
    unittest.main()
