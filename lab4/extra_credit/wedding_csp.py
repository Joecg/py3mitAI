#!/usr/bin/env python
"""
Implementation of a wedding seating csp problem.
"""
import sys
import lab4_wedding
import time
from csp_expanded import CSP, Variable, BinaryConstraint, solve_csp_problem
from csp_expanded import basic_constraint_checker, GroupConstraint

fh = open('/Users/joegriffin/Downloads/Name Card guest list - Sheet1.csv', 'r')
line = fh.readline()
guests = []
Coghlans = []

tablesize = 10
while line:
    entries = line.split(',')
    if entries[2] == 'declined':
        line = fh.readline()
        continue
    new_guest = ' '.join((entries[1], entries[0]))
    guests.append(new_guest)
    if entries[3].lower() == 'coghlan':
        Coghlans.append(new_guest)
    line = fh.readline()

table_bases = ['Joe Griffin', 'Lisa Griffin', 'Gloria Griffin',
               'AnnMarie Patterson', ]

couples = [('John Celentano', 'Jenny Celentano'),
           ('Dan Misko', 'Katie Griffin'),
           ('Cecelia Dobbins', 'Katie Griffin'),
           ('Laurie Eaton', 'Paul Vickers'),
           ('Keiran Fitzpatrick', 'Jenny Celentano'),
           ('Kaye Fitzpatrick', 'Keiran Fitzpatrick'),
           ('Lisa Griffin', 'John Griffin'),
           ('Gloria Griffin', 'Fr. John Love'),
           ('Paul Griffin', 'Gloria Griffin'),
           ('Paul III Griffin', 'Paul Griffin'),
           ('Marsha Griffin', 'Paul Griffin'),
           ('David Griffin', 'Anthony Griffin'),
           ('Edita Griffin', 'Anthony Griffin'),
           ('Matthew Griffin', 'Heather Griffin'),
           ('Heather Griffin', 'James Griffin'),
           ('Judy Griffin', 'Kelli Vella'),
           ('Carol Johnston', 'Kaye Fitzpatrick'),
           ('Tom Johnston', 'Carol Johnston'),
           ('Scarlett Koller', 'Joe Griffin'),
           ('Sam Lewis', 'Megan Foy'),
           ('Tom Markin', 'LeAnn Markin'),
           ('Gene Jr. Mewborn', 'Brittany Snell'),
           ('Gene Sr. Mewborn', 'April Mewborn'),
           ('Matt Mora', 'Tim Patterson'),
           ('Eliza Mora', 'Jo Patterson'),
           ('Debra Northart', 'Nick Patterson'),
           ('Susannah Northart', 'Debra Northart'),
           ('Gwen Patterson', 'Kirk Patterson'),
           ('Tyler Patterson', 'AnnMarie Patterson'),
           ('Tim Patterson', 'Jo Patterson'),
           ('Jo Patterson', 'Nickie Patterson'),
           ('Kirk Patterson', 'Lavona Patterson'),
           ('Nick Patterson', 'Nanette Patterson'),
           ('Kennedy Polamalu', 'Diane Polamalu'),
           ('Theo Raines', 'Lucia Raines'),
           ('Genevieve Raines', 'Brian Raines'),
           ('Brian Raines', 'Theo Raines'),
           ('Lucia Raines', 'Lorenzo Raines'),
           ('Deacon Sanders', 'Fr. John Love'),
           ('Mrs. Sanders', 'Deacon Sanders'),
           ('Brittany Snell', 'Jonathon Griffin'),
           ('Jon Vella', 'Kelli Vella'),
           ('Emilie Vella', 'Kelli Vella'),
           ('Julie Vickers', 'Paul Vickers'),
           ('Anne Walsh', 'Thomas Walsh'),
           ('Thomas Walsh', 'Andrew Walsh'),
           ('Nathanael Walsh', 'Andrew Walsh'),
           ('Ruben Aguiar', 'Juliette Griffin'),
           ('Paul IV Griffin', 'Joe Griffin'),
           ('Jonathon Griffin', 'Joe Griffin'),
           ('Gregory Griffin', 'Jonathon Griffin'),
           ('David Jr. Griffin', 'Megan Griffin'),
           ('Peter Griffin', 'James Griffin'),
           ('David Jr. Griffin', 'Joe Griffin'),
           ('Michael D Sweet', 'Tyler Patterson'),
           ('Teddy Chappell', 'Tyler Patterson'),
           ('Lizzie Griffin', 'AnnMarie Patterson'),
           ('Laurie Eaton', 'Mike Coghlan'),
           ('Lisa Griffin', 'Carol Patterson'),
           ('John Griffin', 'John Celentano'),
           ('William Griffin', 'Peter Griffin')]
