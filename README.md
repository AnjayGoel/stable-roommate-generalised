# Stable Roommate Generalised

[![Tests](https://github.com/AnjayGoel/stable-roommate-generalised/actions/workflows/test.yml/badge.svg)](https://github.com/AnjayGoel/stable-roommate-generalised/actions/workflows/test.yml)

A heuristic algorithm for solving the generalised stable roommate problem, inspired by the difficulty of forming optimal
groups for collaborative projects. While this algorithm doesn't guarantee a stable solution, it does provides a
good approximation in reasonable time.

## Overview

Traditional stable roommate algorithms use ordinal preferences (rankings). This implementation uses **cardinal
preferences** (numerical ratings) because they:

- Carry more information about preference intensity
- Are easier to collect from participants
- Enable more sophisticated preference aggregation

## Problem Formulation

### Input

- **Preference Matrix**: Square matrix `P` where `P[i,j]` represents member `i`'s rating of member `j`
- **Group Size**: Target number of members per group (`k`)

### Output

- List of groups that maximize overall satisfaction

### Mathematical Model

**Group Formation**: Given `n` members, create `⌈n/k⌉` groups

**Preference Aggregation**:

- Member `i`'s preference for group `G`: $\text{pref}(i, G) = \frac{1}{|G|} \sum_{j \in G} P[i,j]$
- Group `G`'s preference for member `i`: $\text{pref}(G, i) = \frac{1}{|G|} \sum_{j \in G} P[j,i]$
- Group `G`'s own satisfaction with members ${m_1, m_2, ..., m_k}$:

$$\text{score}(G) = \frac{1}{k(k-1)} \sum_{i=1}^{k} \sum_{j=1, j \neq i}^{k} P[m_i, m_j]$$

**Objective**: Maximize average group satisfaction across all groups

## Algorithm

### Phase 1: Initialization

1. Calculate number of groups: `num_groups = ⌈n/k⌉`
2. Randomly select `num_groups` members as group seeds
3. Initialize each group with one seed member

### Phase 2: Member Assignment (Gale-Shapley Inspired)

For each round until all members are assigned:

1. **Proposal**: Each ungrouped member proposes to their most preferred available group
2. **Selection**: Each group accepts the member they prefer most among proposers
3. **Optimization**: Perform `optim_steps` rounds of hill-climbing swaps between groups

### Phase 3: Final Optimization

- Run `final_optim_steps` rounds of member swaps across all groups
- Accept swaps that improve overall score

### Complexity

- **Time**: O(n³ × iterations) worst case
- **Space**: O(n²) for preference matrix storage

## Usage

```python
import numpy as np
from algorithm import Matching

# Create preference matrix (example: 8 members)
prefs = np.random.rand(8, 8) * 10  # Random ratings 0-10

# Initialize and solve
matcher = Matching(prefs, group_size=4, optim_steps=2, final_optim_steps=4)
final_score, groups = matcher.solve()

print(f"Final score: {final_score:.2f}")
print(f"Groups: {groups}")
```

## Parameters

| Parameter           | Description                        | Default | Impact                               |
|---------------------|------------------------------------|---------|--------------------------------------|
| `group_size`        | Target members per group           | 4       | Affects group count and dynamics     |
| `optim_steps`       | Optimization rounds per assignment | 2       | Higher = better quality, slower      |
| `final_optim_steps` | Final optimization rounds          | 4       | Higher = better final result, slower |

## Limitations

- **Non-deterministic**: Results vary due to random initialization
- **Local optima**: Hill-climbing may miss global optimum
- **No stability guarantee**: Groups may contain members who prefer other arrangements
- **Computational cost**: Scales poorly with large groups and high optimisation counts

## Web Application

Try the interactive version: [Group Us](https://anjaygoel.github.io/GroupUs/#/)
