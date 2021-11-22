# formal-assignment

Randomized fair assignment of tickets for a set of dinners, to students who sign up in groups.

Features:
- Students in a group will always be seated on the same table (solves bin packing)
- Students in a group will always be given tickets to the same dinner
- Each individual has an almost identical probability of getting a ticket, **regardless of the size of their group** (avoids smaller groups being more likely to get tickets on the basis that there's more likely to be space for them)
- Probability of getting a ticket is the same **regardless of if you sign up to one dinner or both** (and students only get tickets to one max)
- After tickets are allocated, a Simulated Annealing algorithm (see `optimizer.py`) is used to optimize seating placement to maximise as many seating preferences as possible.

## Evaluation

Fairness is evaluated based on a Monte Carlo simulation of randomised groups.
