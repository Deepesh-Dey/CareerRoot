#forms for authentication - login and registration

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from .models import Student, Company

class StudentRegistrationForm(FlaskForm):
    # Student registration form
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(min=10, max=15)])
    department = StringField('Department', validators=[DataRequired()])
    cgpa = FloatField('CGPA', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        #check if email already exists
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('Email already registered')

class StudentLoginForm(FlaskForm):
    # Student login form
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CompanyRegistrationForm(FlaskForm):
    # Company registration form
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    hr_contact = StringField('HR Contact', validators=[DataRequired()])
    website = StringField('Website', validators=[Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        #check if email already exists
        company = Company.query.filter_by(email=email.data).first()
        if company:
            raise ValidationError('Email already registered')

class CompanyLoginForm(FlaskForm):
    # Company login form
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    # Admin login form
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
