############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 4 Starter Code
## v1.1
## - removed the example in ve since it is misleading.
############################################################

from bnetbase import Variable, Factor, BN
import csv
from itertools import product


def normalize(factor):
    '''
    Normalize the factor such that its values sum to 1.
    Do not modify the input factor.

    :param factor: a Factor object. 
    :return: a new Factor object resulting from normalizing factor.
    '''

    ### YOUR CODE HERE ###
    scope = factor.get_scope()
    domains = []
    for v in scope:
        domains.append(v.domain())
    
    # Use itertools.product to get all combinations (got this idea from chatgpt)
    combinations = list(product(*domains)) # will contain all the combinations in tuples

    factor_new = Factor(factor.name+'_normalized', scope)
    total = 0.0
    for combo in combinations:
        for index, v in enumerate(scope):
            v.set_assignment(combo[index])
        val = factor.get_value_at_current_assignments()
        factor_new.add_value_at_current_assignment(val)
        total = total + val
    
    # update the values so they are normalized
    for combo in combinations:
        for index, v in enumerate(scope):
            v.set_assignment(combo[index])
        val = factor_new.get_value_at_current_assignments()
        factor_new.add_value_at_current_assignment(val/total)
    
    return factor_new

def restrict(factor, variable, value):
    '''
    Restrict a factor by assigning value to variable.
    Do not modify the input factor.

    :param factor: a Factor object.
    :param variable: the variable to restrict.
    :param value: the value to restrict the variable to
    :return: a new Factor object resulting from restricting variable to value.
             This new factor no longer has variable in it.
    ''' 

    ### YOUR CODE HERE ###
    factor_vars = factor.get_scope()
    
    if variable not in factor_vars:
        return factor
    
    factor_vars.remove(variable)
    var_domains = [] # example: [[1, 2, 3], ['a', 'b', 'c'], [4, 5, 6]]
    for v in factor_vars:
        var_domains.append(v.domain())
    
    # Use itertools.product to get all combinations (got this idea from chatgpt)
    combinations = list(product(*var_domains)) # will contain all the combinations in tuples

    # now we need to set the assignment for the variable to be value
    # and then set assignments for all the other variables depending on the combinations 
    # eg: var1 = '1' is set
    # now set var2 = 'a' and var3 = '4'
    # next iter set var2 = 'a' and var3 = '5'
    # etc.
    # once we set assignments for the vars, get value at assignment and add it to new factor
    variable.set_assignment(value)

    factor_new = Factor(name=factor.name + '_restrict', scope=factor_vars)
    for combo in combinations:
        for index, v in enumerate(factor_vars):
            v.set_assignment(combo[index])
        factor_new.add_value_at_current_assignment(factor.get_value_at_current_assignments())

    return factor_new




def sum_out(factor, variable):
    '''
    Sum out a variable variable from factor factor.
    Do not modify the input factor.

    :param factor: a Factor object.
    :param variable: the variable to sum out.
    :return: a new Factor object resulting from summing out variable from the factor.
             This new factor no longer has variable in it.
    '''       

    ### YOUR CODE HERE ###
    # similar code to restrict
    factor_vars = factor.get_scope()
    
    if variable not in factor_vars:
        return factor
    
    factor_vars.remove(variable)

    var_domains = []
    for v in factor_vars:
        var_domains.append(v.domain())
    
    combinations = list(product(*var_domains))

    # for each combination that we have
    # we need to iterate through the values of variable
    # then set variable = value
    # then set the values for the variables in the combo as per combo numbers
    # then for that entire combo, what is the value at curr assignment?
    # keep a running total of those values for every combo
    factor_new = Factor(factor.name+'_sumout', scope=factor_vars)
    for combo in combinations:
        val_new = 0
        for val in variable.domain():
            variable.set_assignment(val)
            for index, v in enumerate(factor_vars):
                v.set_assignment(combo[index])
            val_new += factor.get_value_at_current_assignments()
        factor_new.add_value_at_current_assignment(val_new)

    return factor_new



