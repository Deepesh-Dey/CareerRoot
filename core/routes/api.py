# REST API endpoints for students, companies, applications, placements

from flask import Blueprint, request, jsonify
from core.database import db, Student, Company, Application, Placement, PlacementDrive

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Student API endpoints
@api_bp.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    data = [{
        'id': s.student_id,
        'name': s.name,
        'email': s.email,
        'department': s.department,
        'cgpa': s.cgpa,
        'blacklisted': s.blacklist_status
    } for s in students]
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    data = {
        'id': student.student_id,
        'name': student.name,
        'email': student.email,
        'phone': student.phone,
        'department': student.department,
        'cgpa': student.cgpa,
        'blacklisted': student.blacklist_status
    }
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'email', 'password', 'department', 'cgpa']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email already exists'}), 400
    
    from core import hash_password
    student = Student(
        name=data['name'],
        email=data['email'],
        password=hash_password(data['password']),
        phone=data.get('phone'),
        department=data['department'],
        cgpa=data['cgpa']
    )
    db.session.add(student)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Student created', 'id': student.student_id}), 201

@api_bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    data = request.get_json()
    student.name = data.get('name', student.name)
    student.phone = data.get('phone', student.phone)
    student.cgpa = data.get('cgpa', student.cgpa)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Student updated'}), 200

@api_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    db.session.delete(student)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Student deleted'}), 200

#Company API endpoints
@api_bp.route('/companies', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    data = [{
        'id': c.company_id,
        'name': c.company_name,
        'email': c.email,
        'website': c.website,
        'status': c.approval_status,
        'blacklisted': c.blacklist_status
    } for c in companies]
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404
    
    data = {
        'id': company.company_id,
        'name': company.company_name,
        'email': company.email,
        'hr_contact': company.hr_contact,
        'website': company.website,
        'status': company.approval_status,
        'blacklisted': company.blacklist_status
    }
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/companies', methods=['POST'])
def create_company():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'email', 'password', 'hr_contact']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    if Company.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email already exists'}), 400
    
    from core import hash_password
    company = Company(
        company_name=data['name'],
        email=data['email'],
        password=hash_password(data['password']),
        hr_contact=data['hr_contact'],
        website=data.get('website')
    )
    db.session.add(company)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Company created', 'id': company.company_id}), 201

@api_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404
    
    data = request.get_json()
    company.company_name = data.get('name', company.company_name)
    company.hr_contact = data.get('hr_contact', company.hr_contact)
    company.website = data.get('website', company.website)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Company updated'}), 200

@api_bp.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404
    
    db.session.delete(company)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Company deleted'}), 200

# Application API endpoints
@api_bp.route('/applications', methods=['GET'])
def get_applications():
    applications = Application.query.all()
    data = [{
        'id': a.application_id,
        'student_id': a.student_id,
        'drive_id': a.drive_id,
        'status': a.status,
        'applied_date': str(a.application_date)
    } for a in applications]
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    app = Application.query.get(app_id)
    if not app:
        return jsonify({'success': False, 'error': 'Application not found'}), 404
    
    data = {
        'id': app.application_id,
        'student_id': app.student_id,
        'drive_id': app.drive_id,
        'status': app.status,
        'applied_date': str(app.application_date)
    }
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/applications', methods=['POST'])
def create_application():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['student_id', 'drive_id']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    student = Student.query.get(data['student_id'])
    drive = PlacementDrive.query.get(data['drive_id'])
    
    if not student or not drive:
        return jsonify({'success': False, 'error': 'Invalid student or drive'}), 404
    
    existing = Application.query.filter_by(student_id=data['student_id'], drive_id=data['drive_id']).first()
    if existing:
        return jsonify({'success': False, 'error': 'Application already exists'}), 400
    
    app = Application(
        student_id=data['student_id'],
        drive_id=data['drive_id'],
        status='Applied'
    )
    db.session.add(app)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Application created', 'id': app.application_id}), 201

@api_bp.route('/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    app = Application.query.get(app_id)
    if not app:
        return jsonify({'success': False, 'error': 'Application not found'}), 404
    
    data = request.get_json()
    if 'status' in data:
        app.status = data['status']
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Application updated'}), 200

@api_bp.route('/applications/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    app = Application.query.get(app_id)
    if not app:
        return jsonify({'success': False, 'error': 'Application not found'}), 404
    
    db.session.delete(app)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Application deleted'}), 200

# Placement API endpoints
@api_bp.route('/placements', methods=['GET'])
def get_placements():
    placements = Placement.query.all()
    data = [{
        'id': p.placement_id,
        'student_id': p.student_id,
        'company_id': p.company_id,
        'salary': p.salary,
        'placed_date': str(p.placement_date)
    } for p in placements]
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/placements/<int:placement_id>', methods=['GET'])
def get_placement(placement_id):
    placement = Placement.query.get(placement_id)
    if not placement:
        return jsonify({'success': False, 'error': 'Placement not found'}), 404
    
    data = {
        'id': placement.placement_id,
        'student_id': placement.student_id,
        'company_id': placement.company_id,
        'salary': placement.salary,
        'placed_date': str(placement.placement_date)
    }
    return jsonify({'success': True, 'data': data}), 200

@api_bp.route('/placements', methods=['POST'])
def create_placement():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['student_id', 'company_id', 'salary']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    student = Student.query.get(data['student_id'])
    company = Company.query.get(data['company_id'])
    
    if not student or not company:
        return jsonify({'success': False, 'error': 'Invalid student or company'}), 404
    
    placement = Placement(
        student_id=data['student_id'],
        company_id=data['company_id'],
        salary=data['salary']
    )
    db.session.add(placement)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Placement created', 'id': placement.placement_id}), 201

@api_bp.route('/placements/<int:placement_id>', methods=['PUT'])
def update_placement(placement_id):
    placement = Placement.query.get(placement_id)
    if not placement:
        return jsonify({'success': False, 'error': 'Placement not found'}), 404
    
    data = request.get_json()
    placement.salary = data.get('salary', placement.salary)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Placement updated'}), 200

@api_bp.route('/placements/<int:placement_id>', methods=['DELETE'])
def delete_placement(placement_id):
    placement = Placement.query.get(placement_id)
    if not placement:
        return jsonify({'success': False, 'error': 'Placement not found'}), 404
    
    db.session.delete(placement)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Placement deleted'}), 200
