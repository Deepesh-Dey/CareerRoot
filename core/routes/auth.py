# Authentication routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from core.database import db, Admin, Company, Student
from core import hash_password, validate_password_strength
from core.utils.validators import (
    validate_email, validate_name, validate_phone, validate_cgpa,
    validate_company_name, validate_url, sanitize_input, validate_required_field, validate_hr_contact
)

auth_bp = Blueprint('auth', __name__, url_prefix='')

@auth_bp.route('/')
def homepage():
    if 'user_id' in session:
        user_type = session.get('user_type')
        if user_type == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif user_type == 'company':
            return redirect(url_for('company.company_dashboard'))
        elif user_type == 'student':
            return redirect(url_for('student.student_dashboard'))
    
    return render_template('homepage.html')

@auth_bp.route('/admin/login')
def admin_login_page():
    if 'user_id' in session and session.get('user_type') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin_login_page.html')

@auth_bp.route('/company/login')
def company_login_page():
    if 'user_id' in session and session.get('user_type') == 'company':
        return redirect(url_for('company.company_dashboard'))
    
    return render_template('company_login_page.html')

@auth_bp.route('/student/login')
def student_login_page():
    if 'user_id' in session and session.get('user_type') == 'student':
        return redirect(url_for('student.student_dashboard'))
    
    return render_template('student_login_page.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate required fields
        if not user_type or not password:
            flash('Username/Email and Password are required', 'danger')
            return render_template('login.html')
        
        if user_type == 'admin':
            # Validate username is not empty
            if not username:
                flash('Username is required for admin login', 'danger')
                return render_template('admin_login_page.html')
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.verify_password(password):
                # Use Flask-Login to log in user
                login_user(admin)
                session['user_id'] = admin.admin_id
                session['user_type'] = 'admin'
                session['username'] = admin.username
                session.permanent = True
                flash('Login successful! Welcome Admin.', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
                return render_template('admin_login_page.html')
        
        elif user_type == 'student':
            # Validate email format
            if not email:
                flash('Email is required for student login', 'danger')
                return render_template('student_login_page.html')
            if not validate_email(email):
                flash('Please enter a valid email address', 'danger')
                return render_template('student_login_page.html')
            student = Student.query.filter_by(email=email).first()
            if student:
                if student.blacklist_status:
                    flash('Your account has been blacklisted', 'danger')
                    return render_template('student_login_page.html')
                if student.verify_password(password):
                    # Use Flask-Login to log in user
                    login_user(student)
                    session['user_id'] = student.student_id
                    session['user_type'] = 'student'
                    session['username'] = student.name
                    session.permanent = True
                    flash(f'Welcome {student.name}!', 'success')
                    return redirect(url_for('student.student_dashboard'))
                else:
                    flash('Invalid email or password', 'danger')
                    return render_template('student_login_page.html')
            else:
                flash('Invalid email or password', 'danger')
                return render_template('student_login_page.html')
        
        elif user_type == 'company':
            # Validate email format
            if not email:
                flash('Email is required for company login', 'danger')
                return render_template('company_login_page.html')
            if not validate_email(email):
                flash('Please enter a valid email address', 'danger')
                return render_template('company_login_page.html')
            company = Company.query.filter_by(email=email).first()
            if company:
                if company.blacklist_status:
                    flash('Your company account has been blacklisted', 'danger')
                    return render_template('company_login_page.html')
                if company.approval_status != 'Approved':
                    flash(f'Your registration is {company.approval_status}. Please wait for admin approval.', 'warning')
                    return render_template('company_login_page.html')
                if company.verify_password(password):
                    # Use Flask-Login to log in user
                    login_user(company)
                    session['user_id'] = company.company_id
                    session['user_type'] = 'company'
                    session['username'] = company.company_name
                    session.permanent = True
                    flash(f'Welcome {company.company_name}!', 'success')
                    return redirect(url_for('company.company_dashboard'))
                else:
                    flash('Invalid email or password', 'danger')
                    return render_template('company_login_page.html')
            else:
                flash('Invalid email or password', 'danger')
                return render_template('company_login_page.html')
    
    return render_template('login.html')


@auth_bp.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        cgpa = request.form.get('cgpa')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate required fields
        is_valid, error_msg = validate_required_field(name, 'Name')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        is_valid, error_msg = validate_required_field(email, 'Email')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        is_valid, error_msg = validate_required_field(department, 'Department')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        is_valid, error_msg = validate_required_field(cgpa, 'CGPA')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Validate name format
        is_valid, error_msg = validate_name(name)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Validate email format
        if not validate_email(email):
            flash('Please enter a valid email address', 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Validate phone if provided
        is_valid, error_msg = validate_phone(phone)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Validate CGPA
        is_valid, error_msg = validate_cgpa(cgpa)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            flash(f'Password Error: {error_msg}', 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.student_register'))
        
        # Check if email already exists
        if Student.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.student_register'))
        
        try:
            # Sanitize input data
            name = sanitize_input(name)
            department = sanitize_input(department)
            
            student = Student(
                name=name,
                email=email,
                phone=phone,
                department=department,
                cgpa=float(cgpa),
                password=hash_password(password)
            )
            db.session.add(student)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.student_login_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('student_register.html')


@auth_bp.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        email = request.form.get('email')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate required fields
        is_valid, error_msg = validate_required_field(company_name, 'Company Name')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.company_register'))
        
        is_valid, error_msg = validate_required_field(email, 'Email')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.company_register'))
        
        is_valid, error_msg = validate_required_field(hr_contact, 'HR Contact')
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Validate company name format
        is_valid, error_msg = validate_company_name(company_name)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Validate email format
        if not validate_email(email):
            flash('Please enter a valid email address', 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Validate HR contact name
        is_valid, error_msg = validate_hr_contact(hr_contact)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Validate website URL if provided
        is_valid, error_msg = validate_url(website)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            flash(f'Password Error: {error_msg}', 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.company_register'))
        
        # Check if email already exists
        if Company.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.company_register'))
        
        try:
            # Sanitize input data
            company_name = sanitize_input(company_name)
            hr_contact = sanitize_input(hr_contact)
            
            company = Company(
                company_name=company_name,
                email=email,
                hr_contact=hr_contact,
                website=website,
                password=hash_password(password)
            )
            db.session.add(company)
            db.session.commit()
            flash('Registration successful! Your account is pending admin approval.', 'success')
            return redirect(url_for('auth.company_login_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('company_register.html')


@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        username = session.get('username')
        session.clear()
    # Use Flask-Login to log out user
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.homepage'))
