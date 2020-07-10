from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    """We are going to divide the process of creating forms into three phases: create the form class (in this file),
    create the HTML template and implement the view that performs the function. """
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    title_slug = StringField('Title slug', validators=[Length(max=128)])
    content = TextAreaField('Content')
    submit = SubmitField('Send')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class CommentForm(FlaskForm):
    """
    TRACE (comments) step 1: create form class for comments
    """
    content = TextAreaField('Content', validators=[DataRequired(), ])
    submit = SubmitField('Comment')
