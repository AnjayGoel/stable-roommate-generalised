import numpy as np

from algorithm import *

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

matching = Matching(pref, group_size=r, iter_count=2, final_iter_count=2)
score, groups = matching.solve()
print(score)
print(groups)
