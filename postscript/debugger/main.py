from collections import deque, ChainMap
from dataclasses import dataclass
import inspect
import io
import sys

from typing import Optional, Self

from pprint import pprint
from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Footer, Log, Static, TextArea

class Frame:
    '''
    A stack frame on the execution stack
    '''
    def __init__(self, program):
        self.program = iter(program)

@dataclass
class Value:
    value: any # please override this in subclasses

    executable: bool = False
    line: Optional[int] = None
    column: Optional[int] = None
    length: Optional[int] = None

    tag: Optional[str] = None
    predecessor: Optional[Self] = None

    def execute(self, i, direct):
        # XXX this should probably just be `i.operand_stack.append(self)` and subclasses that actually
        #     check `self.executable` should override as such or something - or callers should do the
        #     `if value.executable: …` check
        raise NotImplementedError(f'execute not implemented for type {type(self)}')

    def __ps_str__(self):
        return str(self.value)

    def __ps_repr__(self):
        # XXX improve me!
        return str(self.value)

@dataclass
class MarkValue(Value):
    value: any = None
    def execute(self, i, direct):
        # XXX I *think* it should be ok just to push ourselves onto the stack?
        i.operand_stack.append(self)

    def __ps_str__(self):
        return '-mark-'

    def __ps_repr__(self):
        return '-mark-'

@dataclass
class NameValue(Value):
    value: str

    def execute(self, i, direct):
        if self.executable:
            # executing an executable name looks up the name in the dictionary and executes _that_
            c = i.look_up(self.value)

            # XXX is this how I want to dispatch on values vs functions implementing operators?
            if hasattr(c, 'execute'):
                return c.execute(i, direct=False)
            else:
                return c(i)
        else:
            # executing a literal name appends the name to the operand stack (XXX can I just append(self)?)
            # XXX I *think* it should be ok just to push ourselves onto the stack?
            i.operand_stack.append(self)

@dataclass
class StringValue(Value):
    value: str

    def execute(self, i, direct):
        i.operand_stack.append(self)

    def __ps_repr__(self):
        return '(' + self.value + ')'

@dataclass
class IntegerValue(Value):
    value: int

    def execute(self, i, direct):
        i.operand_stack.append(self)

@dataclass
class ArrayValue(Value):
    value: list[Value]

    def execute(self, i, direct):
        if self.executable and not direct:
            # executing an executable array…executes it
            return i.execute(self)
        else:
            # executing a literal array just pushes it onto the stack
            # XXX I *think* it should be ok just to push ourselves onto the stack?
            i.operand_stack.append(self)

    def __iter__(self):
        return iter(self.value)

    def __ps_str__(self):
        return self.__ps_repr__()

    def __ps_repr__(self):
        pieces = []

        pieces.append('{' if self.executable else '[')
        for v in self.value:
            pieces.append(v.__ps_repr__())
        pieces.append('}' if self.executable else ']')

        return ' '.join(pieces)

# XXX these two classes are kinda weird
@dataclass
class StartProcValue(Value):
    value: any = None

    def execute(self, i, direct):
        # XXX I *think* it should be ok just to push ourselves onto the stack?
        i.operand_stack.append(self)

@dataclass
class EndProcValue(Value):
    value: any = None

def print_value(v, indent=0):
    print('  ' * indent, type(v).__name__, end='', sep='')
    if isinstance(v, ArrayValue):
        print('')
        for subvalue in v.value:
            print_value(subvalue, indent=indent+1)
    else:
        print('', v.value)