def multiply(factor_list):
    '''
    Multiply a list of factors together.
    Do not modify any of the input factors. 

    :param factor_list: a list of Factor objects.
    :return: a new Factor object resulting from multiplying all the factors in factor_list.
    ''' 
    ### YOUR CODE HERE ###

    scope = []
    domain = []
    name = ''
    for factor in factor_list:
        for v in factor.get_scope():
            if v not in scope:
                scope.append(v)
                domain.append(v.domain())
                name = name + v.name
    
    factor_new = Factor('Factor'+name, scope)

    combinations = list(product(*domain))

    for combo in combinations:
        for index, v in enumerate(scope):
            v.set_assignment(combo[index])
        prod = 1
        for factor in factor_list:
            prod *= factor.get_value_at_current_assignments()
        factor_new.add_value_at_current_assignment(prod)
    
    return factor_new



def min_fill_ordering(factor_list, variable_query):
    '''
    This function implements The Min Fill Heuristic. We will use this heuristic to determine the order 
    to eliminate the hidden variables. The Min Fill Heuristic says to eliminate next the variable that 
    creates the factor of the smallest size. If there is a tie, choose the variable that comes first 
    in the provided order of factors in factor_list.

    The returned list is determined iteratively.
    First, determine the size of the resulting factor when eliminating each variable from the factor_list.
    The size of the resulting factor is the number of variables in the factor.
    Then the first variable in the returned list should be the variable that results in the factor 
    of the smallest size. If there is a tie, choose the variable that comes first in the provided order of 
    factors in factor_list. 
    Then repeat the process above to determine the second, third, ... variable in the returned list.

    Here is an example.
    Consider our complete Holmes network. Suppose that we are given a list of factors for the variables 
    in this order: P(E), P(B), P(A|B, E), P(G|A), and P(W|A). Assume that our query variable is Earthquake. 
    Among the other variables, which one should we eliminate first based on the Min Fill Heuristic? 

    - Eliminating B creates a factor of 2 variables (A and E).
    - Eliminating A creates a factor of 4 variables (E, B, G and W).
    - Eliminating G creates a factor of 1 variable (A).
    - Eliminating W creates a factor of 1 variable (A).

    In this case, G and W tie for the best variable to be eliminated first since eliminating each variable 
    creates a factor of 1 variable only. Based on our tie-breaking rule, we should choose G since it comes 
    before W in the list of factors provided.
    '''

    vars = []
    list_of_scopes = []
    for factor in factor_list:
        list_of_scopes.append(factor.get_scope())

    vars_to_eliminate = dict()
    for scope in list_of_scopes:
        for v in scope:
            if v != variable_query and v not in vars_to_eliminate:
                vars_to_eliminate[v] = []
    
    order_of_vars = []
    while vars_to_eliminate:
        var, scope = min_fill_ordering_helper(list_of_scopes, vars_to_eliminate, variable_query)
        if var is not None:
            vars.append(var)
        if var in vars_to_eliminate:
            vars_to_eliminate.pop(var)
        list_of_scopes = generate_scopes(var, scope, list_of_scopes)
    return vars

# return variable to be eliminated
def min_fill_ordering_helper(list_of_scopes, vars_to_eliminate, variable_query):
    ### YOUR CODE HERE ###
    # for each var in dict, if we eliminate them, what vars will be affected?
    for var in vars_to_eliminate.keys():
        num = 0
        for scope in list_of_scopes:
            if var in scope:
                for v in scope:
                    if v != var:
                        num += 1
        vars_to_eliminate[var] = num
    
    sorted_vars = dict(sorted(vars_to_eliminate.items(), key=lambda item: item[1]))
    list_vars = list(sorted_vars.keys())
    
    var_elim = None
    if len(list_vars) > 0:
        var_elim = list_vars[0]
    
    new_scope = []
    # generate new scope
    for s in list_of_scopes:
        if var_elim in s:
            for v in s:
                if not v in new_scope:
                    new_scope.append(v)
    if var_elim in new_scope:
        new_scope.remove(var_elim)

    return var_elim, new_scope

