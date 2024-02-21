from collections import deque, ChainMap
from dataclasses import dataclass
import functools
import inspect
import itertools

import types
import typing
from typing import Optional, Self

class Frame:
    '''
    A stack frame on the execution stack
    '''
    def __init__(self, program):
        self.program = iter(program)

@dataclass(eq=False)
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

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

@dataclass(eq=False)
class MarkValue(Value):
    value: any = None
    def execute(self, i, direct):
        # XXX I *think* it should be ok just to push ourselves onto the stack?
        i.operand_stack.append(self)

    def __ps_str__(self):
        return '-mark-'

    def __ps_repr__(self):
        return '-mark-'

@dataclass(eq=False)
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

@dataclass(eq=False)
class StringValue(Value):
    value: str

    def execute(self, i, direct):
        i.operand_stack.append(self)

    def __ps_repr__(self):
        return '(' + self.value + ')'

@dataclass(eq=False)
class IntegerValue(Value):
    value: int

    def execute(self, i, direct):
        i.operand_stack.append(self)

@dataclass(eq=False)
class RealValue(Value):
    value: float

    def execute(self, i, direct):
        i.operand_stack.append(self)

@dataclass(eq=False)
class ArrayValue(Value):
    value: list[Value]
    args: list[str] = None

    def execute(self, i, direct):
        if self.executable and not direct:
            # executing an executable array…executes it
            restore_tags = None
            try:
                if self.args:
                    restore_tags = []
                    for new_tag, value in zip(reversed(self.args), reversed(i.operand_stack)):
                        restore_tags.append((value, value.tag))
                        value.tag = new_tag
                yield from i.execute(self)
            finally:
                if restore_tags:
                    for v, old_tag in restore_tags:
                        v.tag = old_tag
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
@dataclass(eq=False)
class StartProcValue(Value):
    value: any = None
    args: list[str] = None

    def execute(self, i, direct):
        # XXX I *think* it should be ok just to push ourselves onto the stack?
        i.operand_stack.append(self)

@dataclass(eq=False)
class EndProcValue(Value):
    value: any = None

@dataclass(eq=False)
class StubValue(Value):
    value: any = None

TYPE_MAPPING = {
    int: IntegerValue,
    float: RealValue,
    str: NameValue | StringValue,
}

def print_value(v, indent=0):
    print('  ' * indent, type(v).__name__, end='', sep='')
    if isinstance(v, ArrayValue):
        print('')
        for subvalue in v.value:
            print_value(subvalue, indent=indent+1)
    else:
        print('', v.value)

