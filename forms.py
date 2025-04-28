
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

def password_requirements(form, field):
    pw = field.data
    if len(pw) < 4 or len(pw) > 32:
        raise ValidationError('Password must be between 4 and 32 characters.')
    if not any(c.isupper() for c in pw):
        raise ValidationError('Password must have at least one uppercase letter.')
    if not any(c.isdigit() for c in pw):
        raise ValidationError('Password must have at least one number.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), password_requirements])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    submit = SubmitField('Submit Recipe')

class VisitorEmailForm(FlaskForm):
    email = StringField('Enter your Email', validators=[DataRequired(), Email()])
    submit = SubmitField('View Recipes')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=32)])
    bio = StringField('User Bio')
    submit = SubmitField('Update Profile')
                                           
