# Authentication routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.database import db, Admin, Company, Student
from core import hash_password, validate_password_strength

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
        
        if user_type == 'admin':
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.verify_password(password):
                session['user_id'] = admin.admin_id
                session['user_type'] = 'admin'
                session['username'] = admin.username
                session.permanent = True
                flash('Login successful! Welcome Admin.', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
                return render_template('login.html')
        
        elif user_type == 'student':
            student = Student.query.filter_by(email=email).first()
            if student:
                if student.blacklist_status:
                    flash('Your account has been blacklisted', 'danger')
                    return render_template('login.html')
                if student.verify_password(password):
                    session['user_id'] = student.student_id
                    session['user_type'] = 'student'
                    session['username'] = student.name
                    session.permanent = True
                    flash(f'Welcome {student.name}!', 'success')
                    return redirect(url_for('student.student_dashboard'))
                else:
                    flash('Invalid email or password', 'danger')
                    return render_template('login.html')
            else:
                flash('Invalid email or password', 'danger')
                return render_template('login.html')
        
        elif user_type == 'company':
            company = Company.query.filter_by(email=email).first()
            if company:
                if company.blacklist_status:
                    flash('Your company account has been blacklisted', 'danger')
                    return render_template('login.html')
                if company.approval_status != 'Approved':
                    flash(f'Your registration is {company.approval_status}. Please wait for admin approval.', 'warning')
                    return render_template('login.html')
                if company.verify_password(password):
                    session['user_id'] = company.company_id
                    session['user_type'] = 'company'
                    session['username'] = company.company_name
                    session.permanent = True
                    flash(f'Welcome {company.company_name}!', 'success')
                    return redirect(url_for('company.company_dashboard'))
                else:
                    flash('Invalid email or password', 'danger')
                    return render_template('login.html')
            else:
                flash('Invalid email or password', 'danger')
                return render_template('login.html')
    
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
        
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            flash(f'Password Error: {error_msg}', 'danger')
            return redirect(url_for('auth.student_register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.student_register'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.student_register'))
        
        try:
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
        
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            flash(f'Password Error: {error_msg}', 'danger')
            return redirect(url_for('auth.company_register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.company_register'))
        
        if Company.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.company_register'))
        
        try:
            company = Company(
                company_name=company_name,
                email=email,
                hr_contact=hr_contact,
                website=website,
                password=hash_password(password)
            )
            db.session.add(company)
            db.session.commit()
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
        flash('Logged out successfully', 'success')
    return redirect(url_for('auth.homepage'))
