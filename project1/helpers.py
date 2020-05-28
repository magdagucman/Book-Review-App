from flask import redirect, render_template, request, session, url_for
from functools import wraps

# A function called when error occurs
def error(message, code):
    return render_template("apology.html", code=code, message=message)

def login_required(f):
    #Decorate routes to require login. Based on: http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