def generate_scopes(var, scope, list_of_scopes):
    updated_scopes = []
    for s in list_of_scopes:
        if var not in s:
            updated_scopes.append(s)
    updated_scopes.append(scope)
    return updated_scopes

def ve(bayes_net, var_query, varlist_evidence): 
    '''
    Execute the variable elimination algorithm on the Bayesian network bayes_net
    to compute a distribution over the values of var_query given the 
    evidence provided by varlist_evidence. 

    :param bayes_net: a BN object.
    :param var_query: the query variable. we want to compute a distribution
                     over the values of the query variable.
    :param varlist_evidence: the evidence variables. Each evidence variable has 
                         its evidence set to a value from its domain 
                         using set_evidence.
    :return: a Factor object representing a distribution over the values
             of var_query. that is a list of numbers, one for every value
             in var_query's domain. These numbers sum to 1. The i-th number
             is the probability that var_query is equal to its i-th value given 
             the settings of the evidence variables.

    '''
    ### YOUR CODE HERE ###
    # create factor for each var in bayes network
    # restrict each evidence variable to observed value
    # eliminate hidden vars
        # for each hidden var
            # multiply all factors that contain it
            # sum out that var from the factor
    # multiply remaining
    # normalize

    # initialize
    factors = bayes_net.factors()

    updated_factors = []
    
    # restrict evidence vars recursively
    for factor in factors:
        updated_factor = factor
        for e_v in varlist_evidence:
            if e_v in updated_factor.get_scope():
                updated_factor = restrict(updated_factor, e_v, e_v.get_evidence())
        updated_factors.append(updated_factor)
    
    # eliminate hidden vars
    order_of_vars = min_fill_ordering(updated_factors, var_query)

    for h_v in min_fill_ordering(updated_factors, var_query):
        factors_with_hv = []
        for factor in updated_factors:
            if h_v in factor.get_scope():
                factors_with_hv.append(factor)
        
        for factor in factors_with_hv:
            updated_factors.remove(factor)
        
        updated_factors.append(sum_out(multiply(factors_with_hv), h_v))

    # multiply
    new_factor = multiply(updated_factors)

    return normalize(new_factor)

def find_p():
    return 0

## The order of these domains is consistent with the order of the columns in the data set.
salary_variable_domains = {
"Work": ['Not Working', 'Government', 'Private', 'Self-emp'],
"Education": ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'],
"Occupation": ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'],
"MaritalStatus": ['Not-Married', 'Married', 'Separated', 'Widowed'],
"Relationship": ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
"Race": ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'],
"Gender": ['Male', 'Female'],
"Country": ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'],
"Salary": ['<50K', '>=50K']
}

salary_variable=Variable("Salary", ['<50K', '>=50K'])

