import numpy as np
import random
import math

n = 128
r = 4

rnd = np.random.randint(1, 11, size=(n, n))
np.fill_diagonal(rnd, 0)
np.savetxt("Data.csv", rnd, delimiter=',', fmt="%d")
