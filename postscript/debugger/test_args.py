import io

from .interpreter import Interpreter, Scanner

def run_and_gather_output(program):
    i = Interpreter()

    output_lines = []
    def capture_print(value):
        output_lines.append(str(value))
    i.print = capture_print

    for _ in i.execute(Scanner(io.StringIO(program))):
        pass

    return '\n'.join(output_lines)

def test_basic_args():
    program = '''
/strcat { %args prefix suffix
  ptags
  pop pop (Hello, Rob)
} def

(Hello, ) %tag greeting
(Rob) %tag name

ptags

strcat
    '''

    output = run_and_gather_output(program)
    assert output.splitlines() == [
        'name',
        'greeting',

        'suffix',
        'prefix',
    ]

def test_restore_tags():
    program = '''
/kindapop { %args second first
  pop
} def

1 %tag one
2 %tag two
kindapop
ptags
    '''

    output = run_and_gather_output(program)
    assert output.splitlines() == [
        'one',
    ]
