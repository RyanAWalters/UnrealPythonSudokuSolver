# SUDOKU SOLVER
# by USE OF PROPOGATION CONSTRAINTS, SEARCH, and BRUTE FORCE*
# starting code referenced from Norvig's website and algorithmic descriptions
#
# Brett Gardner, Matt Brandl, Ryan Walters

import time
import sys
import tkinter
import random

digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits

# Cross product of elements in A and elements in B.
def cross(R, C):
    return [r+c for r in R for c in C]
slots = cross(rows, cols)

# 9x9 grid split into 3v3 smaller grids.
# A1 => very top left grid slot, D6 => grid slot (4,6), etc.
unitlist = ([cross(rows, c) for c in cols] + [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])

# Use python dictionaries as glorified hashtables.
units = dict((s, [u for u in unitlist if s in u]) for s in slots) 
peers = dict((s, set( sum(units[s],[])) - set([s]) ) for s in slots)

"""
'Units' refers to potential other_numbers in the same row and column as a 'selected' number.
'Peers' refers to any of the 20 digits around a 'selected' number that
 cannot be the digit of the 'selected' number within a grid slot.
"""

# Attempt to solve a sequence of grids. 
# When showif is a integer of seconds, display puzzles that take longer than the specified int.
# When showif is None, don't display any puzzles.
def solve(grids, filename = 'solved.txt', name='', showif = 0.0):
    
    def time_solve(grid): 
        start = time.clock()
        values = sol(grid)
        t = time.clock()-start
        
        """ Display puzzles that take long enough """
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values:
                display(values)
                display_(filename, values) # for file output
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))
    
    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print ("Solved %d of %d %s puzzles (avg %.4f secs, max %.4f secs)."
               % (sum(results), N, name, sum(times)/N, max(times)))


# *Parses a text(of digits in this case)from the dictionaries in one-line format*
#
# Convert grid to a dictionary of possible values, {slot: digits}, or
# return False if a contradiction is detected.
# Every slot can be any digit 1-9; then assign values from the grid.
def parse_grid(grid):
    values = dict((s, digits) for s in slots)
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False # fail if d cant be assigned to slot s
    return values

# Convert grid into a dictionary of {slot: char} with '0' or '.' for empty slots.
def grid_values(grid):
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(slots, chars))

""" Propagation Constraints (read Norvig)"""
# Returns updated values from propagation constraint, unless a contradiction
# is found (i.e. cant assign a 4 in A2 if there's a 4 in A1)
def assign(values, s, d):
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

# Eliminate possible values for a grid slot, works in tangent with assign()
# so that we eliminate all digits except for the one we need
def eliminate(values, s, d):
    if d not in values[s]:
        return values
    
    values[s] = values[s].replace(d,'')

    # if a slot can have only 1 value d, then that value is eliminated
    # from its peers[]
    if len(values[s]) == 0:
        return False # fail -> value can have no spots
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False 

    # if a unit is reduced to only one valid place for value d, put it there        
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False # fail -> no place to put d.
        elif len(dplaces) == 1:
            if not assign(values, dplaces[0], d):
                return False
            
    return values
""" /Propogation Constraints """



# solved SP to display through the CLI. from Norvig.
def display(values):   
    width = 1 + max(len(values[s]) for s in slots)
    line = '+ '.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width) + ('| ' if c in '36' else '') for c in cols))
        if r in 'CF': #if r is in rows C or F, print the plus signs in the line of -------+---------+---- etc
                print(line)
    print()


# for solved file output
def display_(filename, values):
    f = open(filename, 'w')
    for r in rows:
        for c in cols:
            f.write(''.join(values[r+c]))

def sol(grid):
    return search(parse_grid(grid))

# Depth First Search + propagation to try all values 1-9
def search(values):
    if values is False:
        return False 
    if all(len(values[s]) == 1 for s in slots): 
        return values
    
    """Choose the unfilled slot s with minimum possibilities"""
    n,s = min((len(values[s]), s) for s in slots if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d)) for d in values[s])

def shuffled(seq): # *cant redefine shuffle in Python* 
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

# Return some element of seq that is true.
def some(seq):
    for e in seq:
        if e: return e
    return False

# Returns true or false, depending if the puzzle is solved or not.
# "A puzzle is solved if each unit is a permutation of the digits 1 to 9." - Norvig
def solved(values):
    def unitsolved(unit):
        return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)

# Parse a file into a list of strings, separated by sep = \n (null)
def fromfile(filename, sep = '\n'):
    return open(filename).read().strip().split(sep)

# write a list (puzzle) to a user-specified file
def tofile(filename, values):
    f = open(filename,'w')
    f.write(values) 
    f.close() 



# Make a random puzzle with N or more assignments. If a value breaks the puzzle,
# it restarts. We assume the puzzles are true sudoku puzzles if they solve in a
# reasonable amount of time (i.e. < 1 second)
def generate(N = 17): # at least 17 digits required to make a sudoku puzzle

    values = dict((s, digits) for s in slots)
    
    for s in shuffled(slots):
        if not assign(values, s, random.choice(values[s])):
            break
        
        ds = [values[s] for s in slots if len(values[s]) == 1]
        
        if len(ds) >= N and len(set(ds)) > 7:
            values_ = ''.join(values[s] if len(values[s]) == 1 else '.' for s in slots)
            return values_

    return generate(N) # try again if fail to create a puzzle. (has occured once)


# default testing puzzles
grid1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid2  = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1  = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
""" from Norvig """





    
