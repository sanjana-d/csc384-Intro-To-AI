############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 3 Starter Code
## v1.1
## Changes:
##   v1.1: updated the comments in kropki_model. 
##         the second return value should be a 2d list of variables.
############################################################

from board import *
from cspbase import *

def kropki_model(board):
    """
    Create a CSP for a Kropki Sudoku Puzzle given a board of dimension.

    If a variable has an initial value, its domain should only contain the initial value.
    Otherwise, the variable's domain should contain all possible values (1 to dimension).

    We will encode all the constraints as binary constraints.
    Each constraint is represented by a list of tuples, representing the values that
    satisfy this constraint. (This is the table representation taught in lecture.)

    Remember that a Kropki sudoku has the following constraints.
    - Row constraint: every two cells in a row must have different values.
    - Column constraint: every two cells in a column must have different values.
    - Cage constraint: every two cells in a 2x3 cage (for 6x6 puzzle) 
            or 3x3 cage (for 9x9 puzzle) must have different values.
    - Black dot constraints: one value is twice the other value.
    - White dot constraints: the two values are consecutive (differ by 1).

    Make sure that you return a 2D list of variables separately. 
    Once the CSP is solved, we will use this list of variables to populate the solved board.
    Take a look at csprun.py for the expected format of this 2D list.

    :returns: A CSP object and a list of variables.
    :rtype: CSP, List[List[Variable]]

    """
    name = 'Kropi_CSP'
    csp_model = CSP(name=name)
    vars = create_variables(board.dimension)
    
    for i in range(board.dimension):
        for j in range(board.dimension):
            val = board.cells[i][j]
            var = vars[i * board.dimension + j]
            if val == 0:
                var.add_domain_values(create_initial_domain(board.dimension))
            else:
                var.add_domain_values([int(val)])
    
    for v in vars:
        csp_model.add_var(v)
    
    diff_constraints = create_row_and_col_constraints(board.dimension, satisfying_tuples_difference_constraints(board.dimension), vars)
    for const in diff_constraints:
        csp_model.add_constraint(const)
    
    cage_constraints = create_cage_constraints(board.dimension, satisfying_tuples_difference_constraints(board.dimension), vars)
    for const in cage_constraints:
        csp_model.add_constraint(const)
    
    dot_constraints = create_dot_constraints(board.dimension, board.dots, satisfying_tuples_white_dots(board.dimension), satisfying_tuples_black_dots(board.dimension), vars)
    for const in dot_constraints:
        csp_model.add_constraint(const)

    vars_2d = []
    for i in range(board.dimension):
        rows = []
        for j in range(board.dimension):
            rows.append(vars[i * board.dimension + j])
        vars_2d.append(rows)
    
    return csp_model, vars_2d

def create_initial_domain(dim):
    """
    Return a list of values for the initial domain of any unassigned variable.
    [1, 2, ..., dimension]

    :param dim: board dimension
    :type dim: int

    :returns: A list of values for the initial domain of any unassigned variable.
    :rtype: List[int]
    """
    vals = list(range(1, dim+1))
    return vals

def create_variables(dim):
    """
    Return a list of variables for the board.

    We recommend that your name each variable Var(row, col).

    :param dim: Size of the board
    :type dim: int

    :returns: A list of variables, one for each cell on the board
    :rtype: List[Variables]
    """

    vars = []
    for i in range(dim):
        for j in range(dim):
            var_name = str(i) + ',' + str(j) #row,col
            var = Variable(var_name)
            vars.append(var)
    return vars

def satisfying_tuples_difference_constraints(dim):
    """
    Return a list of satifying tuples for binary difference constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satifying tuples
    :rtype: List[(int,int)]
    """
    tups = []
    for i in range(1, dim+1):
        for j in range(1, dim+1):
            if i != j:
                tups.append((i, j))
    return tups
  
def satisfying_tuples_white_dots(dim):
    """
    Return a list of satifying tuples for white dot constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satifying tuples
    :rtype: List[(int,int)]
    """

    tups = []
    for i in range(1, dim+1):
        for j in range(1, dim+1):
            if i != j:
                if i-j == 1 or j-i == 1:
                    tups.append((i, j))
    return tups
  
