#!/usr/bin/env python
"""
A General Constraint Satisfaction Problem Solver
@author: yks
"""
class Variable:
    """
    Representation of a discrete variable with a finite domain.
    As used in our VD table.
    A variable can be in the assigned state, in which v.is_assigned()
    will return true.
    """
    def __init__(self, name, domain, value=None):
        self._name = name
        self._domain = domain[:]
        self._value = value

    def copy(self):
        return Variable(self._name, self._domain, self._value)

    def get_name(self):
        return self._name

    def reduce_domain(self, value):
        self._domain.remove(value)

    def domain_size(self):
        return len(self._domain)

    def get_domain(self):
        return self._domain[:]

    def is_assigned(self):
        return not (self._value is None)

    def get_assigned_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def __str__(self):
        buf = "%s(%s)" %(self._name, self._domain)
        if self._value is not None:
            buf += ": %s" %(self._value)
        return buf

class BinaryConstraint:
    """
    Representation of a binary-constraint on two variables variable i and
    variable j.
    """
    def __init__(self, var_i_name, var_j_name, check_func, description=None):
        """
        * var_i_name, var_j_name are the names of the variables.
        * check_func is a function that takes four arguments value_i and
        value_j. var_name_i, var_name_j
        Example. lambda i,j,name_i,name_j: i < j and returns true if
        the values passes the constraint, false otherwise.
        * description is a string descriptor of the constraint (helpful
        to determine what constraints triggered a search failure.
        """
        self.var_i_name = var_i_name
        self.var_j_name = var_j_name
        self.check_func = check_func
        self.description = description

    def get_variable_i_name(self):
        return self.var_i_name

    def get_variable_j_name(self):
        return self.var_j_name

    def check(self, state, value_i=None, value_j=None):
        """
        state is the csp state and should be an instance of
        CSPState.
        value_i and value_j are the values assigned to variable
        i and j respectively.   If they are not provided, the they are
        fetched from the state by looking up variable_i and variable_j's
        names.
        """
        variable_i = state.get_variable_by_name(self.var_i_name)
        if value_i is None and not variable_i is None:
            value_i = variable_i.get_assigned_value()

        variable_j = state.get_variable_by_name(self.var_j_name)
        if value_j is None and not variable_j is None:
            value_j = variable_j.get_assigned_value()

        if not value_i is None and not value_j is None:
            return self.check_func(value_i, value_j,
                                   self.var_i_name, self.var_j_name)
        else:
            raise Exception("neither value_i nor value_j are set")

        # if values of i or j are not set, we really can't check
        # this constraint.  So the check passes.
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        name = "BinaryConstraint(%s, %s)" %(self.get_variable_i_name(),
                                            self.get_variable_j_name())
        if self.description is not None:
            name += " : %s" %(self.description)
        return name

class GroupConstraint:
    """
    Representation of a group-constraint on several variables.
    """
    def __init__(self, var_names, check_func, description=None):
        """
        * var_names are the names of the variables.
        * check_func is a function that takes two arguments: values and
        variables
        Example. lambda vars, vals: length(vars) < 10 and returns true if
        the values passes the constraint, false otherwise.
        * description is a string descriptor of the constraint (helpful
        to determine what constraints triggered a search failure.
        """
        self.check_func = check_func
        self.description = description
        self.var_names = var_names

    def get_variable_name_by_index(self, index):
        return self.var_names[index]

    def get_variable_names(self):
        return self.var_names[:]

    def check(self, state, values = (None,)):
        """
        state is the csp state and should be an instance of
        CSPState.
        values are the values assigned to the constrained variables.
        If they are not provided, the they are
        fetched from the state by looking up variable
        names from the attribute list.
        """
        populated_vals = [None] * len(self.var_names)
        if values == (None,):
            arg_values = (None,) * len(self.var_names)
        else:
            arg_values = values
        for idx in range(len(self.var_names)):
            var_i = state.get_variable_by_name(self.var_names[idx])
            if arg_values[idx] is None and var_i is not None:
                populated_vals[idx] = var_i.get_assigned_value()
            else:
                populated_vals[idx] = arg_values[idx]
        return self.check_func(populated_vals, self.get_variable_names())

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        name = "GroupConstraint(%s)" % (self.var_names,)
        if self.description is not None:
            name += " : %s" %(self.description)
        return name