def naive_bayes_model(data_file, variable_domains=salary_variable_domains, class_var=salary_variable):
    '''
    NaiveBayesModel returns a BN that is a Naive Bayes model that represents 
    the joint distribution of value assignments to variables in the given dataset.

    Remember a Naive Bayes model assumes P(X1, X2,.... XN, Class) can be represented as 
    P(X1|Class) * P(X2|Class) * .... * P(XN|Class) * P(Class).

    When you generated your Bayes Net, assume that the values in the SALARY column of 
    the dataset are the CLASS that we want to predict.

    Please name the factors as follows. If you don't follow these naming conventions, you will fail our tests.
    - The name of the Salary factor should be called "Salary" without the quotation marks.
    - The name of any other factor should be called "VariableName,Salary" without the quotation marks. 
      For example, the factor for Education should be called "Education,Salary".

    @return a BN that is a Naive Bayes model and which represents the given data set.
    '''
    ### READ IN THE DATA
    input_data = []
    headers = []
    with open(data_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)

    ### YOUR CODE HERE ###
    # extract class_var name so we can append to vars
    class_var_name = class_var.name

    variables = []
    factors = []
    vars_dict_lookup = dict()
    factors_dict_lookup = dict()
    total_individuals = len(input_data)

    # create variables from variable_domains
    for v_name in variable_domains:
        if v_name == class_var_name:
            continue
        name = v_name
        var = Variable(name, variable_domains[v_name])
        variables.append(var)
        vars_dict_lookup[name] = var
    
    # class_var dictionary key is the domain value and value is list of rows where that domain value appears
    var_names = list(variable_domains.keys())
    total_individuals = len(input_data)
    class_var_index = headers.index(class_var_name)
    class_var_dict = dict()

    for row in input_data:
        val = row[class_var_index]
        if val in class_var_dict:
            class_var_dict[val] += 1
        else:
            class_var_dict[val] = 1

    # create factor for class variable
    factor_name = class_var_name
    f = Factor(factor_name, [class_var])
    f_values = []
    for v in class_var.domain():
        # find P(class_var=v)
        p = class_var_dict[v]/total_individuals
        f_values.append([v, p])
    f.add_values(f_values)
    
    # create factors
    for var in variables:
        name = var.name + ',' + class_var.name
        factor = Factor(name, [var, class_var])
        factors.append(factor)
        factors_dict_lookup[name] = factor
    

    for var in variables:
        values = []
        var_name = var.name
        var_domain = var.domain()
        var_index = headers.index(var.name)
        var_factor = factors_dict_lookup[var.name+','+class_var.name]

        for var_v in var_domain:
            for class_v in class_var.domain():
                sum = 0.0
                for row in input_data:
                    if row[var_index] == var_v and row[class_var_index] == class_v:
                        sum += 1
                values.append([var_v, class_v, sum/class_var_dict[class_v]])
        var_factor.add_values(values)

    factors.append(f)
    variables.append(class_var)

    model = BN("Model", variables, factors)
    return model


