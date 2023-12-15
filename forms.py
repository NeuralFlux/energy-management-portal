from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, AnyOf

# Set your classes here.


class ServiceLocationForm(FlaskForm):
    unit = TextField(
        'Unit', validators=[DataRequired()]
    )
    address = TextField(
        'Address', validators=[DataRequired(), Length(min=3, max=25)]
    )
    zcode = IntegerField(
        'Zip code', validators=[DataRequired()]
    )
    sq_footage = FloatField('Square Footage')
    num_bedrooms = IntegerField('Number of Bedrooms')
    num_bathrooms = IntegerField('Number of Bathrooms')

class DeviceForm(FlaskForm):
    dev_name = TextField(
        'Name', validators=[DataRequired()]
    )
    model_id = SelectField(
        'Model',
    )
    location_id = SelectField(
        'Location'
    )

class RegisterForm(FlaskForm):
    name = TextField(
        'Username', validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )


class LoginForm(FlaskForm):
    name = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])


class ForgotForm(FlaskForm):
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
