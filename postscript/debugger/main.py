import io
import sys

from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Footer, Log, Static, TextArea

from interpreter import Interpreter, Scanner

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
        try:
            next_word = next(self.stepper)
        except StopIteration:
            self.log_widget.write_line('\nProgram finished.')
            return

        assert next_word.line is not None, repr(next_word)
        self.src.highlight(line=next_word.line, col_start=next_word.column, col_end=next_word.column+next_word.length)
        self.src.refresh()
        stack_widget_lines = reversed([ v.__ps_repr__() + (f' [grey42]{v.tag}[/grey42]' if v.tag is not None else '') for v in self.interp.operand_stack ])
        self.stack_widget.update('\n'.join(stack_widget_lines))

if __name__ == '__main__':
    app = DebuggerApp()
    app.run()
