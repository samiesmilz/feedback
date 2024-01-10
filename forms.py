from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Email


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()], render_kw={
                           "placeholder": "Enter your username"})
    password = PasswordField("Password", validators=[InputRequired()], render_kw={
                             "placeholder": "Enter your password"})
    email = EmailField("Email", validators=[InputRequired(), Email()], render_kw={
                       "placeholder": "Enter your email"})
    first_name = StringField("First Name", validators=[InputRequired()], render_kw={
                             "placeholder": "Enter your first name"})
    last_name = StringField("Last Name", render_kw={
                            "placeholder": "Enter your last name"})


class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()], render_kw={
                           "placeholder": "Enter your username"})
    password = PasswordField("Password", validators=[InputRequired()], render_kw={
                             "placeholder": "Enter your password"})


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()], render_kw={
        "placeholder": "Enter your feedback title"})
    content = TextAreaField("Content", validators=[InputRequired()], render_kw={
                            "placeholder": "Enter your feedback content here..."})
