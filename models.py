
from flask import Flask
# Imports the Flask class from the flask module

from datetime import datetime
# Imports the datetime class from the datetime module to handle date and time

from flask_sqlalchemy import SQLAlchemy
# Imports the SQLAlchemy class from the flask_sqlalchemy module to handle database operations

app = Flask(__name__)
# Creates an instance of the Flask class
# The __name__ variable is passed to the Flask constructor to determine the root path of the application

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
# Configures the SQLAlchemy database URI
# This sets the database to be used by the application to a SQLite database named recipes.db

app.config['SECRET_KEY'] = 'your_secret_key'
# Sets the secret key for the application
# The secret key is used by Flask and its extensions to keep data safe, such as for session management and CSRF protection

db = SQLAlchemy()
# Creates an instance of the SQLAlchemy class, which will be used to interact with the database

class User(UserMixin, db.Model):
    # Defines a User class that represents the users table in the database
    id = db.Column(db.Integer, primary_key=True)
    # Defines an id column as the primary key, which is an integer and auto-incremented
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Defines a username column that is a string with a maximum length of 80 characters, must be unique, and cannot be null
    password = db.Column(db.String(200), nullable=False)
    # Defines a password column that is a string with a maximum length of 200 characters and cannot be null
    recipes = db.relationship('Recipe', backref='author', lazy=True)
    # Establishes a one-to-many relationship with the Recipe class, where one user can have many recipes
    # The backref attribute adds a virtual column to the Recipe model to access the user who created the recipe

class Recipe(db.Model):
    # Defines a Recipe class that represents the recipes table in the database
    id = db.Column(db.Integer, primary_key=True)
    # Defines an id column as the primary key, which is an integer and auto-incremented
    title = db.Column(db.String(80), nullable=False)
    # Defines a title column that is a string with a maximum length of 80 characters and cannot be null
    description = db.Column(db.Text, nullable=False)
    # Defines a description column that is a text field and cannot be null
    ingredients = db.Column(db.Text, nullable=False)
    # Defines an ingredients column that is a text field and cannot be null
    instructions = db.Column(db.Text, nullable=False)
    # Defines an instructions column that is a text field and cannot be null
    created = db.Column(db.DateTime, default=datetime.utcnow)
    # Defines a created column that stores the date and time the recipe was created, with a default value of the current date and time
    
    def __repr__(self):
        return f'<Recipe {self.title}>'

if __name__=='__main__':
    app.run(debug=True)