DELIMITERS = {
    '(',
    ')',
    '<',
    '>',
    '[',
    ']',
    '{',
    '}',
    '/',
    '%',
}

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
                    comment = comment[1:]

                if comment.startswith('tag '):
                    tag = comment.removeprefix('tag ')
                if comment.startswith('args '):
                    args = comment.removeprefix('args ').split(' ')

            col_no = 1

            while True:
                stripped = line.lstrip()
                col_no += len(line) - len(stripped)
                line = stripped
                if line == '':
                    break

                if line.startswith('/'):
                    idx = 1
                    while idx < len(line) and not line[idx].isspace() and not line[idx] in DELIMITERS:
                        idx += 1
                    yield NameValue(value=line[1:idx], line=line_no, column=col_no, length=idx, tag=tag)
                    line = line[idx:]
                    col_no += idx
                elif line[0] == '{':
                    assert len(line) == 1 or line[1].isspace()
                    yield StartProcValue(line=line_no, column=col_no, length=1, tag=tag, args=args)
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
                    while idx < len(line) and (line[idx].isdigit() or line[idx] == '.'):
                        idx += 1
                    if '.' in line[:idx]:
                        yield RealValue(value=float(line[:idx]), line=line_no, column=col_no, length=idx, tag=tag)
                    else:
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
                elif line[0:2] == '<<':
                    assert len(line) == 2 or line[2].isspace()
                    yield NameValue(value='<<', line=line_no, column=col_no, length=2, tag=tag, executable=True)
                    line = line[2:]
                    col_no += 2
                elif line[0:2] == '>>':
                    assert len(line) == 2 or line[2].isspace()
                    yield NameValue(value='>>', line=line_no, column=col_no, length=2, tag=tag, executable=True)
                    line = line[2:]
                    col_no += 2
                else:
                    raise NotImplementedError(f"can't handle rest of line {line!r}")

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
        retvals = []
        for expected_type, arg in zip(reversed(signature), reversed(self.operand_stack)):
            if isinstance(expected_type, types.UnionType):
                valid_types = typing.get_args(expected_type)
            else:
                valid_types = (expected_type,)

            unwrap = not any(issubclass(t, Value) for t in valid_types)

            if any(issubclass(t, Value) for t in valid_types):
                assert all(issubclass(t, Value) for t in valid_types), 'if any of the types are Value subclasses, all of them must be'
            else:
                valid_types = tuple(itertools.chain.from_iterable(typing.get_args(TYPE_MAPPING[t]) if isinstance(TYPE_MAPPING[t], types.UnionType) else (TYPE_MAPPING[t],) for t in valid_types))

            assert isinstance(arg, valid_types), f'got {type(arg).__name__}, expected any of {", ".join(t.__name__ for t in valid_types)}'
            retvals.append(arg.value if unwrap else arg)

        # we didn't want to alter the stack unless everything looks good - now that we know that, we
        # can pop the values we've gathered
        for _ in signature:
            self.operand_stack.pop()

        return reversed(retvals)

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
                        start_proc_word = self.operand_stack.pop() # pop the start proc
                        array.reverse()
                        self.operand_stack.append(ArrayValue(
                            value=array,
                            executable=True,
                            line=start_proc_word.line,
                            column=start_proc_word.column,
                            length=1,
                            tag=word.tag,
                            args=start_proc_word.args,
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

def postscript_function(fn):
    expected_types = [ param.annotation for param in inspect.signature(fn).parameters.values() if param.name != 'i' ]

    @functools.wraps(fn)
    def wrapper(i):
        args = i.check_arity(*expected_types)

        return fn(i, *args)

    return wrapper

@postscript_function
def op_add(i: Interpreter, lhs: int|float, rhs: int|float):
    res = lhs + rhs
    if isinstance(res, float):
        i.operand_stack.append(RealValue(
            value=res,
        ))
    else:
        i.operand_stack.append(IntegerValue(
            value=res,
        ))

@postscript_function
def op_copy(i: Interpreter, n: int):
    for _ in range(n):
        i.operand_stack.append(i.operand_stack[-n])

def op_count(i: Interpreter):
    i.operand_stack.append(IntegerValue(value=len(i.operand_stack)))

@postscript_function
def op_def(i: Interpreter, name: str, value: Value):
    i.dictionary_stack[name] = value

def op_dup(i: Interpreter):
    i.operand_stack.append(i.operand_stack[-1])

@postscript_function
def op_exch(i: Interpreter, lhs: Value, rhs: Value):
    i.operand_stack.append(rhs)
    i.operand_stack.append(lhs)

@postscript_function
def op_exec(i: Interpreter, fn: ArrayValue):
    return fn.execute(i, direct=False)

@postscript_function
def op_for(i: Interpreter, init: int, incr: int, limit: int, fn: ArrayValue):
    for j in range(init, limit+1, incr):
        i.operand_stack.append(IntegerValue(
            value=j,
        ))
        maybe_gen = fn.execute(i, direct=False)
        if inspect.isgenerator(maybe_gen):
            yield from maybe_gen

@postscript_function
def op_index(i: Interpreter, idx: int):
    assert idx >= 0

    i.operand_stack.append(i.operand_stack[-1 - idx])

@postscript_function
def op_mul(i: Interpreter, lhs: int|float, rhs: int|float):
    res = lhs * rhs

    if isinstance(res, float):
        i.operand_stack.append(RealValue(
            value=res,
        ))
    else:
        i.operand_stack.append(IntegerValue(
            value=res,
        ))

def op_pop(i: Interpreter):
    assert len(i.operand_stack) > 0, 'operand stack underflow'

    i.operand_stack.pop()

@postscript_function
def op_print(i: Interpreter, v: Value):
    i.print(v.__ps_str__())

def op_pstack(i: Interpreter):
    for v in reversed(i.operand_stack):
        i.print(v.__ps_repr__())

def op_ptags(i: Interpreter):
    for v in reversed(i.operand_stack):
        i.print(str(v.tag))

def op_roll(i: Interpreter):
    # make sure we have enough arguments
    assert len(i.operand_stack) >= 2, 'operand stack underflow'

    # make sure we have at least as many stack elements as the first argument
    # asks for, after removing the arguments
    assert len(i.operand_stack) - 2 >= i.operand_stack[-2].value, 'operand stack underflow'

    n, j = i.check_arity(int, int)

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

# XXX return value (XXX would that mess with generators/stepping?)
@postscript_function
def op_sub(i: Interpreter, lhs: int|float, rhs: int|float):
    res = lhs - rhs
    if isinstance(res, float):
        i.operand_stack.append(RealValue(
            value=res,
        ))
    else:
        i.operand_stack.append(IntegerValue(
            value=res,
        ))

def stub(nargs: int, nret: int = 0):
    def stub_function(i: Interpreter):
        for _ in range(nargs):
            i.operand_stack.pop()
        for _ in range(nret):
            i.operand_stack.append(StubValue())

    return stub_function

core_vocabulary = {
    '=':            op_print,
    'add':          op_add,
    'copy':         op_copy,
    'count':        op_count,
    'currentpoint': stub(0, 2),
    'def':          op_def,
    'dup':          op_dup,
    'exch':         op_exch,
    'exec':         op_exec,
    'findfont':     stub(1, 1),
    'for':          op_for,
    'index':        op_index,
    'lineto':       stub(2),
    'moveto':       stub(2),
    'mul':          op_mul,
    'newpath':      stub(0),
    'pop':          op_pop,
    'pstack':       op_pstack,
    'ptags':        op_ptags,
    'rlineto':      stub(2),
    'rmoveto':      stub(2),
    'roll':         op_roll,
    'scalefont':    stub(2, 1),
    'setfont':      stub(1),
    'setlinewidth': stub(1),
    'setrgbcolor':  stub(3),
    'show':         stub(1),
    'showpage':     stub(0),
    'stroke':       stub(0),
    'sub':          op_sub,
}
