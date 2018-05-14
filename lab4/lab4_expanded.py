from classify import *
import math

##
## CSP portion of lab 4.
##
from csp_expanded import BinaryConstraint, CSP, CSPState, Variable,\
    basic_constraint_checker, solve_csp_problem, GroupConstraint
import itertools

# Implement basic forward checking on the CSPState see csp.py
def forward_checking(state, verbose=False):
    # Before running Forward checking we must ensure
    # that constraints are okay for this state.
    basic = basic_constraint_checker(state, verbose)
    if not basic: return False
    X = state.get_current_variable()
    if X is None: return True
    x = X.get_assigned_value()
    X_name = X.get_name()
    X_constraints = state.get_constraints_by_name(X_name)
    for c in X_constraints:
        if type(c) == BinaryConstraint:
            Y_name = c.get_variable_j_name()
            Y = state.get_variable_by_name(Y_name)
            Y_domain = Y.get_domain()
            for y in Y_domain:
                if not c.check(state, value_i = x, value_j = y):
                    Y.reduce_domain(y)
                if not Y.get_domain(): return False
        elif type(c) == GroupConstraint:
            # Keep vars ordered according to constraint indexing
            var_names = c.get_variable_names()
            var_cnt = len(var_names)
            var_dom = [state.get_variable_by_name(v_name).get_domain() if
                       (v_name != X_name) else [x] for v_name in var_names]
            # Any constraint-satisfying arrangement will do, so start with
            # all Falses for every value of every variable and gradually
            # replace them with Trues
            var_possiblities = [[False] * len(dom) for dom in var_dom]
            for var_combo in itertools.product(var_dom):
                if c.check(state, values = var_combo):
                    for var_idx in range(var_cnt):
                        val_idx = var_dom[var_idx].index(var_combo[var_idx])
                        var_possibilities[var_idx][val_idx] = True
            for var_idx in range(var_cnt):
                var_name = var_names[var_idx]
                var_obj = state.get_variable_by_name(var_name)
                for val_idx in range(len(var_possibilities[var_idx])):
                    if not var_possibilities[var_idx][val_idx]:
                        var_val = var_dom[var_idx][val_idx]
                        var_obj.reduce_domain(var_val)
                if not var_obj.get_domain(): return False
        else:
            raise NotImplementedError
    return True

# Now Implement forward checking + (constraint) propagation through
# singleton domains.
def forward_checking_prop_singleton(state, verbose=False):
    # Run forward checking first.
    if not forward_checking(state, verbose): return False
    queue = [v for v in state.get_all_variables()
             if v.domain_size() == 1]
    visited = []
    while queue:
        X = queue[0]
        X_name = X.get_name()
        visited.append(X)
        queue = queue[1:]
        X_constraints = state.get_constraints_by_name(X_name)
        for c in X_constraints:
            if type(c) == BinaryConstraint:
                Y_name = c.get_variable_i_name()
                j_Y = Y_name == X_name
                if Y_name == X_name: Y_name = c.get_variable_j_name()
                Y = state.get_variable_by_name(Y_name)
                Y_domain = Y.get_domain()
                for y in Y_domain:
                    if j_Y:
                        if not c.check(state,
                                       value_i = X.get_domain()[0],
                                       value_j = y):
                            Y.reduce_domain(y)
                    else:
                        if not c.check(state,
                                       value_i = y,
                                       value_j = X.get_domain()[0]):
                            Y.reduce_domain(y)
                    if not Y.get_domain(): return False
                if ((Y.domain_size() == 1) and
                    not (Y in queue) and
                    not (Y in visited)): queue.append(Y)
            else:
                raise NotImplementedError
    return True

## The code here are for the tester
## Do not change.
from moose_csp import moose_csp_problem
from map_coloring_csp import map_coloring_csp_problem

def csp_solver_tree(problem, checker):
    problem_func = globals()[problem]
    checker_func = globals()[checker]
    answer, search_tree = problem_func().solve(checker_func)
    return search_tree.tree_to_string(search_tree)

##
## CODE for the learning portion of lab 4.
##

### Data sets for the lab
## You will be classifying data from these sets.
senate_people = read_congress_data('S110.ord')
senate_votes = read_vote_data('S110desc.csv')

