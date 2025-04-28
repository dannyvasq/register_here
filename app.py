
from flask import Flask, render_template, redirect, url_for, flash, session
from forms import RegistrationForm, LoginForm, RecipeForm, VisitorEmailForm, ProfileForm
from models import db, User, Recipe, Profile
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route('/', methods=['GET','POST'])
def home():
    form = VisitorEmailForm()
    if form.validate_on_submit():
        session['visitor_email'] = form.email.data
        return redirect(url_for('visitor_recipes'))
    return render_template('home.html', form=form)

@app.route('/visitor_recipes')
def visitor_recipes():
    if 'visitor_email' not in session:
        return redirect(url_for('home'))
    recipes = Recipe.query.all()
    return render_template('visitor_recipes.html', recipes=recipes)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('recipes'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/recipes')
@login_required
def recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template('recipes.html', recipes=recipes)

@app.route('/make_recipe', methods=['GET', 'POST'])
@login_required
def make_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()
        return redirect(url_for('recipes'))
    return render_template('new_recipe.html', form=form)

@app.route('/profile', methods=['POST'])
@login_required
def view_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).all()
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html',profile=profile,recipes=recipes)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #update database for display info on profile
    form = ProfileForm()
    if form.validate_on_submit():
        profile = Profile(id=form.id.data, username=form.username.data, bio=form.bio.data, user_id=current_user.id)
        profile.bio = form.bio.data
        db.session.commit()
        flash("Profile updated.")
    return render_template('edit_profile.html',form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.pop('visitor_email', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
       db.create_all()
    app.run(debug=True)

