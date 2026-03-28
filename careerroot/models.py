#CareerRoot - DB Model

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()


#enums
class ApprovalStatus(Enum):
    #Approval status for companies and drives
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class DriveStatus(Enum):
    #Status of placement drives
    PENDING = "Pending"
    APPROVED = "Approved"
    CLOSED = "Closed"


class ApplicationStatus(Enum):
    #Status of student applications
    APPLIED = "Applied"
    SHORTLISTED = "Shortlisted"
    SELECTED = "Selected"
    REJECTED = "Rejected"


#Admin
class Admin(db.Model):
    #Institute Placement Cell model Pre existing superuser for managing the platform
    __tablename__ = 'admin'
    
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def verify_password(self, password):
        #check if password is correct
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


#Company
class Company(db.Model):
#Company model for recruitment organization  (create drives, view applications, and be managed by admin)
    __tablename__ = 'company'
    
    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    hr_contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    approval_status = db.Column(
        db.String(20),
        default=ApprovalStatus.PENDING.value,
        nullable=False
    )  #pending/aproved/rejected
    blacklist_status = db.Column(db.Boolean, default=False)  # True = blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #relationships
    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def verify_password(self, password):
        #check if password is correct
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Company {self.company_name}>'


#students 
class Student(db.Model):
    #Student model for job seekers (register, apply for drives, and track placement history)
    __tablename__ = 'student'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    resume_path = db.Column(db.String(255), nullable=True)  # Path to uploaded resume
    blacklist_status = db.Column(db.Boolean, default=False)  # True = blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #Relationships
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def verify_password(self, password):
        #check if password is correct
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Student {self.name}>'


#placement drive
class PlacementDrive(db.Model):
    #Placement Drive model (Job Posting) (created by companies, approved by admin Students apply for these drives)
    
    __tablename__ = 'placement_drive'
    
    drive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.String(20),
        default=DriveStatus.PENDING.value,
        nullable=False
    )  # pending, aproved, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #relationships
    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='drive', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Drive {self.job_title} at {self.company_id}>'


#app
class Application(db.Model):
    #Application model - student applying for a placement drive (Tracks application status and prevents duplicate applications)
    
    __tablename__ = 'application'
    
    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.drive_id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(20),
        default=ApplicationStatus.APPLIED.value,
        nullable=False
    )  #Applied, Shortlisted, Selected, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #Relationships
    placement = db.relationship('Placement', backref='application', uselist=False, cascade='all, delete-orphan')
    
    # Unique constraint: one student can only apply once per drive
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),)
    
    def __repr__(self):
        return f'<Application {self.student_id} for Drive {self.drive_id}>'


#placement
class Placement(db.Model):
    #Placement model - tracks final placement/offer of a student
    #Records the successful placement after selection

    __tablename__ = 'placement'
    
    placement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.drive_id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.application_id'), nullable=False)
    selected_date = db.Column(db.DateTime, default=datetime.utcnow)
    salary = db.Column(db.Float, nullable=True)  # Annual salary in LPA
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Placement Student {self.student_id} -> Drive {self.drive_id}>'
