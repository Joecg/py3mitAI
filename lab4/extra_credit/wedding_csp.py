#!/usr/bin/env python
"""
Implementation of a wedding seating csp problem.
"""
import sys
from csp_expanded import CSP, Variable, BinaryConstraint, solve_csp_problem
from csp_expanded import basic_constraint_checker, GroupConstraint

guests = ('Joe', 'Scarlett', 'DaveJr', 'Megan',
          'Matt', 'Heather', 'Lizzie', 'Grace')
tables = list('1234')

def couples_together(val_a, val_b, name_a, name_b):
    return val_a == val_b

def discords_apart(val_a, val_b, name_a, name_b):
    return val_a != val_b

def table_size(vals, names):
    for val in set(vals):
        if (vals.count(val) > 4) and not (val is None):
            return False
    return True

def wedding_csp_problem():
    constraints = []
    rotating_tables = tables
    tables_idx = 0
    variables = []
    for guest_idx in range(len(guests)):
        rotating_tables = (rotating_tables[tables_idx:] +
                           rotating_tables[:tables_idx])
        variables.append(Variable(guests[guest_idx], rotating_tables))
        tables_idx = (tables_idx + 1) % len(tables)

    couples = (guests[:2], guests[2:4], guests[4:6])
    discords = (('Lizzie', 'Grace'),('Heather', 'DaveJr'),
                ('Lizzie', 'Matt'))
    
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

    constraints.append(GroupConstraint(guests, table_size,
                                       "No table can seat " +
                                       "more than six guests"))

    return CSP(constraints, variables)

import lab4_expanded
checker = lab4_expanded.forward_checking
solve_csp_problem(wedding_csp_problem, checker, verbose=True)
