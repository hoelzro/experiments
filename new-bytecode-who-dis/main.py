import dis

def regular_for_loop(values):
    '''
    A function that just uses a regular for loop
    '''
    new_values = []
    for v in values:
        new_values.append(v * 2)
    return new_values

def list_comprehension(values):
    '''
    A function that uses a list comprehension
    '''
    return [v * 2 for v in values]

def generator_function(values):
    '''
    A generator function
    '''
    for v in values:
        yield v * 2

def list_comprehension_with_assignment_expr_conditional(values):
    '''
    A function that uses a list comprehension with := in the conditional
    '''
    return [v * 2 for v in values if (v2 := v)]

def list_comprehension_with_assignment_expr_value(values):
    '''
    A function that uses a list comprehension with := in the value
    '''
    return [(v2 := v) * 2 for v in values]


for fn in [list_comprehension, list_comprehension_with_assignment_expr_conditional, list_comprehension_with_assignment_expr_value]:
    print(fn.__doc__.strip())
    dis.dis(fn)
    print('')
