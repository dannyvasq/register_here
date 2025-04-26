
from flask import Blueprint, render_template, redirect, url_for, flash, session
from register_here.forms import RegistrationForm, LoginForm, RecipeForm, VisitorEmailForm
from register_here.models import db, User, Recipe
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    form = VisitorEmailForm()
    if form.validate_on_submit():
        session['visitor_email'] = form.email.data
        return redirect(url_for('main.visitor_recipes'))
    return render_template('home.html', form=form)

@bp.route('/visitor_recipes')
def visitor_recipes():
    if 'visitor_email' not in session:
        return redirect(url_for('main.home'))
    recipes = Recipe.query.all()
    return render_template('visitor_recipes.html', recipes=recipes)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # Reminder: should hash passwords
            login_user(user)
            return redirect(url_for('main.recipes'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/recipes')
@login_required
def recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template('recipes.html', recipes=recipes)

@bp.route('/make_recipe', methods=['GET', 'POST'])
@login_required
def make_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()
        return redirect(url_for('main.recipes'))
    return render_template('make_recipe.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    session.pop('visitor_email', None)  # NEW: clear visitor email too
    return redirect(url_for('main.home'))

           