discords = [('Gwen Patterson', 'Debra Northart'),
            #('Nanette Patterson', 'Debra Northart'),
            ('Debra Northart', 'Katie Griffin'),
            ('Debra Northart', 'Lisa Griffin'),
            ('Debra Northart', 'Kristene Griffin'),
            ('Debra Northart', 'Paul Griffin'),
            ('Debra Northart', 'Matthew Griffin'),
            ('Debra Northart', 'Judy Griffin'),
            ('Debra Northart', 'Diane Polamalu'),
            ('Debra Northart', 'Gene Sr. Mewborn'),
            ('Debra Northart', 'Brian Raines'),
            ('Diane Polamalu', 'Nanette Patterson'),
            ('Diane Polamalu', 'Lavona Patterson'),
            ('Diane Polamalu', 'Jo Patterson'),
            ('Diane Polamalu', 'Nanette Patterson'),
            ('Diane Polamalu', 'AnnMarie Patterson'),
            ('Kelli Vella', 'Joe Griffin'),
            ('Anne Walsh', 'Joe Griffin'),
            ('Peter Griffin', 'Joe Griffin'),
            ('Diane Polamalu', 'Joe Griffin'),
            ('AnnMarie Patterson', 'Joe Griffin'),
            ('Brian Raines', 'Joe Griffin')]
tables = list('0123456789A')


def couples_together(val_a, val_b, name_a, name_b):
    return val_a == val_b

def discords_apart(val_a, val_b, name_a, name_b):
    return val_a != val_b

def table_size_check(vals, names):
##    for table in set(vals):
##        if table is None: continue
##        if (vals.count(table) > tablesize):
##            return False
    return True

def wedding_csp_problem():
    constraints = []
    rotating_tables = tables
    tables_idx = 0
    variables = []
    for guest_idx in range(len(guests)):
        rotating_tables = (tables[tables_idx:] +
                           tables[:tables_idx])
        ########## Decide whether to rotate tables or not
        variables.append(Variable(guests[guest_idx], rotating_tables))
        ##########
        tables_idx = (tables_idx + 1) % len(tables)

    for coghlan_idx in range(len(Coghlans) - 1):
        constraints.append(BinaryConstraint(Coghlans[coghlan_idx],
                                            Coghlans[coghlan_idx + 1],
                                            couples_together,
                                            "Coghlans must be seated"+
                                            " together"))
        constraints.append(BinaryConstraint(Coghlans[coghlan_idx + 1],
                                            Coghlans[coghlan_idx],
                                            couples_together,
                                            "Coghlans must be seated"+
                                            " together"))

    for pair in couples:
        constraints.append(BinaryConstraint(pair[0], pair[1],
                                            couples_together,
                                            "Members of a pair must"+
                                            " be seated together"))
        constraints.append(BinaryConstraint(pair[1], pair[0],
                                            couples_together,
                                            "Members of a pair must"+
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

    constraints.append(GroupConstraint([], table_size_check,
                                       "No table can be too large."))

    return CSP(constraints, variables)

checker = lab4_wedding.forward_checking_prop_singleton
print('Searching for solution.  Please wait...')
start = time.time()
solution = solve_csp_problem(wedding_csp_problem, checker, verbosity = 0)
print(solution[0])
solution[0].rev_print()
print(time.time() - start)
