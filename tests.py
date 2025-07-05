import unittest
import numpy as np
import random
from algorithm import Matching


class TestMatching(unittest.TestCase):
    def test_all_zero_prefs(self):
        # Large 64x64 zero preference matrix
        prefs = np.zeros((64, 64))
        m = Matching(prefs, group_size=4, optim_steps=1, final_optim_steps=1)
        score, groups = m.solve()
        self.assertAlmostEqual(score, 0.0)

        # Expect 16 groups of at most size 4
        self.assertEqual(len(groups), 16)
        self.assertTrue(all(len(g) <= 4 for g in groups))

    def test_all_one_prefs(self):
        # Large 64x64 all-one preference matrix
        prefs = np.ones((64, 64))
        m = Matching(prefs, group_size=4)
        score, groups = m.solve()

        self.assertAlmostEqual(score, 1.0)

        # Expect 16 groups
        self.assertEqual(len(groups), 16)

    def test_perfect_groups(self):
        # Random perfect clusters of size 4 in a 64-member set
        size = 64
        group_size = 4
        prefs = np.zeros((size, size))

        # Generate 16 random non-overlapping clusters of size 4
        random.seed(42)
        members = list(range(size))
        random.shuffle(members)
        clusters = [members[i:i + group_size] for i in range(0, size, group_size)]

        # Populate prefs so that within each cluster prefs=1
        for cluster in clusters:
            for i in cluster:
                for j in cluster:
                    if i != j:
                        prefs[i][j] = 1

        m = Matching(prefs, group_size=group_size, optim_steps=8, final_optim_steps=8)
        score, groups = m.solve()

        # Expect a perfect score of 1.0 since all members are perfectly grouped
        self.assertAlmostEqual(score, 1.0)

        # Expect 16 perfect groups matching the generated clusters
        sorted_groups = sorted([sorted(g) for g in groups])
        expected = sorted([sorted(cluster) for cluster in clusters])

        self.assertEqual(sorted_groups, expected)

    def test_less_members_than_group(self):
        # Fewer members than group size
        prefs = np.random.rand(3, 3)
        m = Matching(prefs, group_size=5)
        score, groups = m.solve()
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 3)

    def test_single_member(self):
        prefs = np.array([[0]])
        m = Matching(prefs, group_size=4)
        score, groups = m.solve()
        self.assertEqual(score, 0.0)
        self.assertEqual(groups, [[0]])

    def test_group_size_one(self):
        prefs = np.random.rand(5, 5)
        m = Matching(prefs, group_size=1)
        score, groups = m.solve()
        self.assertEqual(len(groups), 5)
        self.assertTrue(all(len(g) == 1 for g in groups))

    def test_zero_iterations(self):
        prefs = np.random.rand(6, 6)
        m = Matching(prefs, group_size=3, optim_steps=0, final_optim_steps=0)
        score, groups = m.solve()
        # Ensure all members are assigned
        member_set = set(i for g in groups for i in g)
        self.assertEqual(member_set, set(range(6)))


if __name__ == '__main__':
    unittest.main()
