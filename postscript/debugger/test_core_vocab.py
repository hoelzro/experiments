import io

from .interpreter import Interpreter, Scanner

def run_and_gather_stack(program):
    i = Interpreter()
    for _ in i.execute(Scanner(io.StringIO(program))):
        pass
    return [ v.value for v in i.operand_stack ]

def run_and_gather_stack_and_output(program):
    i = Interpreter()

    output_lines = []
    def capture_print(value):
        output_lines.append(str(value))
    i.print = capture_print

    for _ in i.execute(Scanner(io.StringIO(program))):
        pass

    return [ v.value for v in i.operand_stack ], '\n'.join(output_lines)

def test_sub():
    program = '10 8 sub'
    values = run_and_gather_stack(program)
    assert values == [2]

def test_sub_reals():
    program = '1 0.1 sub'
    values = run_and_gather_stack(program)
    assert values == [0.9]

def test_print():
    program = '1 2 ='

    values, output = run_and_gather_stack_and_output(program)
    assert values == [1]
    assert output == '2'

def test_index():
    program = '1 2 3 2 index'
    values = run_and_gather_stack(program)
    assert values == [1, 2, 3, 1]

def test_for():
    program = '1 1 4 { 1 sub } for'
    values = run_and_gather_stack(program)
    assert values == [0, 1, 2, 3]

def test_exec():
    program = '{ 3 } exec'
    values = run_and_gather_stack(program)
    assert values == [3]

def test_def():
    program = '/pushthree { 3 } def pushthree'
    values = run_and_gather_stack(program)
    assert values == [3]

def test_dup():
    program = '1 2 dup'
    values = run_and_gather_stack(program)
    assert values == [1, 2, 2]

def test_mul():
    program = '10 8 mul'
    values = run_and_gather_stack(program)
    assert values == [80]

def test_mul_reals():
    program = '0.1 8 mul'
    values = run_and_gather_stack(program)
    assert values == [0.8]

def test_add():
    program = '10 8 add'
    values = run_and_gather_stack(program)
    assert values == [18]

def test_add_reals():
    program = '10.2 0.8 add'
    values = run_and_gather_stack(program)
    assert values == [11]

def test_exch():
    program = '10 8 exch'
    values = run_and_gather_stack(program)
    assert values == [8, 10]

def test_copy():
    program = '1 2 3 4 5 2 copy'
    values = run_and_gather_stack(program)
    assert values == [1, 2, 3, 4, 5, 4, 5]

def test_roll():
    program = '1 2 3 3 2 roll'
    values = run_and_gather_stack(program)
    assert values == [2, 3, 1]

def test_known():
    program = '<< /south true >> /south known'
    values = run_and_gather_stack(program)
    assert values == [True]
