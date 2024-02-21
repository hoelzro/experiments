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
        assert got_values == [expected_value]
