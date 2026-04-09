"""
DriftDater - Flask-WTF Forms for input validation
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    IntegerField, BooleanField, DateField, FloatField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange,
    Optional, ValidationError
)
from datetime import date


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegistrationForm(FlaskForm):
    username  = StringField('Username',  validators=[DataRequired(), Length(3, 64)])
    email     = StringField('Email',     validators=[DataRequired(), Email(), Length(max=128)])
    password  = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name  = StringField('Last Name',  validators=[DataRequired(), Length(max=64)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender    = SelectField('Gender', choices=[
        ('male', 'Male'), ('female', 'Female'),
        ('non-binary', 'Non-Binary'), ('other', 'Other')
    ], validators=[DataRequired()])
    looking_for = SelectField('Looking For', choices=[
        ('any', 'Any'), ('male', 'Male'), ('female', 'Female'),
        ('non-binary', 'Non-Binary')
    ], default='any')

    def validate_date_of_birth(self, field):
        if field.data:
            today = date.today()
            age = today.year - field.data.year - (
                (today.month, today.day) < (field.data.month, field.data.day)
            )
            if age < 18:
                raise ValidationError('You must be at least 18 years old to register.')
            if age > 120:
                raise ValidationError('Please enter a valid date of birth.')


class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class ProfileForm(FlaskForm):
    first_name      = StringField('First Name',  validators=[Optional(), Length(max=64)])
    last_name       = StringField('Last Name',   validators=[Optional(), Length(max=64)])
    bio             = TextAreaField('Bio',        validators=[Optional(), Length(max=1000)])
    parish          = StringField('Parish',       validators=[Optional(), Length(max=64)])
    city            = StringField('City',         validators=[Optional(), Length(max=64)])
    country         = StringField('Country',      validators=[Optional(), Length(max=64)])
    latitude        = FloatField('Latitude',      validators=[Optional()])
    longitude       = FloatField('Longitude',     validators=[Optional()])
    occupation      = StringField('Occupation',   validators=[Optional(), Length(max=128)])
    education_level = SelectField('Education Level', choices=[
        ('', 'Prefer not to say'),
        ('high_school', 'High School'),
        ('associate', "Associate's Degree"),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('doctorate', 'Doctorate'),
        ('other', 'Other'),
    ], validators=[Optional()])
    preferred_age_min = IntegerField('Min Age', validators=[Optional(), NumberRange(18, 99)])
    preferred_age_max = IntegerField('Max Age', validators=[Optional(), NumberRange(18, 99)])
    preferred_radius  = IntegerField('Search Radius (km)',
                                     validators=[Optional(), NumberRange(1, 10000)])
    looking_for     = SelectField('Looking For', choices=[
        ('any', 'Any'), ('male', 'Male'), ('female', 'Female'), ('non-binary', 'Non-Binary')
    ], validators=[Optional()])
    is_public       = BooleanField('Public Profile', default=True)
    photo           = FileField('Profile Photo',
                                validators=[Optional(),
                                            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'],
                                                        'Images only!')])


# ---------------------------------------------------------------------------
# Like / Pass
# ---------------------------------------------------------------------------

class LikeForm(FlaskForm):
    action = SelectField('Action', choices=[('like', 'Like'), ('pass', 'Pass')],
                         validators=[DataRequired()])


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class MessageForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=2000)])


# ---------------------------------------------------------------------------
# Search / Filter
# ---------------------------------------------------------------------------

class SearchForm(FlaskForm):
    q               = StringField('Search',       validators=[Optional()])
    parish          = StringField('Parish',       validators=[Optional()])
    country         = StringField('Country',      validators=[Optional()])
    age_min         = IntegerField('Min Age',     validators=[Optional(), NumberRange(18, 99)])
    age_max         = IntegerField('Max Age',     validators=[Optional(), NumberRange(18, 99)])
    interests       = StringField('Interests',    validators=[Optional()])  # comma-separated
    gender          = SelectField('Gender', choices=[
        ('', 'Any'), ('male', 'Male'), ('female', 'Female'),
        ('non-binary', 'Non-Binary'), ('other', 'Other')
    ], validators=[Optional()])
    sort            = SelectField('Sort By', choices=[
        ('newest', 'Newest'), ('match_score', 'Best Match')
    ], default='newest', validators=[Optional()])
