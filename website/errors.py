from flask import render_template
from flask.typing import ResponseReturnValue

def page_not_found(e: int) -> ResponseReturnValue:
    return render_template('404.html'), 404
