from engelsystem.model import *
from flask import Flask, render_template, request, redirect, url_for, session, Response, g, jsonify
from engelsystem import app
from functools import wraps

@app.before_request
def authenticate():
    key = request.args.get('key', None)
    auth = request.authorization
    g.user = None
    if key:
        session = Session.query.filter_by(id=int(key, 16)).first()
        g.user = session.user
    elif auth:
        user = User.query.filter_by(username=auth.username).first()
        if user and user.verify_auth(auth.password):
            g.user = user

@app.route('/login')
def login():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not (g.user and g.user.has_permission(permission)):
                return login()
            return f(*args, **kwargs)
        return decorated
    return decorator

def api(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if permission and not (g.user and g.user.has_permission(permission)):
                return jsonify(status='error', error='unauth')
            return jsonify(f(*args, **kwargs))
        return decorated
    return decorator

@app.route('/api/user/<username>/read')
@api('show_user')
def user_read(username):
    user = User.query.filter_by(username=username).first_or_404()
    print user.username.__class__
    return dict((k,v) for k,v in user.__dict__.items() if k[0:2] != '__' and v.__class__ in (int,str,unicode,bool) and k != 'password')

@app.route('/user/<username>')
@permission('show_user')
def show_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user)
