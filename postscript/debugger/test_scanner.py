import dataclasses
import io

from .interpreter import IntegerValue, NameValue, RealValue
from .interpreter import Scanner

EXAMPLES = [
    ('/foo', NameValue(value='foo')),
    ('17', IntegerValue(value=17)),
    ('0.16', RealValue(value=0.16)),
    ('/push3', NameValue(value='push3')),
    ('/Times-Roman', NameValue(value='Times-Roman')),
]

def test_scans():
    for program, expected_value in EXAMPLES:
        expected_value.line = 1
        expected_value.column = 1
        expected_value.length = len(program)

        got_values = list(Scanner(io.StringIO(program)))
        assert [ dataclasses.asdict(v) for v in got_values ] == [ dataclasses.asdict(expected_value) ]

def test_dictionary():
    got_values = list(Scanner(io.StringIO('<< /south true /west true /east true >>')))
    expected_values = [
        NameValue(value='<<', line=1, column=1, length=2, executable=True),
        NameValue(value='south', line=1, column=4, length=6),
        NameValue(value='true', line=1, column=11, length=4, executable=True),
        NameValue(value='west', line=1, column=16, length=5),
        NameValue(value='true', line=1, column=22, length=4, executable=True),
        NameValue(value='east', line=1, column=27, length=5),
        NameValue(value='true', line=1, column=33, length=4, executable=True),
        NameValue(value='>>', line=1, column=38, length=2, executable=True),
    ]

    assert [ dataclasses.asdict(v) for v in got_values ] == [ dataclasses.asdict(v) for v in expected_values ]

def test_array():
    got_values = list(Scanner(io.StringIO('[ /foo 17 ]')))
    expected_values = [
        NameValue(value='[', line=1, column=1, length=1, executable=True),
        NameValue(value='foo', line=1, column=3, length=4),
        IntegerValue(value=17, line=1, column=8, length=2),
        NameValue(value=']', line=1, column=11, length=1, executable=True),
    ]

    assert [ dataclasses.asdict(v) for v in got_values ] == [ dataclasses.asdict(v) for v in expected_values ]
