# Company routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from datetime import datetime
from core.database import db, Company, Student, PlacementDrive, Application, ApplicationStatus
from core.utils.chart_data import get_company_chart_data
from core.utils.validators import validate_job_title, validate_required_field, sanitize_input

company_bp = Blueprint('company', __name__, url_prefix='/company')

def check_company():
    if session.get('user_type') != 'company':
        flash('Unauthorized access', 'danger')
        return False
    return True

@company_bp.route('/dashboard')
@login_required
def company_dashboard():
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    total_applications = 0
    for drive in company.drives:
        total_applications += len(drive.applications)
    
    # get chart image url for dashboard
    chart_url = get_company_chart_data(company_id)
    
    return render_template('company_dashboard.html', company=company, total_applications=total_applications,
                         chart_url=chart_url)

@company_bp.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    # check if company is approved
    if company.approval_status != 'Approved':
        flash('Only approved companies can post jobs', 'danger')
        return redirect(url_for('company.company_dashboard'))
    
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        eligibility_criteria = request.form.get('eligibility_criteria')
        skills_required = request.form.get('skills_required')
        experience_required = request.form.get('experience_required')
        salary_range = request.form.get('salary_range')
        application_deadline = request.form.get('application_deadline')
        
        # Validate required fields
        is_valid, error_msg = validate_required_field(job_title, 'Job Title')
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('company_post_job.html', company=company)
        
        is_valid, error_msg = validate_required_field(job_description, 'Job Description')
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('company_post_job.html', company=company)
        
        is_valid, error_msg = validate_required_field(application_deadline, 'Application Deadline')
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('company_post_job.html', company=company)
        
        # Validate job title format
        is_valid, error_msg = validate_job_title(job_title)
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('company_post_job.html', company=company)
        
        try:
            # Sanitize input data
            job_title = sanitize_input(job_title)
            job_description = sanitize_input(job_description)
            eligibility_criteria = sanitize_input(eligibility_criteria)
            skills_required = sanitize_input(skills_required)
            experience_required = sanitize_input(experience_required)
            salary_range = sanitize_input(salary_range)
            
            # convert application_deadline string to datetime object
            if application_deadline:
                deadline_obj = datetime.strptime(application_deadline, '%Y-%m-%dT%H:%M')
            else:
                deadline_obj = None
            
            # Validate deadline is in future
            if deadline_obj and deadline_obj <= datetime.now():
                flash('Application deadline must be in the future', 'danger')
                return render_template('company_post_job.html', company=company)
            
            # create new placement drive
            from core.database import DriveStatus
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
            return redirect(url_for('company.jobs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')
    
    return render_template('company_post_job.html', company=company)


@company_bp.route('/jobs')
@login_required
def jobs():
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    
    return render_template('company_view_jobs.html', company=company, drives=drives)


@company_bp.route('/job/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(drive_id):
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    drive = PlacementDrive.query.get(drive_id)
    
    if not drive or drive.company_id != company_id:
        flash('Job not found', 'danger')
        return redirect(url_for('company.jobs'))
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        
        if new_status in ['Approved', 'Closed']:
            drive.status = new_status
            db.session.commit()
            flash(f'Job status updated to {new_status}.', 'success')
        else:
            flash('Invalid status', 'danger')
        
        return redirect(url_for('company.jobs'))
    
    return render_template('company_edit_job.html', drive=drive)


@company_bp.route('/applications')
@login_required
def applications():
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    applications = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.drive_id
    ).filter(PlacementDrive.company_id == company_id).all()
    
    return render_template('company_view_applications.html', company=company, applications=applications)


@company_bp.route('/application/<int:application_id>/shortlist', methods=['POST'])
@login_required
def shortlist_application(application_id):
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    application = Application.query.get(application_id)
    
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company.applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != company_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company.applications'))
    
    application.status = ApplicationStatus.SHORTLISTED.value
    db.session.commit()
    
    flash('Student shortlisted successfully!', 'success')
    return redirect(url_for('company.applications'))


@company_bp.route('/application/<int:application_id>/interview', methods=['POST'])
@login_required
def interview_application(application_id):
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    application = Application.query.get(application_id)
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company.applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != session.get('user_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('company.applications'))
    
    try:
        application.status = ApplicationStatus.INTERVIEW.value
        application.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Marked for interview', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('company.applications'))


@company_bp.route('/application/<int:application_id>/select', methods=['POST'])
@login_required
def select_application(application_id):
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    application = Application.query.get(application_id)
    
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company.applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != company_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company.applications'))
    
    application.status = ApplicationStatus.SELECTED.value
    db.session.commit()
    
    flash('Student selected successfully!', 'success')
    return redirect(url_for('company.applications'))


@company_bp.route('/application/<int:application_id>/reject', methods=['POST'])
@login_required
def reject_application(application_id):
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    application = Application.query.get(application_id)
    
    if not application:
        flash('Application not found', 'danger')
        return redirect(url_for('company.applications'))
    
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != company_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company.applications'))
    
    application.status = ApplicationStatus.REJECTED.value
    db.session.commit()
    
    flash('Application rejected.', 'success')
    return redirect(url_for('company.applications'))


@company_bp.route('/shortlisted')
@login_required
def shortlisted():
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    company_id = session.get('user_id')
    company = Company.query.get(company_id)
    
    applications = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.drive_id
    ).filter(
        PlacementDrive.company_id == company_id,
        Application.status == ApplicationStatus.SHORTLISTED.value
    ).all()
    
    return render_template('company_shortlisted.html', company=company, applications=applications)


@company_bp.route('/student/<int:student_id>')
@login_required
def view_student(student_id):
    if not check_company():
        return redirect(url_for('auth.homepage'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('company.company_dashboard'))
    
    company_id = session.get('user_id')
    
    applications = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.drive_id
    ).filter(
        Application.student_id == student_id,
        PlacementDrive.company_id == company_id
    ).all()
    
    return render_template('company_student_profile.html', student=student, applications=applications)