class Scanner:
    def __init__(self, lines):
        self.lines = lines

    def __iter__(self):
        for line_no, line in enumerate(self.lines, start=1):
            line = line.rstrip()

            tag = None
            args = None

            if (idx := line.find('%')) != -1:
                comment = line[idx+1:]
                line = line[:idx]

                while len(comment) > 0 and comment[0].isspace():
                    comment = comment[1:comment]

                if comment.startswith('tag '):
                    tag = comment.removeprefix('tag ')
                if comment.startswith('args '):
                    args = comment.removeprefix('args ')

            col_no = 1

            while True:
                stripped = line.lstrip()
                col_no += len(line) - len(stripped)
                line = stripped
                if line == '':
                    break

                if line.startswith('/'):
                    idx = 1
                    while idx < len(line) and line[idx].isalpha():
                        idx += 1
                    yield NameValue(value=line[1:idx], line=line_no, column=col_no, length=idx, tag=tag)
                    line = line[idx:]
                    col_no += idx
                elif line[0] == '{':
                    assert len(line) == 1 or line[1].isspace()
                    yield StartProcValue(line=line_no, column=col_no, length=1, tag=tag)
                    line = line[1:]
                    col_no += 1
                elif line[0] == '}':
                    assert len(line) == 1 or line[1].isspace()
                    yield EndProcValue(line=line_no, column=col_no, length=1, tag=tag)
                    line = line[1:]
                    col_no += 1
                elif line[0].isalpha():
                    idx = 1
                    while idx < len(line) and line[idx].isalpha():
                        idx += 1
                    yield NameValue(value=line[:idx], line=line_no, column=col_no, length=idx, tag=tag, executable=True)
                    line = line[idx:]
                    col_no += idx
                elif (line[0] == '-' and line[1].isdigit()) or line[0].isdigit():
                    idx = 1
                    while idx < len(line) and line[idx].isdigit():
                        idx += 1
                    yield IntegerValue(value=int(line[:idx]), line=line_no, column=col_no, length=idx, tag=tag)
                    line = line[idx:]
                    col_no += idx
                elif line[0] == '(':
                    idx = line.index(')')
                    yield StringValue(value=line[1:idx], line=line_no, column=col_no, length=idx+1, tag=tag)
                    line = line[idx+1:]
                    col_no += idx + 1
                elif line[0] == '=':
                    assert len(line) == 1 or line[1].isspace()
                    yield NameValue(value='=', line=line_no, column=col_no, length=1, tag=tag, executable=True)
                    line = line[1:]
                    col_no += 1
                else:
                    raise NotImplementedError(f"can't handle rest of line {line!r}")

def op_count(i):
    i.operand_stack.append(IntegerValue(value=len(i.operand_stack)))

def op_def(i):
    name, value = i.check_arity(NameValue, Value)

    i.dictionary_stack[name.value] = value

def op_exec(i):
    fn, = i.check_arity(ArrayValue)

    return fn.execute(i, direct=False)

def op_for(i):
    init, incr, limit, fn = i.check_arity(IntegerValue, IntegerValue, IntegerValue, ArrayValue)

    for j in range(init.value, limit.value+1, incr.value):
        i.operand_stack.append(IntegerValue(
            value=j,
        ))
        maybe_gen = fn.execute(i, direct=False)
        if inspect.isgenerator(maybe_gen):
            yield from maybe_gen

def op_index(i):
    idx, = i.check_arity(IntegerValue)
    idx = idx.value

    assert idx >= 0

    i.operand_stack.append(i.operand_stack[-1 - idx])

def op_pop(i):
    assert len(i.operand_stack) > 0, 'operand stack underflow'

    i.operand_stack.pop()

def op_print(i):
    v, = i.check_arity(Value)
    i.print(v.__ps_str__())

def op_pstack(i):
    for v in reversed(i.operand_stack):
        i.print(v.__ps_repr__())

def op_roll(i):
    # make sure we have enough arguments
    assert len(i.operand_stack) >= 2, 'operand stack underflow'

    # make sure we have at least as many stack elements as the first argument
    # asks for, after removing the arguments
    assert len(i.operand_stack) - 2 >= i.operand_stack[-2].value, 'operand stack underflow'

    n, j = (v.value for v in i.check_arity(IntegerValue, IntegerValue))

    assert n > 0

    window = deque(list(i.operand_stack)[-n:])

    if j > 0:
        for _ in range(j):
            window.appendleft(window.pop())
    else:
        for _ in range(-j):
            window.append(window.popleft())

    for _ in range(n):
        i.operand_stack.pop()
    i.operand_stack.extend(window)

def op_sub(i):
    lhs, rhs = i.check_arity(IntegerValue, IntegerValue)

    i.operand_stack.append(IntegerValue(
        value=lhs.value - rhs.value,
    ))

