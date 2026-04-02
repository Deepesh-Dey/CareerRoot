# Chart data calculation and generation utilities using matplotlib

from datetime import datetime, timedelta
from core.database import db, PlacementDrive, Application, Student, Placement, ApplicationStatus
import matplotlib
matplotlib.use('Agg')  # use non-GUI backend for server environment
import matplotlib.pyplot as plt
import os

def get_last_7_days_data():
    # get date range for last 7 days
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=7)
    return seven_days_ago, today

def generate_pie_chart(labels, data, title, filename):
    # generate pie chart image using matplotlib with indigo-violet colors
    chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'images', 'charts')
    
    # create directory if not exists
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    
    filepath = os.path.join(chart_dir, filename)
    
    # filter out zero values to avoid cluttered labels
    filtered_labels = [label for label, value in zip(labels, data) if value > 0]
    filtered_data = [value for value in data if value > 0]
    
    # if all data is zero, show a placeholder
    if not filtered_data:
        filtered_labels = ['No Data']
        filtered_data = [1]
    
    # indigo to violet color palette
    colors = ['#4F46E5', '#6366F1', '#7C3AED', '#9333EA', '#A855F7', '#C084FC'][:len(filtered_labels)]
    
    # create figure and pie chart
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
    ax.pie(filtered_data, labels=filtered_labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 11})
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # save chart
    plt.tight_layout()
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f'/static/images/charts/{filename}'

def get_admin_chart_data():
    # calculate total applications, jobs, and placements for admin dashboard
    seven_days_ago, today = get_last_7_days_data()
    
    # total jobs posted in last 7 days
    total_jobs = PlacementDrive.query.filter(
        PlacementDrive.created_at >= datetime.combine(seven_days_ago, datetime.min.time())
    ).count()
    
    # total applications in last 7 days
    total_applications = Application.query.filter(
        Application.application_date >= datetime.combine(seven_days_ago, datetime.min.time())
    ).count()
    
    # total placements in last 7 days
    total_placements = Placement.query.filter(
        Placement.selected_date >= datetime.combine(seven_days_ago, datetime.min.time())
    ).count()
    
    labels = ['Job Postings', 'Applications', 'Placements']
    data = [total_jobs, total_applications, total_placements]
    
    # generate chart image
    chart_url = generate_pie_chart(labels, data, 'Last 7 Days Activity', 'admin_chart.png')
    
    return chart_url

def get_company_chart_data(company_id):
    # calculate application status distribution for company and generate chart
    company_drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    drive_ids = [drive.drive_id for drive in company_drives]
    
    if not drive_ids:
        # no drives yet, return empty chart
        chart_url = generate_pie_chart(['No Data'], [1], 'Application Status', f'company_{company_id}_chart.png')
        return chart_url
    
    # count applications by status for this company's drives
    applied = Application.query.filter(
        Application.drive_id.in_(drive_ids),
        Application.status == ApplicationStatus.APPLIED.value
    ).count()
    
    shortlisted = Application.query.filter(
        Application.drive_id.in_(drive_ids),
        Application.status == ApplicationStatus.SHORTLISTED.value
    ).count()
    
    selected = Application.query.filter(
        Application.drive_id.in_(drive_ids),
        Application.status == ApplicationStatus.SELECTED.value
    ).count()
    
    rejected = Application.query.filter(
        Application.drive_id.in_(drive_ids),
        Application.status == ApplicationStatus.REJECTED.value
    ).count()
    
    labels = ['Applied', 'Shortlisted', 'Selected', 'Rejected']
    data = [applied, shortlisted, selected, rejected]
    
    # generate chart image
    chart_url = generate_pie_chart(labels, data, 'Application Status Distribution', f'company_{company_id}_chart.png')
    
    return chart_url

def get_student_chart_data(student_id):
    # calculate application status distribution for student and generate chart
    student_applications = Application.query.filter_by(student_id=student_id).all()
    
    if not student_applications:
        # no applications yet, return empty chart
        chart_url = generate_pie_chart(['No Data'], [1], 'Application Status', f'student_{student_id}_chart.png')
        return chart_url
    
    # count applications by each status
    applied = sum(1 for app in student_applications if app.status == ApplicationStatus.APPLIED.value)
    shortlisted = sum(1 for app in student_applications if app.status == ApplicationStatus.SHORTLISTED.value)
    selected = sum(1 for app in student_applications if app.status == ApplicationStatus.SELECTED.value)
    rejected = sum(1 for app in student_applications if app.status == ApplicationStatus.REJECTED.value)
    
    labels = ['Applied', 'Shortlisted', 'Selected', 'Rejected']
    data = [applied, shortlisted, selected, rejected]
    
    # generate chart image
    chart_url = generate_pie_chart(labels, data, 'Application Status Distribution', f'student_{student_id}_chart.png')
    
    return chart_url
