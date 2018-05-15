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
                if not c.check(state, x, y): Y.reduce_domain(y)
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
            var_possibilities = [[False] * len(dom) for dom in var_dom]
            for var_combo in itertools.product(*var_dom):
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
##from moose_csp import moose_csp_problem
##from map_coloring_csp import map_coloring_csp_problem

def csp_solver_tree(problem, checker):
    problem_func = globals()[problem]
    checker_func = globals()[checker]
    answer, search_tree = problem_func().solve(checker_func)
    return search_tree.tree_to_string(search_tree)