core_vocabulary = {
    '=':       op_print,
    'count':   op_count,
    'def':     op_def,
    'exec':    op_exec,
    'for':     op_for,
    'index':   op_index,
    'pop':     op_pop,
    'pstack':  op_pstack,
    'roll':    op_roll,
    'sub':     op_sub,
}

class Interpreter:
    def __init__(self):
        self.operand_stack = deque()
        self.execution_stack = deque()
        self.dictionary_stack = ChainMap(core_vocabulary)

    def _is_building_executable_array(self):
        return any(isinstance(v, StartProcValue) for v in self.operand_stack)

    def look_up(self, name):
        return self.dictionary_stack[name]

    def check_arity(self, *signature):
        assert len(self.operand_stack) >= len(signature), 'operand stack underflow'
        for expected_type, arg in zip(reversed(signature), reversed(self.operand_stack)):
            assert isinstance(arg, expected_type), f'got {type(arg).__name__}, expected {expected_type.__name__}'

        return reversed([ self.operand_stack.pop() for _ in signature ])

    def execute(self, program):
        f = Frame(program)
        self.execution_stack.append(f)

        try:
            for word in program:
                assert f == self.execution_stack[-1] # XXX sanity check

                if self._is_building_executable_array():
                    if isinstance(word, EndProcValue):
                        array = []
                        while not isinstance(self.operand_stack[-1], StartProcValue):
                            array.append(self.operand_stack.pop())
                        line = self.operand_stack[-1].line
                        column = self.operand_stack[-1].column
                        self.operand_stack.pop() # pop the start proc
                        array.reverse()
                        self.operand_stack.append(ArrayValue(
                            value=array,
                            executable=True,
                            line=line,
                            column=column,
                            length=1,
                        ))
                    else:
                        self.operand_stack.append(word)
                else:
                    yield word
                    maybe_gen = word.execute(self, direct=True)
                    if inspect.isgenerator(maybe_gen):
                        yield from maybe_gen
        finally:
            self.execution_stack.pop()
        assert not self._is_building_executable_array() # XXX right?

class SourceCode(Widget):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.highlight_pos = None

    def render(self):
        lines = self.text.splitlines()
        if self.highlight_pos is not None:
            line_no, col_start, col_end = self.highlight_pos
            line = lines[line_no - 1]
            lines[line_no - 1] = ''.join([
                line[:col_start-1],
                '[r]',
                line[col_start-1:col_end-1],
                '[/r]',
                line[col_end-1:],
            ])

        return '\n'.join(lines)

    def highlight(self, line, col_start, col_end):
        self.highlight_pos = (line, col_start, col_end)

class DebuggerApp(App):
    CSS_PATH = 'layout.tcss'

    BINDINGS = [
        ('enter', 'step()', 'Step'),
        ('q', 'quit()', 'Quit'),
    ]

    def compose(self):
        # XXX is this the right place to put this?
        self.interp = Interpreter()

        with open(sys.argv[1], 'r') as f:
            source_code = f.read()
        self.stepper = self.interp.execute(Scanner(io.StringIO(source_code)))

        self.log_widget = Log(classes='output_pane')
        self.log_widget.border_title = 'Output'

        # XXX this is such a hack
        self.interp.print = self.log_widget.write_line

        with Vertical():
            with Horizontal():
                self.src = SourceCode(source_code, classes='box')
                self.src.border_title = 'Code'
                yield self.src

                self.stack_widget = Static('', classes='box')
                self.stack_widget.border_title = 'Stack'
                yield self.stack_widget
            yield self.log_widget
        yield Footer()

    def action_quit(self):
        self.exit()

    def action_step(self):
        next_word = next(self.stepper)
        assert next_word.line is not None, repr(next_word)
        self.src.highlight(line=next_word.line, col_start=next_word.column, col_end=next_word.column+next_word.length)
        self.src.refresh()
        stack_widget_lines = reversed([ v.__ps_repr__() + (f' [grey42]{v.tag}[/grey42]' if v.tag is not None else '') for v in self.interp.operand_stack ])
        self.stack_widget.update('\n'.join(stack_widget_lines))

if __name__ == '__main__':
    app = DebuggerApp()
    app.run()
