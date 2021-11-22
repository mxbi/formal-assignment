from itertools import chain, combinations
import copy
import random

from assignment import Table

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

class SeatingOptimizer:
    def __init__(self, tables):
        self.tables = tables

        self.all_groups = {}
        for table in self.tables:
            for group in table.groups:
                self.all_groups[group.gid] = group

        self.normalise_seating_prefs()

        print(self.score(self.tables))

    def score(self, tables):
        n = 0
        for table in tables:
            table_gids = set([g.gid for g in table.groups])
            for group in table.groups:
                    n += len(group.gid_prefs.intersection(table_gids))
        return n

    def normalise_seating_prefs(self):
        # Get mapping from uid -> gid
        user_group_map = {}
        for group in self.all_groups.values():
            for user in group.users:
                assert user not in user_group_map # user can't have two groups
                user_group_map[user] = group.gid

        total_prefs = 0

        # Tag each group with the other gids it wants to be next to
        for group in self.all_groups.values():
            gid_prefs = set()
            for pref in group.seating_prefs:
                if pref in user_group_map:
                    print(group, pref)
                    gid_prefs.add(user_group_map[pref])
                else:
                    print(f'Warn: pref {pref} not visible, ignoring...')

            group.gid_prefs = gid_prefs
            total_prefs += len(gid_prefs)

        print(f'Loaded {total_prefs} prefs')
        self.max_score = total_prefs

    def one_swap(self, temperature):
        for table_i, table_src in enumerate(self.tables):
            for group in table_src.groups:
                n = group.n

                for table_j, table_dst in enumerate(self.tables):

                    if table_i == table_j:
                        continue

                    base_score = self.score([table_src, table_dst])

                    for other_groups in powerset(table_dst.groups):
                        rep_n = sum([g.n for g in other_groups])

                        if rep_n == n:
                            # Potential swap here!

                            # new_tables = [copy.copy(t) for t in tables]
                            # print(table_src.n, table_dst.n)
                            new_table_src_groups = [e for e in table_src.groups if e.gid != group.gid]
                            new_table_src_groups.extend(other_groups)

                            new_table_dst_groups = [g for g in table_dst.groups if g not in other_groups]
                            new_table_dst_groups.append(group)
                            
                            new_table_src = Table(table_src.size)
                            new_table_src.groups = new_table_src_groups

                            new_table_dst = Table(table_dst.size)
                            new_table_dst.groups = new_table_dst_groups

                            assert new_table_src.n == table_src.n
                            assert new_table_dst.n == table_dst.n

                            # print(len(table_src.groups), len(table_dst.groups), n, rep_n, new_table_src.n, new_table_dst.n)

                            new_score = self.score([new_table_src, new_table_dst])
                            if new_score > base_score:
                                print('found swap!', base_score, new_score)
                                self.tables[table_i] = new_table_src
                                self.tables[table_j] = new_table_dst
                                base_score = new_score

                                print('new overall score:', self.score(self.tables))
                                return

                            elif random.random() < temperature and new_score == base_score:
                                # print('annealing')
                                self.tables[table_i] = new_table_src
                                self.tables[table_j] = new_table_dst
                                # # base_score = new_score
                                # print('new overall score:', self.score(self.tables))

                                return

    def optimize(self):
        for a in range(800):
            temperature = max(0, 0.3 - a*0.00025)
            # print('temperature', temperature)
            self.one_swap(temperature)
