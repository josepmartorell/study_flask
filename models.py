import datetime

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from run import db

from slugify import slugify
from sqlalchemy.exc import IntegrityError


class User(db.Model, UserMixin):
    __tablename__ = 'blog_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        """
        To avoid a security problem, instead of saving user passwords, we will save a password HASH using the
        werkzeug.security library.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        The check_password method VERIFIES if the hash of the password parameter matches that of the user.
        """
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        """Query operations on gets"""
        return User.query.get(id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()


class Post(db.Model):
    """Up to this point we have implemented all the logic that has to do with blog users. Below we implement
    everything related to posts. """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('blog_user.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    title_slug = db.Column(db.String(256), unique=True, nullable=False)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # TRACE (comments) step 3: add a relationship called comments to easily access its list of comments

    comments = db.relationship(
        'Comment', backref='post', lazy=True, cascade='all, delete-orphan', order_by='asc(Comment.created)')

    def __repr__(self):
        return f'<Post {self.title}>'

    def save(self):
        """We will generate a unique slug of the title automatically using the slugify library."""
        if not self.id:
            db.session.add(self)
        if not self.title_slug:
            self.title_slug = slugify(self.title)
        saved = False
        count = 0
        while not saved:
            try:
                db.session.commit()
                saved = True
            except IntegrityError:
                count += 1
                self.title_slug = f'{slugify(self.title)}-{count}'

    def public_url(self):
        return url_for('show_post', slug=self.title_slug)

    @staticmethod
    def get_by_slug(slug):
        """Query operations on posts"""
        return Post.query.filter_by(title_slug=slug).first()

    @staticmethod
    def get_all():
        return Post.query.all()


class Comment(db.Model):
    """
    TRACE (comments) step 2: add a new model to save in the database the comments
    associated with a post
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('blog_user.id', ondelete='SET NULL'))
    user_name = db.Column(db.String)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, content, user_id=None, user_name=user_name, post_id=None):
        self.content = content
        self.user_id = user_id
        self.user_name = user_name
        self.post_id = post_id

    def __repr__(self):
        return f'<Comment {self.content}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_post_id(post_id):
        return Comment.query.filter_by(post_id=post_id).all()