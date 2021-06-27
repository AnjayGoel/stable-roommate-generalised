import numpy as np
from typing import *
import random
import math


class Matching:
    def __init__(self, prefs: np.ndarray, group_size: int = 4, iter_count: int = 2, final_iter_count: int = 4):
        self.group_size = group_size
        self.prefs = prefs
        self.iter_count = iter_count
        self.final_iter_count = final_iter_count
        self.num_members = self.prefs.shape[0]
        self.num_groups = math.ceil(self.num_members / group_size)
        self.ungrouped = [i for i in range(self.num_members)]
        self.unfilled = []
        self.filled = []

        for i in random.sample(range(0, self.num_members), self.num_groups):
            self.unfilled.append(Group(self, [i]))
            self.ungrouped.remove(i)
        super().__init__()

    @staticmethod
    def from_csv(file_path, r: int = 4):
        prefs = np.genfromtxt(file_path, delimiter=',')
        return Matching(prefs, r)

    def get_mem_pref_for_group(self, mem: int, grp: List[int]) -> int:
        pref: int = 0
        for i in grp:
            pref += self.prefs[mem][i]
        pref = pref * (1.0 / len(grp))
        return pref

    def get_group_pref_for_mem(self, mem: int, grp: List[int]) -> int:
        pref: int = 0
        for i in grp:
            pref += self.prefs[i][mem]
        pref = pref * (1.0 / len(grp))
        return pref

    def get_group_score(self, y: List[int]) -> int:
        if len(y) <= 1:
            return 0
        score: int = 0
        for i in y:
            for j in y:
                if not (i == j):
                    score += self.prefs[i][j]
        score = score * (1.0 / (len(y) ** 2 - len(y)))
        return score

    def get_net_score(self) -> float:
        score = 0
        for i in self.filled:
            score += self.get_group_score(i.members)
        return score / self.num_groups

    def solve(self):
        while len(self.ungrouped) != 0:
            self.add_one_member()

        self.filled.extend(self.unfilled)
        self.unfilled = []
        self.optimize(use_filled=True)
        grps = []
        for i in self.filled:
            grps.append(i.members)
        return self.get_net_score(), grps

    def optimize(self, use_filled: bool = True):
        if use_filled:
            grps = self.filled
        else:
            grps = self.unfilled

        iters = self.final_iter_count if use_filled else self.iter_count

        for a in range(iters):
            for grp1 in grps:
                for mem1 in grp1.members:
                    for grp2 in grps:
                        if mem1 == -1:
                            break
                        if grp2 == grp1:
                            continue
                        for mem2 in grp2.members:
                            if mem1 == -1:
                                break
                            if mem2 == mem1:
                                continue
                            grp2mem1 = grp2.members.copy()
                            grp2mem1.remove(mem2)
                            grp2mem1.append(mem1)
                            grp1mem2 = grp1.members.copy()
                            grp1mem2.remove(mem1)
                            grp1mem2.append(mem2)

                            grp_one_new_score = self.get_group_score(grp1mem2)
                            grp_two_new_score = self.get_group_score(grp2mem1)

                            if (grp_one_new_score + grp_two_new_score > self.get_group_score(grp1.members) + self.get_group_score(
                                    grp2.members)):
                                grp1.add_member(mem2)
                                grp1.remove_member(mem1)
                                grp2.add_member(mem1)
                                grp2.remove_member(mem2)
                                mem1 = -1

    def add_one_member(self):

        proposed = np.zeros(
            shape=(len(self.ungrouped), len(self.unfilled)), dtype=bool)

        is_temp_grouped = [False for i in range(len(self.ungrouped))]

        temp_pref = np.zeros(
            shape=(len(self.ungrouped), len(self.unfilled)))

        temp_pref_order = np.zeros(
            shape=(len(self.ungrouped), len(self.unfilled)), dtype=int)

        for i, mem in enumerate(self.ungrouped):
            for j, grp in enumerate(self.unfilled):
                temp_pref[i][j] = self.get_mem_pref_for_group(mem, grp.members)

        for i, mem in enumerate(self.ungrouped):
            temp_pref_order[i] = np.argsort(temp_pref[i])[::-1]

        while is_temp_grouped.count(False) != 0:
            for i, mem in enumerate(self.ungrouped):

                if is_temp_grouped[i]:
                    continue

                if np.count_nonzero(proposed[i] == False) == 0:
                    is_temp_grouped[i] = True
                    continue
                for j in temp_pref_order[i]:
                    if proposed[i][j]:
                        continue

                    grp = self.unfilled[j]
                    proposed[i][j] = True
                    pref = self.get_group_pref_for_mem(mem, grp.members)
                    if pref > grp.tempScore:
                        if grp.tempMember >= 0:
                            is_temp_grouped[self.ungrouped.index(
                                grp.tempMember)] = False
                        grp.add_temp(mem)
                        is_temp_grouped[i] = True
                        break

        for grp in self.unfilled:
            if grp.tempMember < 0:
                continue
            self.ungrouped.remove(grp.tempMember)
            grp.add_permanently()

        self.optimize(use_filled=False)

        for grp in self.unfilled:
            if grp.size() >= self.group_size or len(self.ungrouped) == 0:
                self.filled.append(grp)

        for grp in self.filled:
            self.unfilled.remove(grp)


class Group:
    def __init__(self, game: Matching, members: List[int] = []):
        super().__init__()
        self.game = game
        self.members = members
        self.tempMember = -1
        self.tempScore = -1

    def add_member(self, x: int):
        self.members.append(x)

    def remove_member(self, x: int):
        self.members.remove(x)

    def add_temp(self, x: int) -> int:
        self.tempMember = x
        self.tempScore = self.game.get_group_pref_for_mem(x, self.members)
        return self.tempScore

    def add_permanently(self):
        if self.tempMember == -1:
            return
        self.add_member(self.tempMember)
        self.tempMember = -1
        self.tempScore = -1

    def size(self) -> int:
        return len(self.members)
