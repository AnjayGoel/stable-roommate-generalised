from algorithm import *
import numpy as np
import random
import math

n = 128
r = 4
pref = np.random.randint(1, 11, size=(n, n))
np.fill_diagonal(pref, 0)
np.savetxt("Data.csv", pref, delimiter=',', fmt="%d")

'''
perfect_groups = np.arange(n)
np.random.shuffle(perfect_groups)
perfect_groups =perfect_groups.reshape((-1,r))
for grp in perfect_groups:
    for i in grp:
        for j in grp:
            pref[i][j]=10
'''

game = Game(pref, r=r, iter2=2, iter1=2)
score, groups = game.solve()
print(score)
print(groups)
