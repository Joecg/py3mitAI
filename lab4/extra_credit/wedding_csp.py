#!/usr/bin/env python
"""
Implementation of a wedding seating csp problem.
"""
import sys
import lab4_expanded
import time
from csp_expanded import CSP, Variable, BinaryConstraint, solve_csp_problem
from csp_expanded import basic_constraint_checker, GroupConstraint

guests = ('Joe', 'Scarlett', 'DaveJr', 'Megan',
          'Matt', 'Heather', 'Lizzie', 'Grace')
tables = list('123')
tablesize = 4

def couples_together(val_a, val_b, name_a, name_b):
    return val_a == val_b

def discords_apart(val_a, val_b, name_a, name_b):
    return val_a != val_b

def table_size_check(vals, names):
    return len(set(vals)) != 1

def wedding_csp_problem():
    constraints = []
    rotating_tables = tables
    tables_idx = 0
    variables = []
    for guest_idx in range(len(guests)):
        rotating_tables = (tables[tables_idx:] +
                           tables[:tables_idx])
        variables.append(Variable(guests[guest_idx], rotating_tables))
        tables_idx = (tables_idx + 1) % len(tables)

    couples = (guests[:2], guests[2:4], guests[4:6],
               ('Matt', 'Scarlett'))
    discords = (('Lizzie', 'Grace'), ('Heather', 'DaveJr'),
                ('Grace', 'Megan'))
    
    for pair in couples:
        constraints.append(BinaryConstraint(pair[0], pair[1],
                                            couples_together,
                                            "Members of a couple must"+
                                            " be seated together"))
        constraints.append(BinaryConstraint(pair[1], pair[0],
                                            couples_together,
                                            "Members of a couple must"+
                                            " be seated together"))

    for pair in discords:
        constraints.append(BinaryConstraint(pair[0], pair[1],
                                            discords_apart,
                                            "Discordant pairs must "+
                                            "not be seated together"))
        constraints.append(BinaryConstraint(pair[1], pair[0],
                                            discords_apart,
                                            "Discordant pairs must "+
                                            "not be seated together"))

    for oversize_set in lab4_expanded.itertools.combinations(guests,
                                                             tablesize + 1):
        constraints.append(GroupConstraint(oversize_set, table_size_check,
                                           "One table cannot seat more " +
                                           "than " + str(tablesize) +
                                           " people"))

    return CSP(constraints, variables)

checker = lab4_expanded.forward_checking_prop_singleton
start = time.time()
solution = solve_csp_problem(wedding_csp_problem, checker, verbosity = 0)
print(solution[0])
print(time.time() - start)
