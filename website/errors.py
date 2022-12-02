from flask import render_template

def page_not_found(e: int) -> tuple[str, int]:
    return render_template('404.html'), 404
