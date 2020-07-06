import json
from os import abort

from flask import Flask, render_template
from flask import request, redirect, url_for
from forms import SignupForm, PostForm, LoginForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
with open('../../Documents/flask.json', 'r') as a:
    keys_dict = json.loads(a.read())
token = keys_dict['token'][0]
uri = keys_dict['uri'][0]

app.config['SECRET_KEY'] = token
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

a.close()

login_manager = LoginManager(app)

# fixme: PREVENTION WARNING ->
# To prevent the application from displaying a 401 error when a user tries to access a protected view,
# the login_manager object needs to be customized as below.

login_manager.login_view = "login"

# We will use Flask-SQLAlchemy, a Flask extension that supports the popular Python ORM SQLAlchemy.
# To integrate Flask-SQLAlchemy in our application we create the SQLAlchemy object and initialize it with
# the instance of our app

db = SQLAlchemy(app)

# The import will be declared just after initializing the db object, otherwise the interpreter will complain
# that it cannot find it.

from models import User, Post

posts = []


@app.route("/")
def index():
    all_posts = Post.get_all()
    return render_template("index.html", posts=all_posts)


@app.route("/p/<string:slug>/")
def show_post(slug):
    post = Post.get_by_slug(slug)
    if post is None:
        abort(404)
    return render_template("post_view.html", post=post)


@app.route("/admin/post/", methods=['GET', 'POST'], defaults={'post_id': None})
@app.route("/admin/post/<int:post_id>/", methods=['GET', 'POST'])
@login_required
def post_form(post_id):
    """
    An administrator user must be authenticated in order to create entries. The way in which Flask-login allows
    protecting access to views only to authenticated users is through the @login_required decorator.
    """
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        post = Post(user_id=current_user.id, title=title, content=content)
        post.save()
        return redirect(url_for('index'))
    return render_template("admin/post_form.html", form=form)


@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    """The error variable is passed to the signup_form.html template. This variable contains an error message in case
    a user already exists. """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Check that there is no longer a user with that email
        user = User.get_by_email(email)
        if user is not None:
            error = f'The email  {email} is already being used by another user'
        else:
            # We create the user and save it
            user = User(name=name, email=email)
            user.set_password(password)
            user.save()
            # We leave the user logged in
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login_form.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
