# Stable Roommate Generalised
A heuristic algorithm for solving generalised stable-roommate problem, inspired by the difficulty in forming groups for group projects.

The algorithm uses cardinal method (rating each member on a scale) instead of the usual preference ordering, because it carry more information, are easier to collect, and make aggregating preferences easier. 

### Input

* A square matrix `p` where `p[i][j]` is preference (or rating) of  `i` for `j`
* `r` no of members in each group.

### How does it work?

​	Randomly choose `ng` (`ceil(n/r)`) members to make `ng` groups. Let `n-ng` members propose to each group in order of their preference (Step is similar to Gale-Shapley algorithm).  Each group accepts one new member in each iteration. At end of each iteration, loop through grouped members to check if switching their groups improves overall score (no of times looped is `iter1`). Continue iterating till each member is grouped. Finally loop one last time to check if switching groups improves overall score (no of times looped is `iter2`).

### Note
* Increasing `iter1` and `iter2` improves the matchings but also increases execution time signifficantly.
* Each run of algorithm will give slightly different results. So, looping till a desired score threshold is reached is possible.
