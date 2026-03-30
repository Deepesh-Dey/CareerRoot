#CareerRoot - Placement Portal Flask app with authentication

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Admin, Company, Student, PlacementDrive, Application, Placement, ApplicationStatus, DriveStatus
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
def homepage():
    #home page landing
    if 'user_id' in session:
        user_type = session.get('user_type')
        if user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user_type == 'company':
            return redirect(url_for('company_dashboard'))
        elif user_type == 'student':
            return redirect(url_for('student_dashboard'))
    
    return render_template('homepage.html')


@app.route('/admin/login')
def admin_login_page():
    #admin login page
    if 'user_id' in session and session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_login_page.html')


@app.route('/company/login')
def company_login_page():
    #company login and register page
    if 'user_id' in session and session.get('user_type') == 'company':
        return redirect(url_for('company_dashboard'))
    
    return render_template('company_login_page.html')


@app.route('/student/login')
def student_login_page():
    #student login and register page
    if 'user_id' in session and session.get('user_type') == 'student':
        return redirect(url_for('student_dashboard'))
    
    return render_template('student_login_page.html')


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
                    return redirect(url_for('homepage'))
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
                    return redirect(url_for('homepage'))
                if company.approval_status != 'Approved':
                    flash(f'Your registration is {company.approval_status}. Please wait for admin approval.', 'warning')
                    return redirect(url_for('homepage'))
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
            return redirect(url_for('homepage'))
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
            return redirect(url_for('homepage'))
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
    return redirect(url_for('homepage'))


#dashboard routes
@app.route('/admin/dashboard')
def admin_dashboard():
    #admin dashboard
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
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
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    return render_template('company_dashboard.html', company=company)


@app.route('/student/dashboard')
def student_dashboard():
    #student dashboard
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    return render_template('student_dashboard.html', student=student)


#admin management routes

@app.route('/admin/companies/pending')
def admin_approve_companies():
    # show companies waiting for approval
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all pending companies
    pending_companies = Company.query.filter_by(approval_status='Pending').all()
    
    return render_template('admin_approve_companies.html', companies=pending_companies)


@app.route('/admin/company/approve/<int:company_id>', methods=['POST'])
def approve_company(company_id):
    # approve a company registration
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found', 'danger')
        return redirect(url_for('admin_approve_companies'))
    
    # change status to approved
    company.approval_status = 'Approved'
    db.session.commit()
    flash(f'{company.company_name} approved successfully!', 'success')
    
    return redirect(url_for('admin_approve_companies'))


@app.route('/admin/company/reject/<int:company_id>', methods=['POST'])
def reject_company(company_id):
    # reject a company registration
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found', 'danger')
        return redirect(url_for('admin_approve_companies'))
    
    # change status to rejected
    company.approval_status = 'Rejected'
    db.session.commit()
    flash(f'{company.company_name} rejected.', 'warning')
    
    return redirect(url_for('admin_approve_companies'))


@app.route('/admin/drives/pending')
def admin_approve_drives():
    # show placement drives waiting for approval
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all pending drives with company info
    pending_drives = PlacementDrive.query.filter_by(status='Pending').all()
    
    return render_template('admin_approve_drives.html', drives=pending_drives)


@app.route('/admin/drive/approve/<int:drive_id>', methods=['POST'])
def approve_drive(drive_id):
    # approve a placement drive
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Drive not found', 'danger')
        return redirect(url_for('admin_approve_drives'))
    
    # change status to approved
    drive.status = 'Approved'
    db.session.commit()
    flash(f'{drive.job_title} approved successfully!', 'success')
    
    return redirect(url_for('admin_approve_drives'))


@app.route('/admin/drive/reject/<int:drive_id>', methods=['POST'])
def reject_drive(drive_id):
    # reject a placement drive
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Drive not found', 'danger')
        return redirect(url_for('admin_approve_drives'))
    
    # change status back to pending (reject)
    # note: this is a simple reject, in production you might delete or mark as rejected
    db.session.delete(drive)
    db.session.commit()
    flash(f'{drive.job_title} rejected.', 'warning')
    
    return redirect(url_for('admin_approve_drives'))


@app.route('/admin/students')
def admin_view_students():
    # view all students
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all students
    all_students = Student.query.all()
    
    return render_template('admin_view_students.html', students=all_students)


