import io

from .interpreter import Interpreter, Scanner

def run_and_gather_tags(program):
    i = Interpreter()
    for _ in i.execute(Scanner(io.StringIO(program))):
        pass
    return [ v.tag for v in i.operand_stack ]

def test_no_tag():
    program = '1'
    tags = run_and_gather_tags(program)
    assert tags == [None]

def test_integer_literal():
    program = '1 %tag one'
    tags = run_and_gather_tags(program)
    assert tags == ['one']

def test_two_literals():
    program = '''
1 %tag one
2 %tag two
    '''
    tags = run_and_gather_tags(program)
    assert tags == ['one', 'two']

def test_name_literal():
    program = '/name %tag one'
    tags = run_and_gather_tags(program)
    assert tags == ['one']

def test_string_literal():
    program = '(string) %tag two'
    tags = run_and_gather_tags(program)
    assert tags == ['two']

def test_executable_array():
    program = '''
{ %tag start
  1
} %tag end
    '''
    tags = run_and_gather_tags(program)
    assert tags == ['end']

_comment='''
  - if a word is executed and does *not* have a tag…
    - if the stack isn't altered, nothing happens (obviously)
    - if a value is removed, nothing happens (obviously)
    - if a value is moved around the stack, nothing happens
    - if a value is copied from elsewhere in the stack, the copied value has the same tag as the original
    - if a value is created, no tag is created for this value (well, maybe some operators will "infer" a tag)
  - if a word is executed and *does* have a tag…
    - if the stack isn't altered, nothing happens (obviously)
    - if a value is removed, nothing happens (obviously)
    - if a value is moved around the stack…
    - if a value is copied from elsewhere in the stack…
    - if a value is created…
  - look at those http://tunes.org/~iepos/joy.html things
'''
