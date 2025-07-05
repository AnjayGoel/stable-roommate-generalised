import numpy as np
import random
import math
from typing import List, Tuple


class Matching:
    """
    A heuristic algorithm for solving the generalized stable roommate problem.
    The algorithm groups members based on a matrix of cardinal preferences (ratings)
    to maximize overall group satisfaction.
    """

    def __init__(self, prefs: np.ndarray, group_size: int = 4, optim_steps: int = 2, final_optim_steps: int = 4):
        """
        Initializes the Matching algorithm.

        Args:
            prefs (np.ndarray): A square matrix where prefs[i, j] is the preference of member i for member j.
            group_size (int): The target number of members in each group.
            optim_steps (int): Number of optimization iterations after adding each member.
            final_optim_steps (int): Number of final optimization iterations after all members are grouped.
        """

        if not isinstance(prefs, np.ndarray) or prefs.ndim != 2 or prefs.shape[0] != prefs.shape[1]:
            raise ValueError("Preferences must be a square 2D NumPy array.")

        if group_size <= 0:
            raise ValueError("Group size must be a positive integer.")

        if optim_steps < 0 or final_optim_steps < 0:
            raise ValueError("Iteration counts must be non-negative integers.")

        if np.any(prefs < 0):
            raise ValueError("Preferences must be non-negative.")

        self.prefs = prefs
        self.group_size = group_size
        self.optim_steps = optim_steps
        self.final_optim_steps = final_optim_steps

        self.num_members = self.prefs.shape[0]
        self.num_groups = math.ceil(self.num_members / self.group_size)

        # Members who are not yet grouped
        self.ungrouped = list(range(self.num_members))

        # Groups that are currently not at max capacity
        self.unfilled_groups: List[List[int]] = []

        # Groups that have been filled to capacity
        self.filled_groups: List[List[int]] = []

        # Randomly select initial members to seed each group
        if self.num_groups > 0:
            initial_members = random.sample(self.ungrouped, self.num_groups)
            for mem in initial_members:
                self.unfilled_groups.append([mem])
                self.ungrouped.remove(mem)

    @staticmethod
    def from_csv(file_path: str, group_size: int = 4) -> 'Matching':
        """Creates a Matching instance from a CSV file."""
        prefs = np.genfromtxt(file_path, delimiter=',', dtype=float)
        return Matching(prefs, group_size)

    def get_mem_pref_for_group(self, mem: int, grp: List[int]) -> float:
        """Calculates a member's average preference for a group using NumPy."""
        if not grp:
            return 0.0

        return self.prefs[mem, grp].mean()

    def get_group_pref_for_mem(self, mem: int, grp: List[int]) -> float:
        """Calculates a group's average preference for a member using NumPy."""
        if not grp:
            return 0.0

        return self.prefs[grp, mem].mean()

    def get_group_score(self, grp: List[int]) -> float:
        """
        Calculates the internal preference score for a single group using NumPy.
        The score is the average of all non-self preferences among members.
        """
        n = len(grp)
        if n <= 1:
            return 0.0

        # Create a sub-matrix of preferences using np.ix_
        group_prefs = self.prefs[np.ix_(grp, grp)]

        # Sum all preferences and subtract the diagonal (self-preferences)
        total_pref = group_prefs.sum() - np.trace(group_prefs)

        # Normalize by the number of connections
        return total_pref / (n * (n - 1))

    def get_net_score(self, groups: List[List[int]]) -> float:
        """Calculates the average score across all provided groups."""
        if not groups:
            return 0.0

        total_score = sum(self.get_group_score(grp) for grp in groups)
        return total_score / len(groups)

    def solve(self) -> Tuple[float, List[List[int]]]:
        """
        Runs the full matching algorithm.

        Returns:
            A tuple containing the final net score and the list of groups.
        """

        while self.ungrouped:
            # Assign one member to groups
            self._add_one_member_to_groups()

            # Intermediate optimization by swapping members between groups
            self._optimize(self.unfilled_groups, self.optim_steps)

        # Move all remaining unfilled groups to the filled list
        self.filled_groups.extend(self.unfilled_groups)
        self.unfilled_groups = []

        # Final optimization swaps on all groups
        self._optimize(self.filled_groups, self.final_optim_steps)

        final_score = self.get_net_score(self.filled_groups)
        return final_score, self.filled_groups

    def _optimize(self, groups: List[List[int]], iters: int):
        """
        Improves matching by swapping members between groups if it increases the total score.
        This is a hill-climbing optimization step.
        """
        if iters <= 0 or not groups:
            return

        for _ in range(iters):
            group_scores = [self.get_group_score(g) for g in groups]

            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):  # Compare each pair of groups once
                    grp1 = groups[i]
                    grp2 = groups[j]

                    # Iterate over a copy of members as the original list might be modified
                    for mem1 in grp1[:]:
                        swapped = False
                        for mem2 in grp2[:]:
                            # Create hypothetical new groups after the swap
                            new_grp1 = [m for m in grp1 if m != mem1] + [mem2]
                            new_grp2 = [m for m in grp2 if m != mem2] + [mem1]

                            # Check if the swap is beneficial
                            score_after = self.get_group_score(new_grp1) + self.get_group_score(new_grp2)
                            score_before = group_scores[i] + group_scores[j]

                            if score_after > score_before:
                                # Perform the swap on the actual group lists
                                grp1.remove(mem1)
                                grp1.append(mem2)
                                grp2.remove(mem2)
                                grp2.append(mem1)

                                # Update cached scores and break to re-evaluate with the new group
                                group_scores[i] = self.get_group_score(grp1)
                                group_scores[j] = self.get_group_score(grp2)
                                swapped = True
                                break
                        if swapped:
                            # A swap occurred, continue the `mem1` loop with the now-modified grp1
                            continue

    def _add_one_member_to_groups(self):
        """
        Performs one round of member proposals to groups, inspired by the Gale-Shapley algorithm.
        """
        if not self.ungrouped or not self.unfilled_groups:
            return

        # Each ungrouped member evaluates and ranks the unfilled groups
        member_proposals = np.array([
            [self.get_mem_pref_for_group(mem, grp) for grp in self.unfilled_groups]
            for mem in self.ungrouped
        ])
        member_proposal_order = np.argsort(-member_proposals, axis=1)

        # Groups receive proposals and decide
        temp_members = np.full(len(self.unfilled_groups), -1, dtype=int)
        temp_scores = np.full(len(self.unfilled_groups), -1.0, dtype=float)

        member_is_engaged = [False] * len(self.ungrouped)
        proposal_index = [0] * len(self.ungrouped)

        free_members_exist = True
        while free_members_exist:
            free_members_exist = False
            for i, mem in enumerate(self.ungrouped):
                if member_is_engaged[i] or proposal_index[i] >= len(self.unfilled_groups):
                    continue

                free_members_exist = True

                group_idx = member_proposal_order[i, proposal_index[i]]
                proposal_index[i] += 1

                group_pref_for_mem = self.get_group_pref_for_mem(mem, self.unfilled_groups[group_idx])

                if group_pref_for_mem > temp_scores[group_idx]:
                    old_suitor = int(temp_members[group_idx])
                    if old_suitor != -1:
                        old_suitor_idx = self.ungrouped.index(old_suitor)
                        member_is_engaged[old_suitor_idx] = False

                    temp_members[group_idx] = mem
                    temp_scores[group_idx] = group_pref_for_mem
                    member_is_engaged[i] = True

        # Add the accepted members permanently for this round
        for i, mem in enumerate(temp_members):
            if mem != -1:
                self.unfilled_groups[i].append(mem)
                self.ungrouped.remove(mem)

        # Move groups that are now full to the 'filled' list
        # Iterate backwards to safely remove items while iterating
        for i in range(len(self.unfilled_groups) - 1, -1, -1):
            if len(self.unfilled_groups[i]) >= self.group_size:
                self.filled_groups.append(self.unfilled_groups.pop(i))