@app.route('/admin/companies')
def admin_view_companies():
    # view all companies
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all companies
    all_companies = Company.query.all()
    
    return render_template('admin_view_companies.html', companies=all_companies)


@app.route('/admin/drives')
def admin_view_drives():
    # view all placement drives
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all drives
    all_drives = PlacementDrive.query.all()
    
    return render_template('admin_view_drives.html', drives=all_drives)


@app.route('/admin/applications')
def admin_view_applications():
    # view all applications
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all applications with related data
    all_applications = Application.query.all()
    
    return render_template('admin_view_applications.html', applications=all_applications)


@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    # search for students or companies
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    search_results = []
    search_type = None
    search_query = None
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')  
        search_query = request.form.get('search_query')
        
        if search_type == 'student' and search_query:
            # search students by name, email, or student_id
            search_results = Student.query.filter(
                (Student.name.ilike(f'%{search_query}%')) |
                (Student.email.ilike(f'%{search_query}%')) |
                (Student.phone.ilike(f'%{search_query}%'))
            ).all()
        
        elif search_type == 'company' and search_query:
            # search companies by name or email
            search_results = Company.query.filter(
                (Company.company_name.ilike(f'%{search_query}%')) |
                (Company.email.ilike(f'%{search_query}%'))
            ).all()
    
    return render_template('admin_search.html', 
                         results=search_results, 
                         search_type=search_type, 
                         search_query=search_query)


@app.route('/admin/blacklist')
def admin_blacklist():
    # manage blacklisted users
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    # get all blacklisted students and companies
    blacklisted_students = Student.query.filter_by(blacklist_status=True).all()
    blacklisted_companies = Company.query.filter_by(blacklist_status=True).all()
    
    return render_template('admin_blacklist.html', 
                         students=blacklisted_students, 
                         companies=blacklisted_companies)


@app.route('/admin/blacklist/student/<int:student_id>', methods=['POST'])
def blacklist_student(student_id):
    # blacklist or unblacklist a student
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin_blacklist'))
    
    # toggle blacklist status
    student.blacklist_status = not student.blacklist_status
    db.session.commit()
    
    if student.blacklist_status:
        flash(f'{student.name} has been blacklisted.', 'warning')
    else:
        flash(f'{student.name} has been removed from blacklist.', 'success')
    
    return redirect(url_for('admin_blacklist'))


@app.route('/admin/blacklist/company/<int:company_id>', methods=['POST'])
def blacklist_company(company_id):
    # blacklist or unblacklist a company
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found', 'danger')
        return redirect(url_for('admin_blacklist'))
    
    # toggle blacklist status
    company.blacklist_status = not company.blacklist_status
    db.session.commit()
    
    if company.blacklist_status:
        flash(f'{company.company_name} has been blacklisted.', 'warning')
    else:
        flash(f'{company.company_name} has been removed from blacklist.', 'success')
    
    return redirect(url_for('admin_blacklist'))


#company job management routes
@app.route('/company/post-job', methods=['GET', 'POST'])
def company_post_job():
    # company post new job
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    # check if company is approved
    if company.approval_status != 'Approved':
        flash('Only approved companies can post jobs', 'danger')
        return redirect(url_for('company_dashboard'))
    
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        eligibility_criteria = request.form.get('eligibility_criteria')
        skills_required = request.form.get('skills_required')
        experience_required = request.form.get('experience_required')
        salary_range = request.form.get('salary_range')
        application_deadline = request.form.get('application_deadline')
        
        try:
            #convert application_deadline string to datetime object
            if application_deadline:
                deadline_obj = datetime.strptime(application_deadline, '%Y-%m-%dT%H:%M')
            else:
                deadline_obj = None
            
            #create new placement drive
            drive = PlacementDrive(
                company_id=company_id,
                job_title=job_title,
                job_description=job_description,
                eligibility_criteria=eligibility_criteria,
                skills_required=skills_required,
                experience_required=experience_required,
                salary_range=salary_range,
                application_deadline=deadline_obj,
                status=DriveStatus.PENDING.value
            )
            db.session.add(drive)
            db.session.commit()
            flash('Job posted successfully! Waiting for admin approval.', 'success')
            return redirect(url_for('company_jobs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')
    
    return render_template('company_post_job.html', company=company)


@app.route('/company/jobs')
def company_jobs():
    # view all jobs posted by company
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    # get all drives posted by this company
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    
    return render_template('company_view_jobs.html', company=company, drives=drives)


@app.route('/company/job/<int:drive_id>/edit', methods=['GET', 'POST'])
def company_edit_job(drive_id):
    # edit job posting status (active/closed)
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    drive = PlacementDrive.query.get(drive_id)
    
    if not drive or drive.company_id != company_id:
        flash('Job not found', 'danger')
        return redirect(url_for('company_jobs'))
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        
        if new_status in ['Approved', 'Closed']:
            drive.status = new_status
            db.session.commit()
            flash(f'Job status updated to {new_status}.', 'success')
        else:
            flash('Invalid status', 'danger')
        
        return redirect(url_for('company_jobs'))
    
    return render_template('company_edit_job.html', drive=drive)


@app.route('/company/applications')
def company_applications():
    # view all applications for jobs posted by company
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    # get all applications for this company's drives
    applications = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.drive_id
    ).filter(PlacementDrive.company_id == company_id).all()
    
    return render_template('company_view_applications.html', company=company, applications=applications)


