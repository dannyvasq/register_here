
import os
import random
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image

from forms import RegistrationForm, LoginForm, RecipeForm, VisitorEmailForm, ProfileForm
from models import db, User, Recipe, Profile

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def save_resized_image(image_file, filename, size=(300, 300)):
    filepath = os.path.join(app.root_path, 'static/uploads', filename)
    img = Image.open(image_file)
    img.thumbnail(size)  
    img.save(filepath)

def get_placeholder_colors(count):
    colors = [
        "#FF6B6B", "#6BCB77", "#4D96FF", "#FFC75F",
        "#F9F871", "#A393EB", "#FF9671", "#00C9A7",
        "#D65DB1", "#845EC2"
    ]
    random.shuffle(colors)
    return colors[:count]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route('/', methods=['GET','POST'])
def home():
    recipes = Recipe.query.order_by(Recipe.title.asc()).all()
    return render_template('home.html', recipes=recipes)

@app.route('/visitor_recipes')
def visitor_recipes():
    if 'visitor_email' not in session:
        return redirect(url_for('home'))
    search_query = request.args.get('q', '')  
    if search_query:
        recipes = Recipe.query.filter(Recipe.title.ilike(f'%{search_query}%')).all()
    else:
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
    missing_images_count = sum(1 for r in recipes if not r.image_filename)
    placeholder_colors = get_placeholder_colors(missing_images_count)
    return render_template('recipes.html', recipes=recipes, name=current_user.username, placeholder_colors=placeholder_colors)

@app.route('/make_recipe', methods=['GET', 'POST'])
@login_required
def make_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = None

        if image_file:
            filename = secure_filename(image_file.filename)
            save_resized_image(image_file, filename, size=(300,300))

        recipe = Recipe(
            title=form.title.data, 
            description=form.description.data,
            ingredients=form.ingredients.data,  
            instructions=form.instructions.data, 
            user_id=current_user.id
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('recipes'))

    return render_template('new_recipe.html', form=form)

@app.route('/recipe/<int:id>')
def recipe_details(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipe_details.html', recipe=recipe)

@app.route('/edit_recipe/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    
    if recipe.user_id != current_user.id:
        abort(403)

    form = RecipeForm(obj=recipe)
    form.image.label.text = 'Replace Image'

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        
        # Handle new image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            save_resized_image(form.image.data, filename, size=(300, 300))
            recipe.image_filename = filename

        # Handle "remove image" checkbox
        elif form.remove_image.data and recipe.image_filename:
            image_path = os.path.join(app.root_path, 'static/uploads', recipe.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
            recipe.image_filename = None

        db.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipes'))

    return render_template('edit_recipe.html', form=form, recipe=recipe)

@app.route('/delete_recipe/<int:id>', methods=['POST'])
@login_required
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    if recipe.user_id != current_user.id:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully.', 'success')
    return redirect(url_for('recipes'))

@app.route('/user/<int:user_id>/recipes')
@login_required
def user_recipes(user_id):
    user = User.query.get_or_404(user_id)
    recipes = Recipe.query.filter_by(user_id=user.id).order_by(Recipe.title.asc()).all()
    return render_template('user_recipes.html', user=user, recipes=recipes)

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