class CSPState:
    """
    Representation of a single state in the CSP search tree.  One can
    think of this as the encapsulation of the Variable-domain (VD) table.
    """
    def __init__(self,
                 constraint_map,
                 variable_map,
                 variable_order,
                 variable_index):
        """
        constraint_map - a dictionary of variable names to
                         lists of associated constraints
        variable_map - a dictionary of variable names to
                       variable objects
        variable_order - the ordering in which variables are assigned
                       values are the names of variables
        variable_index - the position into the variable_order in which
                       we are currently making an assignment.
        """
        self.constraint_map = constraint_map
        self.variable_map = variable_map
        self.variable_order = variable_order
        self.variable_index = variable_index

    def copy(self):
        """
        Make a complete deep copy of this state; this should be
        done so that modifications to the VD table is only transmitted
        to children but not siblings (in the search tree).
        """
        # make a deep copy of the variable map.
        new_variable_map = {}
        for var_name, variable in self.variable_map.items():
            new_variable_map[var_name] = variable.copy()
        new_state = CSPState(self.constraint_map,
                             new_variable_map,
                             self.variable_order,
                             self.variable_index)
        return new_state

    def get_constraints_by_name(self, variable_name):
        """
        List only constraints associated with variable_name
        (where variable_name is variable_i in the constraint)
        """
        constraints = []
        for key, val in self.constraint_map.items():
            for constraint in val:
                if type(constraint) == BinaryConstraint:
                    if key[0] == variable_name:
                        constraints.append(constraint)
                elif type(constraint) == GroupConstraint:
                    if variable_name in key:
                        constraints.append(constraint)
        return constraints

    def get_all_constraints(self):
        """
        List all the constraints in this problem
        """
        constraints = []
        for key, val in self.constraint_map.items():
            constraints += val
        return constraints

    def get_all_variables(self):
        """
        List all the variable objects in this problem
        """
        variables = []
        for name in self.variable_order:
            variables.append(self.variable_map[name])
        return variables

    def get_current_variable_name(self):
        """
        Get the name of the variable currently being assigned.
        This function will returns None when in the root/initial state.
        """
        if self.variable_index >= 0:
            return self.get_variable_by_index(self.variable_index).get_name()
        else:
            return None

    def get_current_variable(self):
        """
        Get variable (object) currently being assigned.
        """
        if self.variable_index >= 0:
            return self.get_variable_by_index(self.variable_index)
        else:
            return None

    def set_variable_by_index(self, variable_index, variable_value):
        """
        assign variable (given index) the variable_value
        """
        variable = self.get_variable_by_index(variable_index)
        if variable is not None:
            variable.set_value(variable_value)
            self.variable_index = variable_index
        # WEDDING ONLY: If table is now full, remove table from all domains
        is_cnt = 0
        for var in self.get_all_variables():
            if var.is_assigned():
                if var.get_assigned_value() == variable_value:
                    is_cnt += 1
        if is_cnt >= 10:
            for var in self.get_all_variables():
                if variable_value in var.get_domain():
                    var.reduce_domain(variable_value)

    def get_variable_by_index(self, index):
        """
        fetch the index(th) variable object
        """
        if index >= 0 and index < len(self.variable_order):
            return self.variable_map[self.variable_order[index]]
        return None

    def get_variable_by_name(self, name):
        """
        fetch a variable object by the variable name
        """
        if name in self.variable_map:
            return self.variable_map[name]
        return None

    def is_solution(self):
        """
        Check if this csp state is a solution.
        Note we assume that constraint checking has been done
        on this state.  This merely checks if all the variables
        have an assignment
        """
        for var in self.get_all_variables():
            if not var.is_assigned():
                return False
        return True

    def solution(self):
        """
        return the set of tuples (var-name, var-value) for
        all the assigned variables
        """
        assignment = []
        for varname in self.variable_order:
            vnode = self.get_variable_by_name(varname)
            if vnode.is_assigned():
                assignment.append((vnode.get_name(),
				   vnode.get_assigned_value()))
        return assignment

    def __str__(self):
        return self.vd_table()

    def vd_table(self):
        """
        Output the vd table as a string for debugging.
        """
        buf = ""
        for var_name in self.variable_order:
            var = self.variable_map[var_name]
            if var.is_assigned():
                buf += "%s | %s*\n" %(var.get_name(),
				      var.get_assigned_value())
            else:
                buf += "%s | %s\n" %(var.get_name(),
                                     var.get_domain())
        return buf

    def rev_print(self):
        value_dict = dict()
        for variable in self.get_all_variables():
            if not variable.is_assigned():
                continue
            value = variable.get_assigned_value()
            if value in value_dict:
                value_dict[value].append(variable.get_name())
            else:
                value_dict[value] = [variable.get_name()]
        for value in value_dict:
            print(value,':',value_dict[value])