@app.route('/company/application/<int:application_id>/shortlist', methods=['POST'])
def company_shortlist_application(application_id):
    # shortlist a student for a job
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    application = Application.query.get(application_id)
    
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company_applications'))
    
    # verify company owns this drive
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != company_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company_applications'))
    
    # update status
    application.status = ApplicationStatus.SHORTLISTED.value
    db.session.commit()
    
    flash('Student shortlisted successfully!', 'success')
    return redirect(url_for('company_applications'))


@app.route('/company/application/<int:application_id>/select', methods=['POST'])
def company_select_application(application_id):
    # select a student for final placement
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    application = Application.query.get(application_id)
    
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company_applications'))
    
    # verify company owns this drive
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != company_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company_applications'))
    
    # update status
    application.status = ApplicationStatus.SELECTED.value
    db.session.commit()
    
    flash('Student selected successfully!', 'success')
    return redirect(url_for('company_applications'))


@app.route('/company/application/<int:application_id>/reject', methods=['POST'])
def company_reject_application(application_id):
    # reject a student application
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    application = Application.query.get(application_id)
    
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company_applications'))
    
    # verify company owns this drive
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != company_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company_applications'))
    
    # update status
    application.status = ApplicationStatus.REJECTED.value
    db.session.commit()
    
    flash('Application rejected.', 'success')
    return redirect(url_for('company_applications'))


@app.route('/company/shortlisted')
def company_shortlisted():
    # view shortlisted candidates
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    # get all shortlisted applications for this company's drives
    applications = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.drive_id
    ).filter(
        PlacementDrive.company_id == company_id,
        Application.status == ApplicationStatus.SHORTLISTED.value
    ).all()
    
    return render_template('company_shortlisted.html', company=company, applications=applications)


#student job management routes

@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    # student profile update
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if request.method == 'POST':
        # update student profile
        name = request.form.get('name')
        phone = request.form.get('phone')
        department = request.form.get('department')
        cgpa = request.form.get('cgpa')
        
        try:
            student.name = name
            student.phone = phone
            student.department = department
            student.cgpa = float(cgpa) if cgpa else None
            db.session.commit()
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('student_profile.html', student=student)


@app.route('/student/jobs')
def student_jobs():
    # search and view approved job postings
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    # get all approved drives from approved companies
    drives = db.session.query(PlacementDrive).join(
        Company, PlacementDrive.company_id == Company.company_id
    ).filter(
        PlacementDrive.status == 'Approved',
        Company.approval_status == 'Approved'
    ).all()
    
    return render_template('student_view_jobs.html', student=student, drives=drives)


