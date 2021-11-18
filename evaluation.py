from assignment import Assignment
from groups import generate_groups

import pandas as pd
import numpy as np

def flatten(t):
    return [item for sublist in t for item in sublist]

all_all_people = []
for i in range(5000):
    assignment = Assignment(table_size=8, num_tables=10, num_nights=2, verbose=False)

    groups = generate_groups(100, size_dist=[0.2, 0.2, 0.2, 0.4], seed=i)

    assignment = assignment.run(groups, assignment_seed=i)
    tables = assignment[0] + assignment[1]
    assigned_people = [t.get_users() for t in tables]
    assigned_people = set(flatten(assigned_people))
    # print(len(assigned_people))

    all_people = []
    for group in groups:
        for user in group.users:
            all_people.append({'uid': user, 'dateprefs': group.dateprefs, 'n': group.n, 'assigned': user in assigned_people})

    all_all_people.extend(all_people)
    # df = pd.DataFrame(all_people)

df = pd.DataFrame(all_all_people)

print('Number of people in each group size')
print(df.groupby('n')['assigned'].count())

print('Probability of ticket given group size')
print(df.groupby('n')['assigned'].mean())

print('Probability of ticket given which formals were signed up to')
print(df.groupby('dateprefs')['assigned'].mean())