def basic_constraint_checker(state, verbosity = 0):
    """
    Basic constraint checker used to check at every assignment
    whether the assignment passes all the constraints
    """
    constraints = state.get_all_constraints()
    for constraint in constraints:
        if verbosity > 2: print(constraint)
        if type(constraint) == BinaryConstraint:
            var_i = state.get_variable_by_name(constraint.get_variable_i_name())
            var_j = state.get_variable_by_name(constraint.get_variable_j_name())
            if (not var_i.is_assigned()) or (not var_j.is_assigned()):
                continue
        elif type(constraint) == GroupConstraint:
            any_continue = False
            for var_name in constraint.get_variable_names():
                var_obj = state.get_variable_by_name(var_name)
                if not var_obj.is_assigned():
                    any_continue = True
                    continue
            if any_continue: continue
        if verbosity > 3: print('Evaluation')
        if not constraint.check(state):
            if verbosity > 0:
                print("CONSTRAINT-FAILS: %s" % (constraint))
            return False
    return True

def count_extract(var_count_tuple):
    return var_count_tuple[1]

class CSP:
    """
    Top-level wrapper object that encapsulates all the
    variables and constraints of a CSP problem
    """
    def __init__(self, constraints, variables):
        # Step 1: generate a constraint map, a mapping of pairs of
        # variable names to defined constraints on that pair.
        self.constraint_map = {}
        for constraint in constraints:
            if type(constraint) == BinaryConstraint:
                i = constraint.get_variable_i_name()
                j = constraint.get_variable_j_name()
                tup = (i, j)
                if tup not in self.constraint_map:
                    lst = []
                    self.constraint_map[tup] = lst
                else:
                    lst = self.constraint_map[tup]
                lst.append(constraint)
            elif type(constraint) == GroupConstraint:
                tup = tuple(constraint.get_variable_names())
                if tup not in self.constraint_map:
                    self.constraint_map[tup] = []
                self.constraint_map[tup].append(constraint)
            else:
                raise NotImplementedError

        # Step 2: generate the variable map,
        # and sort variables from most constrained to least constrained
        self.variable_map = {}
        variable_order = []
        for var in variables:
            var_name = var.get_name()
            self.variable_map[var_name] = var
            constraint_count = 0
            for connection in self.constraint_map:
                if var_name in connection:
                    constraint_count += len(self.constraint_map[connection])
            variable_order.append((var_name,
                                   constraint_count))
        self.variable_order = [var_name for (var_name, count) in
                               sorted(variable_order,
                                      key = count_extract,
                                      reverse = True)]


    def initial_state(self):
        """
        Returns the starting state of the CSP with no variables assigned.
        """
        return CSPState(self.constraint_map, self.variable_map,
                        self.variable_order, -1)

    def solve(self,
              constraint_checker=basic_constraint_checker,
              verbosity = 0):
        """
        Perform a depth-first search with backtracking to solve
        This CSP problem.

        The constraint_checker is a function that performs constraint-checking
        propagation on a CSPState.  By default the checker does
        basic constraint checking (without propagation).

        returns the solution state, and the search tree.
        """
        initial_state = self.initial_state()
        search_root = Node("ROOT", initial_state)
        agenda = [search_root]

        step = 0
        while len(agenda) > 0:
            try:
                cur_node = agenda.pop(0)
                state = cur_node.value
                cur_node.step = step

                if verbosity > 0:
                    print("-"*20)
                    print("%d. EXAMINING:\n%s" %(step, state.vd_table()))

                if not constraint_checker(state, verbosity):
                    if verbosity > 0:
                        print("%d. FAIL:\n%s" %(step, state.vd_table()))
                    cur_node.status = Node.FAILED
                    step += 1
                    continue

                if state.is_solution():
                    cur_node.status = Node.SOLUTION
                    if verbosity > 0:
                        print("%d. SOLUTION:\n%s" %(step, state.vd_table()))
                    return state, search_root

                cur_node.status = Node.CONTINUE
                if verbosity > 0:
                    print("%d. CONTINUE:\n%s" %(step, state.vd_table()))


                next_variable_index = state.variable_index + 1
                next_variable = state.get_variable_by_index(next_variable_index)
                values = next_variable.get_domain()

                children = []
                for value in values:
                    new_state = state.copy()
                    new_state.set_variable_by_index(next_variable_index, value)
                    children.append(Node(str(value), new_state))

                cur_node.add_children(children)
                agenda = children + agenda
                step += 1
            except KeyboardInterrupt:
                print("-"*20)
                print("%d. EXAMINING:\n%s" %(step, state.vd_table()))
                input('Ready...')
                print('Running. Please wait...')

        # fail! no solution
        return None, search_root

