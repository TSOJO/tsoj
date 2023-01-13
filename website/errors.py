from flask import render_template
from flask.typing import ResponseReturnValue

def page_not_found(e) -> ResponseReturnValue:
    return render_template('404.html', description=e.description), 404

def unauthorised(e):
    return render_template('403.html', description=e.description), 403
