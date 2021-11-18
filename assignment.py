from groups import generate_groups
from itertools import groupby
import numpy as np
from math import ceil
import random

class Table:
    def __init__(self, size):
        self.size = size
        self.groups = []

    @property
    def n(self) -> int:
        return sum([g.n for g in self.groups])

    @property
    def spaces(self) -> int:
        return self.size - self.n

    @property
    def full(self) -> bool:
        return self.n == self.size

    def can_fit(self, group):
        return self.n + group.n <= self.size

    def can_fit_exactly(self, group):
        return self.n + group.n == self.size

    def seat(self, group):
        self.groups.append(group)

    def __repr__(self):
        return f'T[{self.n}/{self.size} ({len(self.groups)})]'

    def get_users(self):
        return [user for g in self.groups for user in g.users]

class NotEnoughTables(Exception):
    pass

class Assignment:
    def __init__(self, table_size, num_tables, num_nights=2, verbose=True):
        # TODO: Support more than two nights
        # This would require a change to the fair splitting algorithm
        assert num_nights == 2
        self.table_size = table_size
        self.num_tables = num_tables
        self.num_nights = num_nights
        self.verbose = verbose

    def fit_group_into_tables(self, group, tables):
        """
        Given a set of tables, and a group, attempt to seat the group somewhere at the tables.
        """
        # If we have a table where we fit exactly, take that.
        for table in tables:
            if table.can_fit_exactly(group):
                table.seat(group)
                return 

        # Otherwise, use the first table where we fit at all
        for table in tables:
            if table.can_fit(group):
                table.seat(group)
                return

        # There wasn't anywhere we could fit this group
        raise NotEnoughTables()


    def sort_into_tables(self, groups, extra_tables=0):
        """
        Given a set of groups, fit them into ceil(groups/table_size) tables. 
        If this fails, you can provide an `extra_tables` argument
        """
        total_people = sum([g.n for g in groups])
        num_tables = ceil(total_people / self.table_size)

        if self.verbose:
            print(f'{total_people} people, making {num_tables}+{extra_tables} tables')

        tables = [Table(self.table_size) for _ in range(num_tables + extra_tables)]
        
        # Go from largest to smallest group sizes
        groups = sorted(groups, key=lambda g: g.n, reverse=True)
        for group in groups:
            # Fit each group into the tables
            self.fit_group_into_tables(group, tables)

        return tables

    def run(self, groups, assignment_seed=42):
        np.random.seed(assignment_seed)
        random.seed(assignment_seed)

        groups_sorted_by_night = sorted(groups, key=lambda x: x.dateprefs)

        all_tables = []
        for night, subgroups in groupby(groups_sorted_by_night, key=lambda x: x.dateprefs):
            subgroups = list(subgroups)

            extra_tables = 0
            while True:
                try:
                    tables = self.sort_into_tables(subgroups, extra_tables)
                    break
                except NotEnoughTables:
                    # We may not be able to fit into ceil() tables, so we'll try again with one more table
                    # print(f'[WARN] Not enough tables for night `{night}`, increasing by one...')
                    extra_tables += 1
                    print(f'[WARN] Not enough tables for night `{night}`, increasing by one...')

            for t in tables:
                t.night = night

            all_tables.extend(tables)

        if self.verbose:
            print(f'{len(all_tables)} total tables, {sum([t.n for t in all_tables])/len(all_tables)} per table')

        # We have a list of tables, arranged like this
        # [NIGHT A] [BOTH NIGHTS] [NIGHT B]
        #                ^
        # We split down the middle, and this is how we allocate either to night A or B.
        n_tables_per_formal = len(all_tables) / self.num_nights
        # If we have an uneven split, we flip a coin
        if n_tables_per_formal % 1 != 0:
            if np.random.random() < 0.5:
                n_tables_per_formal += 0.5
            else:
                n_tables_per_formal -= 0.5

        night_a_tables = all_tables[:int(n_tables_per_formal)]
        night_b_tables = all_tables[int(n_tables_per_formal):]

        # Make sure that not more than 50% of groups want to go to ONLY A or B
        # If this is the case, we can't allocate using this approach
        # We would need to bias the split
        for table in night_a_tables:
            assert table.night in ['a', 'both']
            for g in table.groups:
                assert g.dateprefs in ['a', 'both']

        for table in night_b_tables:
            assert table.night in ['c', 'both']
            for g in table.groups:
                assert g.dateprefs in ['c', 'both']

        # Randomly select tables for each night
        night_a_selection = np.random.choice(night_a_tables, self.num_tables, replace=False)
        night_b_selection = np.random.choice(night_b_tables, self.num_tables, replace=False)
        
        if self.verbose:
            print(f"Chose {sum([t.n for t in night_a_selection])} for night a:", " ".join(map(repr, night_a_selection)))
            print(f"Chose {sum([t.n for t in night_b_selection])} for night b:", " ".join(map(repr, night_b_selection)))

        # This assignment might not be full (some tables might still have gap). We need to fill in the gaps
        # This is done by randomly sorting the unsuccessful groups, and then greedily selecting them 
        # This does give a SLIGHT preference to smaller groups, but this is only where larger groups would absolutely not fit
        for night_selection, night_tables in zip([night_a_selection, night_b_selection], [night_a_tables, night_b_tables]):
            rejected_tables = [t for t in night_tables if t not in night_selection]
            
            num_spaces = sum([t.spaces for t in night_selection])

            if self.verbose:
                print(f"{len(rejected_tables)} tables were rejected of {sum([t.n for t in rejected_tables])} people, with {num_spaces} spaces, filling in")
            rejected_groups = [g for t in rejected_tables for g in t.groups]

            # Attempt to fit groups in a random order
            rejected_groups = sorted(rejected_groups, key=lambda x: np.random.random())
            for group in rejected_groups:
                try:
                    self.fit_group_into_tables(group, night_selection)
                except NotEnoughTables:
                    # This isn't an issue, we can do the next group
                    pass

            num_spaces = sum([t.spaces for t in night_selection])
            if self.verbose:
                print(f"After filling, we have {num_spaces} spaces left")
                print(" ".join(map(repr, night_selection)))

        # Final assignment :)
        return [night_a_selection.tolist(), night_b_selection.tolist()]
            

if __name__ == '__main__':
    assignment = Assignment(table_size=8, num_tables=10, num_nights=2)

    groups = generate_groups(100, seed=42)
    assignment = assignment.run(groups, assignment_seed=42)