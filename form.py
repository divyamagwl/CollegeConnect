from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, PasswordField, StringField
from wtforms import validators, ValidationError
from wtforms.validators import InputRequired, Length, Email, EqualTo


class RegisterForm(FlaskForm):
    username = StringField("Username",validators=[InputRequired(), Length(min=4,max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', message="Passwords do not match")])
    submit = SubmitField('Register now')

class LoginForm(FlaskForm):
    username = TextField("Username",validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField('Login now')

class AddForm(FlaskForm):
    aimsTowards = TextField("To")
    description = TextAreaField("Post description", validators=[InputRequired()])
    author = TextField("Author of the Post (optional) :") 
    submit = SubmitField('Submit')
