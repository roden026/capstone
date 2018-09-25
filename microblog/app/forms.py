from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField,SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# This section will be particularly useful for my page
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class SurveyForm(FlaskForm):
    content = TextAreaField('Enter Review Text Here', validators=[Length(min=10, max=500)])
    overall_rating = SelectField('Overall Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'), (6,'6'), (7,'7'), (8,'8'), (9,'9'), (10,'10')],
        coerce=int,
        validators = [DataRequired()])

    type_traveller = SelectField('Type of Traveller',
        choices=[('Business','Business'), ('Couple Leisure','Couple Leisure'), ('FamilyLeisure','Family Leisure'), ('Solo Leisure','Solo Leisure')],
        coerce=str,
        validators = [DataRequired()])

    cabin_flown = SelectField('Cabin Flown',
        choices=[('Business Class','Business Class'), ('Economy','Economy'), ('First Class','First Class'), ('Premium Economy','Premium Economy')],
        coerce=str,
        validators = [DataRequired()])

    seat_comfort_rating = SelectField('Seat Comfort Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    cabin_staff_rating = SelectField('Cabin Staff Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    food_beverages_rating = SelectField('Food Beverage Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    inflight_entertainment_rating = SelectField('Inflight Entertainment Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    ground_service_rating = SelectField('Ground Service Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    wifi_connectivity_rating = SelectField('Wifi Connectivity Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    value_money_rating = SelectField('Value Money Rating',
        choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')],
        coerce=int,
        validators = [DataRequired()])

    submit = SubmitField('Submit')