class Node:
    """
    A tree node that csp.solve() uses/returns that keeps track of the CSP
    search tree.
    """
    UNEXTENDED = "u"
    FAILED = "f"
    CONTINUE = "c"
    SOLUTION = "*"

    def __init__(self, label, value):
        self.label = label
        self.status = Node.UNEXTENDED
        self.value = value
        self.step = '-'
        self.children = []

    def add_children(self, children):
        self.children += children

    def __str__(self):
        return self.label

    def tree_to_string(self, node, depth=0):
        pad = depth*"\t"
        current_var = node.value.get_current_variable_name()
        if current_var is not None:
            buf = "%s%s=%s(%s,%s)\n" %(pad,
                                       current_var,
                                       node.label,
                                       node.status,
                                       node.step)
        else:
            buf = "%s%s\n" %(pad, node.label)

        for child in node.children:
            buf += self.tree_to_string(child, depth+1)
        return buf


def simple_csp_problem():
    """
    Formulation of a simple CSP problem that attempts to find
    an assignment to 4 variables: A,B,C,D.  With the constraint that
    A < B < C < D.
    """
    variables = []
    domain = [1, 2, 3, 4]

    variables.append(Variable("A", domain))
    variables.append(Variable("B", domain))
    variables.append(Variable("C", domain))
    variables.append(Variable("D", domain))

    constraints = []

    def less_than(val_a, val_b, name_a=None, name_b=None):
        return val_a < val_b

    constraints.append(BinaryConstraint("A", "B", less_than, "A < B"))
    constraints.append(BinaryConstraint("B", "C", less_than, "B < C"))
    constraints.append(BinaryConstraint("C", "D", less_than, "C < D"))

    def not_equal(val_a, val_b, name_a=None, name_b=None):
        return val_a != val_b

    constraints.append(BinaryConstraint("A", "B", not_equal, "A != B"))
    constraints.append(BinaryConstraint("B", "C", not_equal, "B != C"))
    constraints.append(BinaryConstraint("C", "D", not_equal, "C != D"))
    constraints.append(BinaryConstraint("A", "D", not_equal, "A != D"))
    return CSP(constraints, variables)

def solve_csp_problem(problem, checker, verbosity = 0):
    """
    problem is a function that returns a CSP object that we can solve.
    checker is a function that implements the contraint checking.
    variable_order_cmp is a comparator for ordering the variables.
    """
    csp = problem()
    answer, search_tree = csp.solve(checker, verbosity = verbosity)

    if verbosity > 0:
        if answer is not None:
            print("ANSWER: %s" %(answer.solution()))
        else:
            print("NO SOLUTION FOUND")
        if search_tree is not None:
            print("TREE:\n")
            print(search_tree.tree_to_string(search_tree))

    return answer, search_tree

if __name__ == "__main__":
    checker = basic_constraint_checker
    #import lab4
    #fc_checker = lab4.forward_checking
    #fcps_checker = lab4.forward_checking_prop_singleton
    solve_csp_problem(simple_csp_problem, checker, verbosity = 1)