@app.route('/student/jobs/search', methods=['GET', 'POST'])
def student_search_jobs():
    # search jobs by company, position, or skills
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    search_query = request.form.get('search_query', '')
    search_type = request.form.get('search_type', 'position')  # position, company, skills
    
    drives = []
    
    if search_query:
        if search_type == 'position':
            # search by job title
            drives = db.session.query(PlacementDrive).join(
                Company, PlacementDrive.company_id == Company.company_id
            ).filter(
                PlacementDrive.status == 'Approved',
                Company.approval_status == 'Approved',
                PlacementDrive.job_title.ilike(f'%{search_query}%')
            ).all()
        
        elif search_type == 'company':
            # search by company name
            drives = db.session.query(PlacementDrive).join(
                Company, PlacementDrive.company_id == Company.company_id
            ).filter(
                PlacementDrive.status == 'Approved',
                Company.approval_status == 'Approved',
                Company.company_name.ilike(f'%{search_query}%')
            ).all()
        
        elif search_type == 'skills':
            # search by skills
            drives = db.session.query(PlacementDrive).join(
                Company, PlacementDrive.company_id == Company.company_id
            ).filter(
                PlacementDrive.status == 'Approved',
                Company.approval_status == 'Approved',
                PlacementDrive.skills_required.ilike(f'%{search_query}%')
            ).all()
    
    return render_template('student_search_jobs.html', student=student, drives=drives, search_query=search_query, search_type=search_type)


@app.route('/student/apply/<int:drive_id>', methods=['POST'])
def student_apply_job(drive_id):
    # apply for a job
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    # check if student is blacklisted
    if student.blacklist_status:
        flash('Your account has been blacklisted', 'danger')
        return redirect(url_for('student_jobs'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Job not found', 'danger')
        return redirect(url_for('student_jobs'))
    
    # check if student already applied
    existing_app = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first()
    
    if existing_app:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('student_jobs'))
    
    try:
        # create application
        application = Application(
            student_id=student_id,
            drive_id=drive_id,
            status=ApplicationStatus.APPLIED.value
        )
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('student_applications'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error applying for job: {str(e)}', 'danger')
        return redirect(url_for('student_jobs'))


@app.route('/student/applications')
def student_applications():
    # view applied jobs and their status
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    # get all applications for this student
    applications = Application.query.filter_by(student_id=student_id).all()
    
    return render_template('student_view_applications.html', student=student, applications=applications)


@app.route('/student/job/<int:drive_id>')
def student_job_details(drive_id):
    # view job details
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Job not found', 'danger')
        return redirect(url_for('student_jobs'))
    
    company = Company.query.get(drive.company_id)
    student = Student.query.get(session.get('user_id'))
    
    # check if student already applied
    application = Application.query.filter_by(
        student_id=student.student_id,
        drive_id=drive_id
    ).first()
    
    return render_template('student_job_details.html', drive=drive, company=company, student=student, application=application)


#Milestone 6: Application History and Status Tracking

@app.route('/company/application/<int:application_id>/interview', methods=['POST'])
def company_interview_application(application_id):
    # mark application for interview
    if session.get('user_type') != 'company':
        flash('Unauthorized', 'danger')
        return redirect(url_for('homepage'))
    
    application = Application.query.get(application_id)
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company_applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != session.get('user_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('company_applications'))
    
    try:
        application.status = ApplicationStatus.INTERVIEW.value
        application.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Marked for interview', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('company_applications'))


@app.route('/admin/student/<int:student_id>')
def admin_view_student(student_id):
    # admin view student profile and applications
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # get all applications for this student
    applications = Application.query.filter_by(student_id=student_id).all()
    
    return render_template('admin_student_profile.html', student=student, applications=applications)


@app.route('/company/student/<int:student_id>')
def company_view_student(student_id):
    # company view student profile
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('company_dashboard'))
    
    company_id = session.get('user_id')
    
    # get applications to this company jobs only
    applications = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.drive_id
    ).filter(
        Application.student_id == student_id,
        PlacementDrive.company_id == company_id
    ).all()
    
    return render_template('company_student_profile.html', student=student, applications=applications)


@app.route('/admin/placements')
def admin_placements():
    # view all placements
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    placements = Placement.query.all()
    return render_template('admin_placements.html', placements=placements)


@app.route('/student/placements')
def student_placements():
    # view own placements
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    # get all placements for this student
    placements = Placement.query.filter_by(student_id=student_id).all()
    
    return render_template('student_placements.html', student=student, placements=placements)


@app.route('/student/application/<int:application_id>')
def student_application_details(application_id):
    # view application details
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('homepage'))
    
    application = Application.query.get(application_id)
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('student_applications'))
    
    # check if it belongs to logged in student
    if application.student_id != session.get('user_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('student_applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    company = Company.query.get(drive.company_id)
    
    return render_template('student_application_details.html', application=application, drive=drive, company=company)


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
