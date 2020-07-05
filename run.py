import json

from flask import Flask, render_template
from flask import request, redirect, url_for
from forms import SignupForm, PostForm

app = Flask(__name__)
with open('../../Documents/flask.json', 'r') as a:
    keys_dict = json.loads(a.read())
token = keys_dict['token'][0]

app.config['SECRET_KEY'] = token
a.close()

posts = []


@app.route("/")
def index():
    return render_template("index.html", posts=posts)


@app.route('/p/<string:slug>/')
def show_post(slug):
    return 'Showing the post {}'.format(slug)


@app.route("/admin/post/", methods=['GET', 'POST'], defaults={'post_id': None})
@app.route("/admin/post/<int:post_id>/", methods=['GET', 'POST'])
def post_form(post_id):
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
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        next = request.args.get('next', None)
        if next:
            return redirect(next)
        return redirect(url_for('index'))
    return render_template("signup_form.html", form=form)
