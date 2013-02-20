from flask import Flask, render_template, request, redirect, url_for, session, Response, g, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = 'xahwohpheNg3ShooB3ox'
db = SQLAlchemy(app)
babel = Babel(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = User.get_logged_in()
    if user is not None and user.locale in ('de', 'en'):
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  The best match wins.
    return request.accept_languages.best_match(['de', 'en'])

from model import *
from controller import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shifts')
def shifts():
    rooms = Room.query.all()
    return render_template('shifts.html', rooms=rooms)

if __name__ == "__main__":
    app.run(debug=True)