def explore(bayes_net, question):
    '''    
    Return a probability given a Naive Bayes Model and a question number 1-6. 
    
    The questions are below: 
    1. What percentage of the women in the test data set does our model predict having a salary >= $50K? 
    2. What percentage of the men in the test data set does our model predict having a salary >= $50K? 
    3. What percentage of the women in the test data set satisfies the condition: P(S=">=$50K"|Evidence) is strictly greater than P(S=">=$50K"|Evidence,Gender)?
    4. What percentage of the men in the test data set satisfies the condition: P(S=">=$50K"|Evidence) is strictly greater than P(S=">=$50K"|Evidence,Gender)?
    5. What percentage of the women in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?
    6. What percentage of the men in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?

    @return a percentage (between 0 and 100)
    ''' 
    

    ### YOUR CODE HERE ###
    percent = 0.0
    input_data = []
    headers = []
    with open('data/adult-test.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)

    if question == 1:
        total_more = 0.0
        total_female = 0.0
        query_var = bayes_net.get_variable('Salary')

        for row in input_data:
            if 'Male' in row:
                continue
            total_female += 1
            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'Gender' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)
                #print('Setting evidence var ', var.name, '=', val)
            # perform VE with salary as query
            res = ve(bayes_net, query_var, evidence_vars)
            more_p = res.get_value(['>=50K'])
            if more_p > 0.5:
                total_more += 1
        #print(total_more)
        #print(total_female)
        
        percent = total_more/float(total_female)*100.00

    if question == 2:
        total_more = 0.0
        total_male = 0.0
        query_var = bayes_net.get_variable('Salary')

        for row in input_data:
            if 'Female' in row:
                continue
            total_male += 1
            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'Gender' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)
                #print('Setting evidence var ', var.name, '=', val)
            # perform VE with salary as query
            res = ve(bayes_net, query_var, evidence_vars)
            more_p = res.get_value(['>=50K'])
            if more_p > 0.5:
                total_more += 1
        #print(total_more)
        #print(total_male)
        
        percent = total_more/float(total_male)*100.00

    if question == 3:
        total_more = 0.0
        total_female = 0.0
        query_var = bayes_net.get_variable('Salary')

        for row in input_data:
            if 'Male' in row:
                continue
            total_female += 1
            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'Gender' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)

            # perform VE with salary as query and gender not in evidence
            res = ve(bayes_net, query_var, evidence_vars)
            more_p = res.get_value(['>=50K'])

            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)

            # perform VE with salary as query and gender in evidence
            res2 = ve(bayes_net, query_var, evidence_vars)
            more_p2 = res2.get_value(['>=50K'])

            if more_p > more_p2:
                total_more += 1

        #print(total_more)
        #print(total_female)
        
        percent = total_more/float(total_female)*100.00
    
    if question == 4:
        total_more = 0.0
        total_male = 0.0
        query_var = bayes_net.get_variable('Salary')

        for row in input_data:
            if 'Female' in row:
                continue
            total_male += 1
            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'Gender' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)

            # perform VE with salary as query and gender not in evidence
            res = ve(bayes_net, query_var, evidence_vars)
            more_p = res.get_value(['>=50K'])

            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)

            # perform VE with salary as query and gender in evidence
            res2 = ve(bayes_net, query_var, evidence_vars)
            more_p2 = res2.get_value(['>=50K'])

            if more_p > more_p2:
                total_more += 1

        #print(total_more)
        #print(total_male)
        
        percent = total_more/float(total_male)*100.00

    if question == 5:
        total_more = 0.0
        total_female = 0.0
        query_var = bayes_net.get_variable('Salary')

        for row in input_data:
            if 'Male' in row:
                continue
            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'Gender' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)
                #print('Setting evidence var ', var.name, '=', val)
            # perform VE with salary as query
            res = ve(bayes_net, query_var, evidence_vars)
            more_p = res.get_value(['>=50K'])
            if more_p > 0.5:
                total_female += 1
                # check if actual salary is >=50k
                if '>=50K' in row:
                    total_more += 1
        
        #print(total_more)
        #print(total_female)
        
        percent = total_more/float(total_female)*100.00
    
    if question == 6:
        total_more = 0.0
        total_male = 0.0
        query_var = bayes_net.get_variable('Salary')

        for row in input_data:
            if 'Female' in row:
                continue
            evidence_vars = []
            for index, val in enumerate(row):
                var_name = headers[index]
                if var_name == 'Salary' or var_name == 'Gender' or var_name == 'MaritalStatus' or var_name == 'Race' or var_name == 'Country':
                    continue
                var = bayes_net.get_variable(var_name)
                var.set_evidence(val)
                evidence_vars.append(var)
                #print('Setting evidence var ', var.name, '=', val)
            # perform VE with salary as query
            res = ve(bayes_net, query_var, evidence_vars)
            more_p = res.get_value(['>=50K'])
            if more_p > 0.5:
                total_male += 1
                # check if actual salary is >=50k
                if '>=50K' in row:
                    total_more += 1
        
        #print(total_more)
        #print(total_male)
        
        percent = total_more/float(total_male)*100.00
    
    return percent

#print(explore(naive_bayes_model('adult-train.csv'), 1))
#print(explore(naive_bayes_model('adult-train.csv'), 2))
#print(explore(naive_bayes_model('adult-train.csv'), 3))
#print(explore(naive_bayes_model('adult-train.csv'), 4))
#print(explore(naive_bayes_model('adult-train.csv'), 5))
#print(explore(naive_bayes_model('adult-train.csv'), 6))

