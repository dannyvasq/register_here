
# Import various field types and validators from wtforms
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

# Define a form class for creating and submitting recipes
class RecipeForm(FlaskForm):

    # Define a title field that is a string and is required
    title = StringField('Title', validators=[DataRequired()])
    
    # Define a description field that is a text area and is required
    description = TextAreaField('Description', validators=[DataRequired()])
    
    # Define an ingredients field that is a text area and is required
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    
    # Define an instructions field that is a text area and is required
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    
    # Define a submit button for the form
    submit = SubmitField('Submit')

