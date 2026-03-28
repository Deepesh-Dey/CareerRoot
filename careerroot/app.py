#CareerRoot - Placement Portal Flask app with authentication

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Admin, Company, Student, PlacementDrive, Application, Placement
from forms import StudentLoginForm, StudentRegistrationForm, CompanyLoginForm, CompanyRegistrationForm, AdminLoginForm
from auth import validate_password_strength, hash_password, verify_password


#app configuration
app = Flask(__name__)

#database config. using SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'careerroot.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'careerroot-secret-key-dev'  #production change

#database initialised
db.init_app(app)

#session config
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  #24 hrs
app.config['SESSION_COOKIE_SECURE'] = False  #set true in production for https
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

def init_database():
    #Initialize the db - creates all tables and adds default admin
    #This runs only one time during the first setup
    with app.app_context():
        #create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        #checking if admin already exist
        existing_admin = Admin.query.filter_by(username='admin').first()
        if not existing_admin:
            #create default admin
            
            admin = Admin(
                username='admin',
                password=hash_password('Admin@123'),  #changing password required
                email='admin@careerroot.com'
            )
            db.session.add(admin)
            db.session.commit()
            print(" Default admin created!")
            print("  Username: admin")
            print("  Password: Admin@123")
            print("  (Change this password in production!)")
        else:
            print("✓ Admin already exists!")


#routes
@app.route('/')
def home():
    #home page
    if 'user_id' in session:
        user_type = session.get('user_type')
        if user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user_type == 'company':
            return redirect(url_for('company_dashboard'))
        elif user_type == 'student':
            return redirect(url_for('student_dashboard'))
    
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    #login page for all user types - student, company, and admin
    if request.method == 'POST':
        user_type = request.form.get('user_type')  #student, company, admin
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        #admin login
        if user_type == 'admin':
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.verify_password(password):
                session['user_id'] = admin.admin_id
                session['user_type'] = 'admin'
                session['username'] = admin.username
                session.permanent = True
                flash('Login successful! Welcome Admin.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        
        #student login
        elif user_type == 'student':
            student = Student.query.filter_by(email=email).first()
            if student:
                if student.blacklist_status:
                    flash('Your account has been blacklisted', 'danger')
                    return redirect(url_for('login'))
                if student.verify_password(password):
                    session['user_id'] = student.student_id
                    session['user_type'] = 'student'
                    session['username'] = student.name
                    session.permanent = True
                    flash(f'Welcome {student.name}!', 'success')
                    return redirect(url_for('student_dashboard'))
            flash('Invalid email or password', 'danger')
        
        #company login
        elif user_type == 'company':
            company = Company.query.filter_by(email=email).first()
            if company:
                if company.blacklist_status:
                    flash('Your company account has been blacklisted', 'danger')
                    return redirect(url_for('login'))
                if company.approval_status != 'Approved':
                    flash(f'Your registration is {company.approval_status}. Please wait for admin approval.', 'warning')
                    return redirect(url_for('login'))
                if company.verify_password(password):
                    session['user_id'] = company.company_id
                    session['user_type'] = 'company'
                    session['username'] = company.company_name
                    session.permanent = True
                    flash(f'Welcome {company.company_name}!', 'success')
                    return redirect(url_for('company_dashboard'))
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')


@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    #student registration
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        cgpa = request.form.get('cgpa')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        #validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            flash(f'Password Error: {error_msg}', 'danger')
            return redirect(url_for('student_register'))
        
        #check password match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('student_register'))
        
        #check if email already exists
        if Student.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('student_register'))
        
        try:
            #create new student
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
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('student_register.html')


@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    #company registration
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        email = request.form.get('email')
        hr_contact = request.form.get('hr_contact')
        website = request.form.get('website')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        #validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            flash(f'Password Error: {error_msg}', 'danger')
            return redirect(url_for('company_register'))
        
        #check password match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('company_register'))
        
        #check if email already exists
        if Company.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('company_register'))
        
        try:
            #create new company
            company = Company(
                company_name=company_name,
                email=email,
                hr_contact=hr_contact,
                website=website,
                password=hash_password(password)
            )
            db.session.add(company)
            db.session.commit()
            flash('Registration successful! Please wait for admin approval before you can login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('company_register.html')


@app.route('/logout')
def logout():
    #logout user
    if 'user_id' in session:
        username = session.get('username')
        session.clear()
        flash(f'Logged out successfully', 'success')
    return redirect(url_for('login'))


#dashboard routes
@app.route('/admin/dashboard')
def admin_dashboard():
    #admin dashboard
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         total_companies=total_companies,
                         total_drives=total_drives,
                         total_applications=total_applications)


@app.route('/company/dashboard')
def company_dashboard():
    #company dashboard
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    return render_template('company_dashboard.html', company=company)


@app.route('/student/dashboard')
def student_dashboard():
    #student dashboard
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    return render_template('student_dashboard.html', student=student)


@app.route('/health')
def health_check():
    #health check
    return {
        'status': 'healthy',
        'database': 'connected'
    }


if __name__ == '__main__':
    #init database
    init_database()
    
    print("\n" + "="*50)
    print("  CareerRoot - Placement Portal Application")
    print("="*50)
    print("Starting Flask server...\n")
    
    app.run(debug=True, host='localhost', port=5000)