house_people = read_congress_data('H110.ord')
house_votes = read_vote_data('H110desc.csv')

last_senate_people = read_congress_data('S109.ord')
last_senate_votes = read_vote_data('S109desc.csv')


### Part 1: Nearest Neighbors
## An example of evaluating a nearest-neighbors classifier.
senate_group1, senate_group2 = crosscheck_groups(senate_people)
##evaluate(nearest_neighbors(hamming_distance, 1),
##         senate_group1, senate_group2, verbose=1)

## Write the euclidean_distance function.
## This function should take two lists of integers and
## find the Euclidean distance between them.
## See 'hamming_distance()' in classify.py for an example that
## computes Hamming distances.

def euclidean_distance(list1, list2):
    return sum([(i-j)**2 for (i, j) in zip(list1, list2)])**0.5

#Once you have implemented euclidean_distance, you can check the results:
##evaluate(nearest_neighbors(euclidean_distance, 1),
##         senate_group1, senate_group2)

## By changing the parameters you used, you can get a classifier factory that
## deals better with independents. Make a classifier that makes at most 3
## errors on the Senate.

my_classifier = nearest_neighbors(euclidean_distance, 5)
#evaluate(my_classifier, senate_group1, senate_group2, verbose=1)

### Part 2: ID Trees
#print(CongressIDTree(senate_people, senate_votes, homogeneous_disorder))

## Now write an information_disorder function to replace
## homogeneous_disorder, which should lead to simpler trees.

def information_disorder(yes, no):
    total_disorder = 0
    total_size = sum([len(group) for group in (yes, no)])
    for group in (yes, no):
        group_len = len(group)
        group_options = set(group)
        group_disorder = 0
        for option in group_options:
            option_ratio = group.count(option) / group_len
            group_disorder -= option_ratio * math.log(option_ratio, 2)
        total_disorder += group_disorder * group_len / total_size
    return total_disorder

#print(CongressIDTree(senate_people, senate_votes, information_disorder))
##evaluate(idtree_maker(senate_votes, homogeneous_disorder),
##         senate_group1, senate_group2)

## Now try it on the House of Representatives. However, do it over a data set
## that only includes the most recent n votes, to show that it is possible to
## classify politicians without ludicrous amounts of information.

def limited_house_classifier(house_people, house_votes, n, verbose = False):
    house_limited, house_limited_votes = limit_votes(house_people,
    house_votes, n)
    (house_limited_group1,
     house_limited_group2) = crosscheck_groups(house_limited)

    if verbose:
        print("ID tree for first group:")
        print(CongressIDTree(house_limited_group1, house_limited_votes,
                             information_disorder))
        print()
        print("ID tree for second group:")
        print(CongressIDTree(house_limited_group2, house_limited_votes,
                             information_disorder))
        print()

    return evaluate(idtree_maker(house_limited_votes, information_disorder),
                    house_limited_group1, house_limited_group2)


## Find a value of n that classifies at least 430 representatives correctly.
## Hint: It's not 10.
N_1 = 44
rep_classified = limited_house_classifier(house_people, house_votes, N_1)

## Find a value of n that classifies at least 90 senators correctly.
N_2 = 67
senator_classified = limited_house_classifier(senate_people,
                                              senate_votes, N_2)

## Now, find a value of n that classifies at least 95 of last year's
## senators correctly.
N_3 = 23
old_senator_classified = limited_house_classifier(last_senate_people,
                                                  last_senate_votes, N_3)


## The standard survey questions.
HOW_MANY_HOURS_THIS_PSET_TOOK = " "
WHAT_I_FOUND_INTERESTING = " "
WHAT_I_FOUND_BORING = " "


## This function is used by the tester, please don't modify it!
def eval_test(eval_fn, group1, group2, verbose = 0):
    """ Find eval_fn in globals(), then execute evaluate() on it """
    # Only allow known-safe eval_fn's
    if eval_fn in [ 'my_classifier' ]:
        return evaluate(globals()[eval_fn], group1, group2, verbose)
    else:
        raise Exception("Error: Tester tried to use an "+
                        "invalid evaluation function: '%s'" %
                        eval_fn)


