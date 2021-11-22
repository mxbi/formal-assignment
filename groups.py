import numpy as np
import uuid

# np.random.seed(4200)

class Group:
    def __init__(self, users, dateprefs, gid=None):
        self.users = users
        self.n = len(self.users)
        self.dateprefs = dateprefs
        self.gid = gid or uuid.uuid4()

    def __repr__(self):
        return f"G[{self.n},{self.dateprefs}]{self.users}"

def generate_groups(n_groups, size_dist=[0.25, 0.25, 0.25, 0.25], seed=42):
    np.random.seed(seed)
    groups = []

    for i in range(n_groups):
        num_users = np.random.choice(np.arange(len(size_dist))+1, p=size_dist)
        users = [uuid.uuid4() for _ in range(num_users)]

        dateprefs = np.random.choice(["a", "both", "c"], p=[0.33, 0.34, 0.33])
        # dateprefs = np.random.choice(["a", "both", "c"], p=[0, 1, 0])
        groups.append(Group(users, dateprefs))

    print(f"Generated {len(groups)} groups of total {sum([g.n for g in groups])} people")

    return groups

if __name__ == '__main__':
    generate_groups(100)