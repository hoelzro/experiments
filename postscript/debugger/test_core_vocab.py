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
