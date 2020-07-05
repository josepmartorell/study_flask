import json

from flask import Flask, render_template
from flask import request, redirect, url_for
from forms import SignupForm, PostForm, LoginForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import User, users
from werkzeug.urls import url_parse

app = Flask(__name__)
with open('../../Documents/flask.json', 'r') as a:
    keys_dict = json.loads(a.read())
token = keys_dict['token'][0]

app.config['SECRET_KEY'] = token
a.close()

login_manager = LoginManager(app)

# fixme: PREVENTION WARNING ->
# To prevent the application from displaying a 401 error when a user tries to access a protected view,
# the login_manager object needs to be customized as below.

login_manager.login_view = "login"

posts = []


@app.route("/")
def index():
    return render_template("index.html", posts=posts)


@app.route('/p/<string:slug>/')
def show_post(slug):
    return 'Showing the post {}'.format(slug)


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
        title_slug = form.title_slug.data
        content = form.content.data

        post = {'title': title, 'title_slug': title_slug, 'content': content}
        posts.append(post)

        return redirect(url_for('index'))
    return render_template("admin/post_form.html", form=form)


@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # We create the user and save it
        user = User(len(users) + 1, name, email, password)
        users.append(user)
        # We leave the user logged in
        login_user(user, remember=True)
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("signup_form.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user(form.email.data)
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
