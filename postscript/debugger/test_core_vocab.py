import io

from .interpreter import Interpreter, Scanner

def run_and_gather_stack(program):
    i = Interpreter()
    for _ in i.execute(Scanner(io.StringIO(program))):
        pass
    return [ v.value for v in i.operand_stack ]

def test_sub():
    program = '10 8 sub'
    values = run_and_gather_stack(program)
    assert values == [2]
