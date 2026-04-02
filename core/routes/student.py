# Student routes blueprint

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.database import db, Student, Company, PlacementDrive, Application, Placement, ApplicationStatus
from core.utils.chart_data import get_student_chart_data

student_bp = Blueprint('student', __name__, url_prefix='/student')

def check_student():
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'danger')
        return False
    return True


@student_bp.route('/dashboard')
def student_dashboard():
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    # get chart image url for dashboard
    chart_url = get_student_chart_data(student_id)
    
    return render_template('student_dashboard.html', student=student,
                         chart_url=chart_url)


@student_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if request.method == 'POST':
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
            return redirect(url_for('student.student_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('student_profile.html', student=student)

@student_bp.route('/jobs')
def jobs():
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    drives = db.session.query(PlacementDrive).join(
        Company, PlacementDrive.company_id == Company.company_id
    ).filter(
        PlacementDrive.status == 'Approved',
        Company.approval_status == 'Approved'
    ).all()
    
    return render_template('student_view_jobs.html', student=student, drives=drives)


@student_bp.route('/jobs/search', methods=['GET', 'POST'])
def search_jobs():
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
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
    
    return render_template('student_search_jobs.html', student=student, drives=drives, 
                         search_query=search_query, search_type=search_type)


@student_bp.route('/job/<int:drive_id>')
def job_details(drive_id):
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Job not found', 'danger')
        return redirect(url_for('student.jobs'))
    
    company = Company.query.get(drive.company_id)
    student = Student.query.get(session.get('user_id'))
    
    application = Application.query.filter_by(
        student_id=student.student_id,
        drive_id=drive_id
    ).first()
    
    return render_template('student_job_details.html', drive=drive, company=company, 
                         student=student, application=application)


@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
def apply_job(drive_id):
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    # check if student is blacklisted
    if student.blacklist_status:
        flash('Your account has been blacklisted', 'danger')
        return redirect(url_for('student.jobs'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Job not found', 'danger')
        return redirect(url_for('student.jobs'))
    
    # check if student already applied
    existing_app = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first()
    
    if existing_app:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('student.jobs'))
    
    try:
        application = Application(
            student_id=student_id,
            drive_id=drive_id,
            status=ApplicationStatus.APPLIED.value
        )
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('student.applications'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error applying for job: {str(e)}', 'danger')
        return redirect(url_for('student.jobs'))

@student_bp.route('/applications')
def applications():
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    applications = Application.query.filter_by(student_id=student_id).all()
    
    return render_template('student_view_applications.html', student=student, applications=applications)


@student_bp.route('/application/<int:application_id>')
def application_details(application_id):
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    application = Application.query.get(application_id)
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('student.applications'))
    
    if application.student_id != session.get('user_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('student.applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    company = Company.query.get(drive.company_id)
    
    return render_template('student_application_details.html', application=application, 
                         drive=drive, company=company)

@student_bp.route('/placements')
def placements():
    if not check_student():
        return redirect(url_for('auth.homepage'))
    
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    placements = Placement.query.filter_by(student_id=student_id).all()
    
    return render_template('student_placements.html', student=student, placements=placements)
