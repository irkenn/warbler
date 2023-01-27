from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, URL


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserUpdateForm(FlaskForm):
    """Form for updating fields in the user"""

    username = StringField('Username', validators=[Optional()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    image_url = StringField('Image URL', validators=[Optional(), URL(require_tld=True, message='Please provide a valid URL address or leave the field empty')])
    header_image_url = StringField('Header image URL', validators=[Optional(), URL(require_tld=True, message='Please provide a valid URL address or leave the field empty')])
    bio = StringField('Bio', validators=[Optional()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])

