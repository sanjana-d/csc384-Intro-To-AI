############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 3 Starter Code
## v1.0
##
############################################################

def check_constraint(constraint, var, pruned):

    cur_domain = var.cur_domain()
    for val in cur_domain:
        # assign this value to the unassigned variable
        # see if this assignment violates any constraints
        var.assign(val)
        # get values of the variables in the scope
        assignments = []
        vars = constraint.get_scope()
        for v in vars:
            assignments.append(v.get_assigned_value())

        # check if this assignment violates constraint
        if not constraint.check(assignments):
            # prune it from var's domain
            var.prune_value(val)
            pruned.append((var, val))
        # unassign it now
        var.unassign()
        # check if domain is empty/need to backtrack since we could've pruned all values
    if var.cur_domain_size() == 0:
        return False, pruned
    return True, pruned
        

def prop_FC(csp, last_assigned_var=None):
    """
    This is a propagator to perform forward checking. 

    First, collect all the relevant constraints.
    If the last assigned variable is None, then no variable has been assigned 
    and we are performing propagation before search starts.
    In this case, we will check all the constraints.
    Otherwise, we will only check constraints involving the last assigned variable.

    Among all the relevant constraints, focus on the constraints with one unassigned variable. 
    Consider every value in the unassigned variable's domain, if the value violates 
    any constraint, prune the value. 

    :param csp: The CSP problem
    :type csp: CSP
        
    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: The boolean indicates whether forward checking is successful.
        The boolean is False if at least one domain becomes empty after forward checking.
        The boolean is True otherwise.
        Also returns a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]
    """

    pruned = []

    if not last_assigned_var:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(last_assigned_var)
    for constraint in constraints:
        # focus on cons with 1 unassigned var
        if constraint.get_num_unassigned_vars() == 1:
            unassigned_var = constraint.get_unassigned_vars()[0]
            # assign it to values in its domain and check constraint
            is_valid, pruned = check_constraint(constraint, unassigned_var, pruned)
            if not is_valid:
                return False, pruned
    return True, pruned

def tuple_valid(constraint, t):
    for i, v in enumerate(constraint.get_scope()):
        # for ith variable in constraint, the ith variable in tuple is its potential val
        # we just want to check if its in var's domain to see if this arc applies to us here
        # if its not in its domain means that t[i] = val was assigned to the other variable in constraint so we ignore this arc
        if not v.in_cur_domain(t[i]):
            return False
    return True

def check_arc(constraint, var, val):
    # check if sup_tuples of this constraint has var, val
    # if it does then we need to traverse all the tuples in which we assigned val to var
    # then check if the assignment is valid
    if (var, val) in constraint.sup_tuples:
        for t in constraint.sup_tuples[(var, val)]:
            if tuple_valid(constraint, t):
                return True
    return False

def restore_arc_consistency(csp, constraints_queue, not_queue, pruned):
    all_constraints_queue = csp.get_all_cons()
    # while queue not empty, take out arcs, restore consistency, add arcs
    while len(constraints_queue) > 0:
        cons = constraints_queue.pop(0)
        not_queue.append(cons)
        vars  = cons.get_scope()
        for var in vars:
            for val in var.cur_domain():
                if not check_arc(cons, var, val):
                    var.prune_value(val)
                    pruned.append((var, val))

                    if var.cur_domain_size() == 0:
                        constraints_queue.clear()
                        return False, pruned
                    else:
                        # add constraints for the var back into queue
                        for c in not_queue:
                            if var in c.get_scope():
                                constraints_queue.append(c)
                                not_queue.remove(c)
                        

    return True, pruned

def prop_AC3(csp, last_assigned_var=None):
    """
    This is a propagator to perform the AC-3 algorithm.

    Keep track of all the constraints in a queue (list). 
    If the last_assigned_var is not None, then we only need to 
    consider constraints that involve the last assigned variable.

    For each constraint, consider every variable in the constraint and 
    every value in the variable's domain.
    For each variable and value pair, prune it if it is not part of 
    a satisfying assignment for the constraint. 
    Finally, if we have pruned any value for a variable,
    add other constraints involving the variable back into the queue.

    :param csp: The CSP problem
    :type csp: CSP
        
    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: a boolean indicating if the current assignment satisifes 
        all the constraints and a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]
    """
    pruned = []

    if not last_assigned_var:
        constraints_queue = csp.get_all_cons()
        not_queue = []
    else:
        constraints_queue = csp.get_cons_with_var(last_assigned_var)
        not_queue = [item for item in csp.get_all_cons() if item not in constraints_queue]

    valid, pruned = restore_arc_consistency(csp, constraints_queue, not_queue, pruned)
    if not valid:
        return False, pruned
    return True, pruned

def ord_mrv(csp):
    """
    Implement the Minimum Remaining Values (MRV) heuristic.
    Choose the next variable to assign based on MRV.

    If there is a tie, we will choose the first variable. 

    :param csp: A CSP problem
    :type csp: CSP

    :returns: the next variable to assign based on MRV

    """

    # get all unassigned variables
    # go through variables domain sizes and keep track of smallest domain

    vars = csp.get_all_unasgn_vars()
    min = float('inf')
    res = None

    for var in vars:
        size = var.cur_domain_size()
        if size < min:
            min = size
            res = var
    return res


###############################################################################
# Do not modify the prop_BT function below
###############################################################################


def prop_BT(csp, last_assigned_var=None):
    """
    This is a basic propagator for plain backtracking search.

    Check if the current assignment satisfies all the constraints.
    Note that we only need to check all the fully instantiated constraints 
    that contain the last assigned variable.
    
    :param csp: The CSP problem
    :type csp: CSP

    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: a boolean indicating if the current assignment satisifes all the constraints 
        and a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]

    """
    
    # If we haven't assigned any variable yet, return true.
    if not last_assigned_var:
        return True, []
        
    # Check all the constraints that contain the last assigned variable.
    for c in csp.get_cons_with_var(last_assigned_var):

        # All the variables in the constraint have been assigned.
        if c.get_num_unassigned_vars() == 0:

            # get the variables
            vars = c.get_scope() 

            # get the list of values
            vals = []
            for var in vars: #
                vals.append(var.get_assigned_value())

            # check if the constraint is satisfied
            if not c.check(vals): 
                return False, []

    return True, []
