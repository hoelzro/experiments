import io
import sys

from rich.segment import Segment
from rich.style import Style
from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.geometry import Size
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.widgets import Footer, Log, Static

from interpreter import Interpreter, Scanner

class SourceCode(ScrollView):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.lines = text.splitlines()
        self.virtual_size = Size(max(len(line) for line in self.lines), len(self.lines))
        self.highlight_pos = None

    def render_line(self, y: int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        idx = scroll_y + y
        if idx >= len(self.lines):
            return Strip.blank(self.virtual_size.width)

        target_line = self.lines[idx]

        match self.highlight_pos:
            case (line_no, col_start, col_end):
                if (line_no - 1) == idx:
                    segments = [Segment(target_line[:col_start-1]), Segment(target_line[col_start-1:col_end-1], Style(reverse=True)), Segment(target_line[col_end-1:])]
                else:
                    segments = [Segment(target_line)]
            case None:
                segments = [Segment(target_line)]

        strip = Strip(segments)
        strip.crop(scroll_x, scroll_x + self.size.width)
        return strip

    def highlight(self, line, col_start, col_end):
        self.highlight_pos = (line, col_start, col_end)

    def unhilight(self):
        self.highlight_pos = None

    def scroll_into_view(self, line, column):
        line -= 1
        column -= 1

        if self.scroll_offset.y <= line <= (self.size.height + self.scroll_offset.y):
            return

        self.scroll_to(y=line)

class DebuggerApp(App):
    CSS_PATH = 'layout.tcss'

    BINDINGS = [
        ('enter', 'step()', 'Step'),
        ('q', 'quit()', 'Quit'),
    ]

    def __init__(self, source_filename, **kwargs):
        super().__init__(**kwargs)
        self.source_filename = source_filename

    def compose(self):
        # XXX is this the right place to put this?
        self.interp = Interpreter()

        with open(self.source_filename, 'r') as f:
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

                with Vertical():
                    self.stack_widget = Static('', classes='stack_widget')
                    self.stack_widget.border_title = 'Stack'
                    yield self.stack_widget

                    self.graphics_state_widget = Static('', classes='graphics_state_widget')
                    self.graphics_state_widget.border_title = 'Graphics State'
                    yield self.graphics_state_widget
            yield self.log_widget
        yield Footer()

    def action_quit(self):
        self.exit()

    def action_step(self):
        try:
            next_word = next(self.stepper)
        except StopIteration:
            self.log_widget.write_line('\nProgram finished.')
            next_word = None

        if next_word is not None:
            assert next_word.line is not None, repr(next_word)
            # XXX what if the next_word doesn't have a line property?
            self.src.highlight(line=next_word.line, col_start=next_word.column, col_end=next_word.column+next_word.length)
            self.src.scroll_into_view(next_word.line, next_word.column)
        else:
            self.src.unhilight()

        self.src.refresh()
        stack_widget_lines = reversed([ v.__ps_repr__() + (f' [grey42]{v.tag}[/grey42]' if v.tag is not None else '') for v in self.interp.operand_stack ])
        self.stack_widget.update('\n'.join(stack_widget_lines))
        self.graphics_state_widget.update(self.interp._describe_graphics_state())

if __name__ == '__main__':
    mode = 'run'
    source_filename = None

    for arg in sys.argv[1:]:
        if arg == '--tokens':
            mode = 'dump_tokens'
        elif arg == '--interactive':
            mode = 'interactive'
        elif arg == '--run':
            mode = 'run'
        elif arg.startswith('-'):
            raise Exception(f'unrecognized flag {arg!r}')
        else:
            source_filename = arg

    match mode:
        case 'dump_tokens':
            with open(source_filename, 'r') as f:
                for w in Scanner(f):
                    print(w)
        case 'interactive':
            app = DebuggerApp(source_filename)
            app.run()
        case 'run':
            t = Interpreter()
            t.print = print
            with open(source_filename, 'r') as f:
                for _ in t.execute(Scanner(f)):
                    pass
        case _:
            raise Exception(f'invalid mode {mode!r}')
