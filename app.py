
# Import neccesary libraries and modules

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime


# Initialize Flask app and configure database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Load user function for Flask_Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define User model

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy=True)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    email = StringField(validators=[InputRequired(), Length(min=4, max=120)], render_kw={"placeholder":"Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
             raise ValidationError("That username already exists. Please choose a different one.")
   
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()

        if existing_user_email:
             raise ValidationError("That email address already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})

    submit = SubmitField("Login")

# Define Recipe model

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Define RecipeForm class

class RecipeForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(min=1, max=80)], render_kw={"placeholder": "Title"})
    description = TextAreaField(validators=[InputRequired()], render_kw={"placeholder": "Description"})
    ingredients = TextAreaField(validators=[InputRequired()], render_kw={"placeholder": "Ingredients"})
    instructions = TextAreaField(validators=[InputRequired()], render_kw={"placeholder": "Instructions"})
    submit = SubmitField("Add Recipe")


# Route to home page

@app.route('/')
def home():
    return render_template('home.html')


# Route to login

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and  bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('show_recipes'))
    return render_template('login.html', form=form)


# Route to logout

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Route to register a new user

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# Route to show all recipes

@app.route('/recipes')
@login_required
def show_recipes():
    recipes = Recipe.query.filter_by(author=current_user).all()
    return render_template('recipes.html', name=current_user.username, recipes=recipes)


# Route to add a new recipe

@app.route('/recipe/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        try:
            recipe = Recipe(
                title=form.title.data,
                description=form.description.data,
                ingredients=form.ingredients.data,
                instructions=form.instructions.data,
                author=current_user
            )
            db.session.add(recipe)
            db.session.commit()
            flash('Recipe added successfully!', 'success')
            return redirect(url_for('show_recipes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding recipe: {str(e)}', 'danger')
    return render_template('new_recipe.html', form=form)


# Route to show recipe details

@app.route('/recipes/<int:id>')
def recipe_details(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipe_details.html', recipe=recipe)


# Route to delete a recipe

@app.route('/recipe/<int:id>/delete', methods=['POST'])
@login_required
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    if recipe.author != current_user:
        flash('You do not have permission to delete this recipe.', 'danger')
        return redirect(url_for('show_recipes'))
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('show_recipes'))


# Run the Flask app

if __name__ == '__main__':
    app.run(debug=True)
