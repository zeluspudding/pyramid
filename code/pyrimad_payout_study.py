# Find feasibility of a pyrimad referral system for getting people to mine monero
import random
from  ete3 import Tree, TreeStyle

hashes_per_minute = 2843/2
mining_hours_per_day = 8
hashes_per_day = hashes_per_minute * 60 * mining_hours_per_day
mining_days_per_month = 5 * 4

hashes_per_month = hashes_per_day * mining_days_per_month

global_difficulty = 30214170692
block_reward = 6.51
our_cut_after_coinhive = 0.7

mined_XMR_per_month = hashes_per_month/global_difficulty * block_reward * our_cut_after_coinhive
dollars_per_XMR = 89.23
dollars_per_month = mined_XMR_per_month * dollars_per_XMR

#%% Make random tree
def make_tree(max_children, depth, level=0, tree=Tree(), children=[]):
    def make_node(parent, level, index):
        child_name = str(level) + '_' + str(index)
        child = parent.add_child(name = child_name)
        child.add_features(level = level,
                           m_mined = dollars_per_month,
                           m_in = 0,
                           pre_total =  0,
                           m_out = 0,
                           total = 0)
        return child

    # Make root children
    if not tree.children:
        for i, child in enumerate(range(random.randint(1, max_children+2))):
            node = make_node(tree, level, i)
            children.append(node)
        return make_tree(max_children, depth-1, level+1, tree, children)
    elif depth == 0:
        return tree
    # Add children to children
    else:
        new_children = []
        i = 0
        for child in children:
            # Add more children
            for node in range(random.randint(0, max_children)):
                new_node = make_node(child, level, i)
                new_children.append(new_node)
                i += 1
        return make_tree(max_children, depth-1, level+1, tree, new_children)

#%% Make random pyramid
height = 5
max_individual_referrals = 20 # max local width
t = make_tree(max_individual_referrals, height)

#%% Redistribute earnings upstream
miner_cut = 0.7 #percent
def redistribute_earnings(tree, level):
    # Initialize leaf nodes
    if level == height - 1: # handle zero based indexing
        for node in tree.search_nodes(level=level):
            node.pre_total = node.m_mined
            node.m_out = node.pre_total * (1 - miner_cut)
            node.total = node.pre_total * miner_cut
        return redistribute_earnings(tree, level-1)
    elif level < 0:
        return tree
    else:
        for node in tree.search_nodes(level=level):
            node.m_in = sum([child.m_out for child in node.children])
            node.pre_total = node.m_mined + node.m_in
            node.m_out = node.pre_total * (1 - miner_cut)
            node.total = node.pre_total * miner_cut
        return redistribute_earnings(tree, level-1)

t = redistribute_earnings(t, height - 1)

for level in range(height):
    earnings = [node.total for node in t.search_nodes(level=level)]
    ma = max(earnings)
    mi = min(earnings)
    print('Level: %s, Max Month Pay: %s, Min Month Pay: %s' %(level,ma,mi))
