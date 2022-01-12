from datetime import datetime
from myblog import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from sqlalchemy.orm import validates
import re


class TimestampMixin(object):
    """Model to track creation and update times."""
    created_timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_timestmap = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(UserMixin, db.Model):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=80):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @validates('username')
    def validate_username(self, key, username: str) -> str:
        if re.compile(r'[$-/:-?{-~! "^_`\[\]]').search(username):
            raise AssertionError("You cannot use symbols in your username!")
        return username

    @staticmethod
    def validate_username_static(username: str):
        if re.compile(r'[$-/:-?{-~! "^_`\[\]]').search(username):
            raise AssertionError("You cannot use symbols in your username!")


class Post(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    status = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='original_post',
                               lazy='dynamic')

    def __repr__(self):
        return f'<Post {self.body}>'


class Comment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f'<Comment {self.body}>'
