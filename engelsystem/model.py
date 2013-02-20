from engelsystem import db, request
from crypt import crypt
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), nullable=False),
)

role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), nullable=False),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), nullable=False),
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    realname = db.Column(db.String(64))
    password = db.Column(db.String(128), nullable=False)
    hometown = db.Column(db.String(64))
    arrived = db.Column(db.Boolean, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    tshirt = db.Column(db.Boolean, nullable=False)
    locale = db.Column(db.String(2), nullable=False)
    roles = db.relationship('Role', secondary=user_roles,
        backref='users')
    shift_entries = db.relationship('ShiftEntry', backref='user', lazy='dynamic')
    sessions = db.relationship('Session', backref='user', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_auth(self, password):
        return self.password == crypt(password, self.password)

    def has_permission(self, name):
        # XXX: this seems to be doable in SQLAlchemy only, without loops
        perm = Permission.query.filter_by(name=name).first()
        if not perm:
            raise RuntimeError('No such permission: %s' % name)
        for role in self.roles:
            if role in perm.roles:
                return True
        return False

    @staticmethod
    def get_logged_in():
        auth = request.authorization
        if not auth:
            return None
        return User.query.filter_by(username=auth.username).first()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary=role_permissions,
        backref='roles')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True, nullable=False)
    description = db.Column(db.String(256))

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.DateTime, index=True, nullable=False)



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    comment = db.Column(db.String(256))
    visible = db.Column(db.Boolean, nullable=False)
    order = db.Column(db.Integer)
    source = db.Column(db.String(256))
    shifts = db.relationship('Shift', backref='room', lazy='dynamic')
    task_allocations = db.relationship('TaskAllocation', backref='room')
    tasks = association_proxy('task_allocation', 'task')

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), index=True, nullable=False)
    title = db.Column(db.String(64))
    comment = db.Column(db.String(256))
    url = db.Column(db.String(256))
    begin = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    task_allocations = db.relationship('TaskAllocation', backref='shift')
    tasks = association_proxy('task_allocation', 'task')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restricted = db.Column(db.Boolean, nullable=False)
    approvable_by_role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    texts = db.relationship('TaskText', collection_class=attribute_mapped_collection('language'))
    allocation = db.relationship('TaskAllocation', backref='task')

class TaskAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    amount = db.Column(db.Integer, nullable=False)
    assigned = db.relationship('ShiftEntry', backref='task_allocation')
    restricted = association_proxy('task', 'restricted')
    texts = association_proxy('task', 'texts')

class TaskText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    language = db.Column(db.String(2), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(256))

class ShiftEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_allocation_id = db.Column(db.Integer, db.ForeignKey('task_allocation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    freeloaded = db.Column(db.Boolean, nullable=False)

class UserTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    approved = db.Column(db.Boolean, nullable=False)
