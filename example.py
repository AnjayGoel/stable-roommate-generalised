from algorithm import *
import numpy as np
prefs = np.genfromtxt("Data.csv", delimiter=',')
game = Game(prefs, r=4, iter2=2, iter1=2)
score, groups = game.solve()
print(score)
for i in groups:
    print(i.members)
