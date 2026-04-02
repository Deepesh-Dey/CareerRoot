# Admin routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.database import db, Admin, Company, Student, PlacementDrive, Application
from core.utils.chart_data import get_admin_chart_data

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_admin():
    if session.get('user_type') != 'admin':
        flash('Unauthorized access', 'danger')
        return False
    return True

@admin_bp.route('/dashboard')
def admin_dashboard():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    
    # get chart image url for dashboard
    chart_url = get_admin_chart_data()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         total_companies=total_companies,
                         total_drives=total_drives,
                         total_applications=total_applications,
                         chart_url=chart_url)

@admin_bp.route('/companies/pending')
def approve_companies():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    pending_companies = Company.query.filter_by(approval_status='Pending').all()
    return render_template('admin_approve_companies.html', companies=pending_companies)

@admin_bp.route('/company/approve/<int:company_id>', methods=['POST'])
def approve_company(company_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found', 'danger')
        return redirect(url_for('admin.approve_companies'))
    
    company.approval_status = 'Approved'
    db.session.commit()
    flash(f'{company.company_name} approved successfully!', 'success')
    
    return redirect(url_for('admin.approve_companies'))

@admin_bp.route('/company/reject/<int:company_id>', methods=['POST'])
def reject_company(company_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found', 'danger')
        return redirect(url_for('admin.approve_companies'))
    
    company.approval_status = 'Rejected'
    db.session.commit()
    flash(f'{company.company_name} rejected.', 'warning')
    
    return redirect(url_for('admin.approve_companies'))

@admin_bp.route('/drives/pending')
def approve_drives():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    pending_drives = PlacementDrive.query.filter_by(status='Pending').all()
    return render_template('admin_approve_drives.html', drives=pending_drives)


@admin_bp.route('/drive/approve/<int:drive_id>', methods=['POST'])
def approve_drive(drive_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Drive not found', 'danger')
        return redirect(url_for('admin.approve_drives'))
    
    drive.status = 'Approved'
    db.session.commit()
    flash(f'{drive.job_title} approved successfully!', 'success')
    
    return redirect(url_for('admin.approve_drives'))


@admin_bp.route('/drive/reject/<int:drive_id>', methods=['POST'])
def reject_drive(drive_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        flash('Drive not found', 'danger')
        return redirect(url_for('admin.approve_drives'))
    
    db.session.delete(drive)
    db.session.commit()
    flash(f'{drive.job_title} rejected.', 'warning')
    
    return redirect(url_for('admin.approve_drives'))

@admin_bp.route('/students')
def view_students():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    all_students = Student.query.all()
    return render_template('admin_view_students.html', students=all_students)

@admin_bp.route('/companies')
def view_companies():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    all_companies = Company.query.all()
    return render_template('admin_view_companies.html', companies=all_companies)

@admin_bp.route('/drives')
def view_drives():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    all_drives = PlacementDrive.query.all()
    return render_template('admin_view_drives.html', drives=all_drives)

@admin_bp.route('/applications')
def view_applications():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    all_applications = Application.query.all()
    return render_template('admin_view_applications.html', applications=all_applications)

@admin_bp.route('/student/<int:student_id>')
def view_student(student_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    applications = Application.query.filter_by(student_id=student_id).all()
    return render_template('admin_student_profile.html', student=student, applications=applications)

@admin_bp.route('/search', methods=['GET', 'POST'])
def search():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    search_results = []
    search_type = None
    search_query = None
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')  
        search_query = request.form.get('search_query')
        
        if search_type == 'student' and search_query:
            search_results = Student.query.filter(
                (Student.name.ilike(f'%{search_query}%')) |
                (Student.email.ilike(f'%{search_query}%')) |
                (Student.phone.ilike(f'%{search_query}%'))
            ).all()
        
        elif search_type == 'company' and search_query:
            search_results = Company.query.filter(
                (Company.company_name.ilike(f'%{search_query}%')) |
                (Company.email.ilike(f'%{search_query}%'))
            ).all()
    
    return render_template('admin_search.html', 
                         results=search_results, 
                         search_type=search_type, 
                         search_query=search_query)


@admin_bp.route('/blacklist')
def blacklist():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    blacklisted_students = Student.query.filter_by(blacklist_status=True).all()
    blacklisted_companies = Company.query.filter_by(blacklist_status=True).all()
    
    return render_template('admin_blacklist.html', 
                         students=blacklisted_students, 
                         companies=blacklisted_companies)


@admin_bp.route('/blacklist/student/<int:student_id>', methods=['POST'])
def blacklist_student(student_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin.blacklist'))
    
    student.blacklist_status = not student.blacklist_status
    db.session.commit()
    
    if student.blacklist_status:
        flash(f'{student.name} has been blacklisted.', 'warning')
    else:
        flash(f'{student.name} has been removed from blacklist.', 'success')
    
    return redirect(url_for('admin.blacklist'))


@admin_bp.route('/blacklist/company/<int:company_id>', methods=['POST'])
def blacklist_company(company_id):
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found', 'danger')
        return redirect(url_for('admin.blacklist'))
    
    company.blacklist_status = not company.blacklist_status
    db.session.commit()
    
    if company.blacklist_status:
        flash(f'{company.company_name} has been blacklisted.', 'warning')
    else:
        flash(f'{company.company_name} has been removed from blacklist.', 'success')
    
    return redirect(url_for('admin.blacklist'))

@admin_bp.route('/placements')
def placements():
    if not check_admin():
        return redirect(url_for('auth.homepage'))
    
    from core.database import Placement
    placements = Placement.query.all()
    return render_template('admin_placements.html', placements=placements)
