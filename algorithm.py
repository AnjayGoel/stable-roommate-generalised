import numpy as np
from typing import *
import random
import math
from subprocess import call
import os
import time

startTime = time.time()


def clear():
    _ = call('clear' if os.name == 'posix' else 'cls')


class Game:
    def __init__(self, prefs: np.ndarray, r: int = 4, iter1: int = 2, iter2: int = 4):
        self.r = r
        self.prefs = prefs
        self.iter1 = iter1
        self.iter2 = iter2
        self.n = self.prefs.shape[0]
        self.ng = math.ceil(self.n / r)
        self.ungrouped = [i for i in range(self.n)]
        self.unfilled = []
        self.filled = []

        for i in random.sample(range(0, self.n), self.ng):
            self.unfilled.append(Group(self, [i]))
            self.ungrouped.remove(i)
        super().__init__()

    @staticmethod
    def fromCSV(filePath, r: int = 4):
        prefs = np.genfromtxt(filePath, delimiter=',')
        return Game(prefs, r)

    def getPref(self, x: int, y: List[int]) -> int:
        pref: int = 0
        for i in y:
            pref += self.prefs[x][i]
        pref = pref * (1.0 / len(y))
        return pref

    def getGroupScore(self, y: List[int]) -> int:
        if (len(y) <= 1):
            return 0
        score: int = 0
        for i in y:
            for j in y:
                if not (i == j):
                    score += self.prefs[i][j]
        score = score * (1.0 / (len(y) ** 2-len(y)))
        return score

    def getNetScore(self) -> float:
        score = 0
        for i in self.filled:
            score += self.getGroupScore(i.members)
        return score/self.ng

    def solve(self):
        while (len(self.ungrouped) != 0):
            self.addOneMember()

        self.filled.extend(self.unfilled)
        self.unfilled = []
        self.optimize(useFilled=True)
        return self.getNetScore(), self.filled

    def optimize(self, useFilled: bool = True):
        if (useFilled):
            grps = self.filled
        else:
            grps = self.unfilled

        iter = self.iter2 if useFilled else self.iter1

        for a in range(iter):
            for grp1 in grps:
                for mem1 in grp1.members:
                    for grp2 in grps:
                        if (mem1 == -1):
                            break
                        if (grp2 == grp1):
                            continue
                        for mem2 in grp2.members:
                            if (mem1 == -1):
                                break
                            if (mem2 == mem1):
                                continue
                            grp2mem1 = grp2.members.copy()
                            grp2mem1.remove(mem2)
                            grp2mem1.append(mem1)
                            grp1mem2 = grp1.members.copy()
                            grp1mem2.remove(mem1)
                            grp1mem2.append(mem2)

                            grp1newScore = self.getGroupScore(grp1mem2)
                            grp2newScore = self.getGroupScore(grp2mem1)

                            if (grp1newScore + grp2newScore > self.getGroupScore(grp1.members) + self.getGroupScore(grp2.members)):
                                grp1.addMember(mem2)
                                grp1.removeMember(mem1)
                                grp2.addMember(mem1)
                                grp2.removeMember(mem2)
                                mem1 = -1

    def addOneMember(self):

        proposed = np.zeros(
            shape=(len(self.ungrouped), len(self.unfilled)), dtype=bool)

        isTempGrouped = [False for i in range(len(self.ungrouped))]

        tempPref = np.zeros(
            shape=(len(self.ungrouped), len(self.unfilled)))

        tempPrefOrder = np.zeros(
            shape=(len(self.ungrouped), len(self.unfilled)), dtype=int)

        for i, mem in enumerate(self.ungrouped):
            for j, grp in enumerate(self.unfilled):
                tempPref[i][j] = self.getPref(mem, grp.members)

        for i, mem in enumerate(self.ungrouped):
            tempPrefOrder[i] = np.argsort(tempPref[i])[::-1]

        while (isTempGrouped.count(False) != 0):
            for i, mem in enumerate(self.ungrouped):

                if (isTempGrouped[i]):
                    continue

                if (np.count_nonzero(proposed[i] == False) == 0):
                    isTempGrouped[i] = True
                    continue
                for j in tempPrefOrder[i]:
                    if (proposed[i][j]):
                        continue

                    grp = self.unfilled[j]
                    proposed[i][j] = True
                    if (tempPref[i][j] > grp.tempScore):
                        if grp.tempMember >= 0:
                            isTempGrouped[self.ungrouped.index(
                                grp.tempMember)] = False
                        grp.addTemp(mem)
                        isTempGrouped[i] = True
                        break

        for grp in self.unfilled:
            if (grp.tempMember < 0):
                continue
            self.ungrouped.remove(grp.tempMember)
            grp.addPermanently()

        self.optimize(useFilled=False)

        for grp in self.unfilled:
            if grp.size() >= self.r or len(self.ungrouped) == 0:
                self.filled.append(grp)

        for grp in self.filled:
            self.unfilled.remove(grp)


class Group:
    def __init__(self, game: Game, members: List[int] = []):
        super().__init__()
        self.game = game
        self.members = members
        self.tempMember = -1
        self.tempScore = -1

    def addMember(self, x: int):
        self.members.append(x)

    def removeMember(self, x: int):
        self.members.remove(x)

    def addTemp(self, x: int) -> int:
        self.tempMember = x
        self.tempScore = self.game.getPref(x, self.members)
        return self.tempScore

    def addPermanently(self):
        if (self.tempMember == -1):
            return
        self.addMember(self.tempMember)
        self.tempMember = -1
        self.tempScore = -1

    def size(self) -> int:
        return len(self.members)
