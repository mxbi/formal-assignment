from os import dup
from numpy.random.mtrand import f
import pandas as pd
from groups import Group

df = pd.read_csv('formal.csv')

all_people = []
groups = []
for _, group in df.iterrows():
    crsid1 = group['What is your crsID?'].lower().strip()
    if isinstance(group['Who else is in your group, if you have one?'], str):
        others = [x.lower().strip() for x in group['Who else is in your group, if you have one?'].replace(',', ' ').split(' ') if x]
    else:
        others = []

    if isinstance(group['Is there anyone else you would want to sit next to (outside of your group)?'], str):
        prefs = [x.lower().strip() for x in group['Is there anyone else you would want to sit next to (outside of your group)?'].replace(',', ' ').split(' ') if x]
    else:
        prefs = []

    dates = group['Which formals would you want tickets for?']

    if 'Wed' in dates:
        dateprefs = ['a', 'both']['Fri' in dates]
    elif 'Fri' in dates:
        dateprefs = 'c'

    g = Group([crsid1] + others, dateprefs)
    g.seating_prefs = prefs
    print(g)
    groups.append(g)
    all_people.extend(g.users)

seen = {}
dupes = []

for x in all_people:
    if x not in seen:
        seen[x] = 1
    else:
        if seen[x] == 1:
            dupes.append(x)
        seen[x] += 1

print(dupes)
assert not len(dupes)

for datepref in ['a', 'both', 'c']:
    print(datepref, sum([g.n for g in groups if g.dateprefs == datepref]))

from assignment import Assignment

ass = Assignment(table_size=8, num_tables=10, num_nights=2, verbose=True)
tables_wed, tables_fri = ass.run(groups, 5107553692733392547432348082803 % 2**32) # # as chosed by sam :)

print(tables_wed, tables_fri)

seen = []
for table in tables_wed:
    print(table, table.get_users())
    for user in table.get_users():
        assert user not in seen
        seen.append(user)

print('---')

for table in tables_fri:
    print(table, table.get_users())
    for user in table.get_users():
        assert user not in seen
        seen.append(user)


##################
# Allocation done
# Time to optimize seating plans
###################

from optimizer import SeatingOptimizer

sow = SeatingOptimizer(tables_wed)
sow.optimize()

new_wed_tables = sow.tables

sof = SeatingOptimizer(tables_fri)
sof.optimize()

new_fri_tables = sow.tables

output = open('assignment.txt', 'w')
output.write('WEDNESDAY\n\n')

for i, table in enumerate(tables_wed):
    output.write(f'TABLE {i+1}\n')
    for user in table.get_users():
        output.write(user + '\n')
    output.write('\n')

output.write('---\n')
output.write('FRIDAY\n\n')

for i, table in enumerate(tables_fri):
    output.write(f'TABLE {i+1}\n')
    for user in table.get_users():
        output.write(user + '\n')
    output.write('\n')