def satisfying_tuples_black_dots(dim):
    """
    Return a list of satifying tuples for black dot constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satifying tuples
    :rtype: List[(int,int)]
    """

    tups = []
    for i in range(1, dim+1):
        for j in range(1, dim+1):
            if i != j:
                if 2*i == j or 2*j == i:
                    tups.append((i, j))
    return tups
    
def create_row_and_col_constraints(dim, sat_tuples, variables):
    """
    Create and return a list of binary all-different row/column constraints.

    :param dim: Size of the board
    :type dim: int

    :param sat_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple are different.
    :type sat_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary all-different constraints
    :rtype: List[Constraint]
    """
    # the variable in row and col is at index i = row * dim + col in the list
    constraints = []

    # row constraints
    for row in range(dim):
        for i in range(dim):
            var1 = variables[row * dim + i]
            for j in range(i, dim):
                if i != j:
                    var2 = variables[row * dim + j]
                    name = 'Row_' + var1.name + '_' + var2.name
                    scope = [var1, var2]
                    const = Constraint(name, scope)
                    const.add_satisfying_tuples(sat_tuples)
                    constraints.append(const)

    # col constraints
    for row in range(dim):
        for i in range(dim):
            var1 = variables[i * dim + row]
            for j in range(i, dim):
                if i != j:
                    var2 = variables[j * dim + row]
                    name = 'Col_' + var1.name + '_' + var2.name
                    scope = [var1, var2]
                    const = Constraint(name, scope)
                    const.add_satisfying_tuples(sat_tuples)
                    constraints.append(const)
    return constraints
#create_row_and_col_constraints(4, satisfying_tuples_difference_constraints(4), create_variables(4))
def create_cage_constraints(dim, sat_tuples, variables):
    """
    Create and return a list of binary all-different constraints for all cages.

    :param dim: Size of the board
    :type dim: int

    :param sat_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple are different.
    :type sat_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary all-different constraints
    :rtype: List[Constraint]
    """
    constraints_dict = dict()
    constraints = []
    subgrid_rows = 3
    subgrid_cols = 2

    if dim == 9:
        subgrid_cols = 3
    if dim == 4:
        subgrid_rows = 2
    
    for i in range(0, dim, subgrid_rows):
        for j in range(0, dim, subgrid_cols):

            # go through subgrid
            for row in range(i, i+subgrid_rows):
                for col in range(j, j+subgrid_cols):
                    var1 = variables[row * dim + col]
                    # row, col are indices within subgrid
                    # for each element in the subgrid we need to traverse the subgrid again
                    for k in range(i, i+subgrid_rows):
                        for l in range(j, j+subgrid_cols):
                            if k != row or l != col:
                                var2 = variables[k * dim + l]
                                name = 'Cage_' + var1.name + '_' + var2.name
                                inverse_name = 'Cage_' + var2.name + '_' + var1.name
                                if inverse_name not in constraints_dict:
                                    scope = [var1, var2]
                                    const = Constraint(name, scope)
                                    const.add_satisfying_tuples(sat_tuples)
                                    constraints.append(const)
                                    constraints_dict[name] = True
    return constraints

def create_dot_constraints(dim, dots, white_tuples, black_tuples, variables):
    """
    Create and return a list of binary constraints, one for each dot.

    :param dim: Size of the board
    :type dim: int
    
    :param dots: A list of dots, each dot is a Dot object.
    :type dots: List[Dot]

    :param white_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple satisfy the white dot constraint.
    :type white_tuples: List[(int, int)]
    
    :param black_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple satisfy the black dot constraint.
    :type black_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary dot constraints
    :rtype: List[Constraint]
    """
    constraints = []
    for dot in dots:
        var1 = variables[dot.cell_row * dim + dot.cell_col]
        var2 = variables[dot.cell2_row * dim + dot.cell2_col]
        name = 'Dot_' + var1.name + '_' + var2.name
        scope = [var1, var2]
        const = Constraint(name, scope)
        if dot.color == CHAR_BLACK:
            const.add_satisfying_tuples(black_tuples)
        else:
            const.add_satisfying_tuples(white_tuples)
        
        constraints.append(const)

    return constraints