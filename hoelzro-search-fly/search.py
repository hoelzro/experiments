import contextlib
import sqlite3

from flask import Flask, render_template, request

def create_app(*args):
    app = Flask(__name__)
    app.jinja_options.update(
        variable_start_string='«',
        variable_end_string='»',
    )
    # XXX reload templates

    @app.route('/search')
    def search():
        conn = sqlite3.connect('search-index.db')

        query = request.args.get('q', '')
        matches = []
        if query != '':
            with contextlib.closing(conn.cursor()) as c:
                c.execute('select url, title from pages where pages match ? order by rank', (query,))
                matches = c.fetchall()

        return render_template('search.html', matches=matches)

    return app.wsgi_app(*args)

if __name__ == '__main__':
    app = create_app()
    app.run()
