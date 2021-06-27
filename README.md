# Stable Roommate Generalised

A heuristic algorithm for solving generalised stable-roommate problem, inspired by the difficulty in forming groups for
group projects.

The algorithm uses cardinal method (rating each member on a scale) instead of the usual preference ordering, because it
carries more information, is easier to collect, and makes aggregating preferences easier.

### Input

* A square matrix `pref` where `pref[i][j]` is preference (or rating) of  `i` for `j`
* `group_size`: Number of members in each group.
### Output
* List of groups.
### How does it work?

* number of groups = `ceil(num_members/group_size)`
* Randomly initialize each group with a single member.
* Let left over members propose to each group in order of their preference (Step is similar to Gale-Shapley algorithm).  Each group accepts one new member in each iteration.
* At end of each iteration, swap members between groups if swapping improves overall score (Step executed `iter_count` no of times).
 * Continue the process till the last member is grouped. 
 * Finally, iterate one last time to check if swapping members improves overall score (no of times looped is `final_iter_count`).

### Note

* Increasing `iter_count` and `final_iter_count` improves the matching but also increases execution time significantly.
* Each run of algorithm will give slightly different results (as initial step involves choosing random members). So, looping till a desired score threshold is reached is
  possible.
  
### Got a web app for this?
* [Yes](https://anjaygoel.github.io/GroupUs/#/)
