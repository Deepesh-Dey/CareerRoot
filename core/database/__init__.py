# Import database models and forms for easy access
from .models import (
    db, Admin, Company, Student, 
    PlacementDrive, Application, Placement,
    ApprovalStatus, DriveStatus, ApplicationStatus
)
from .forms import (
    StudentLoginForm, StudentRegistrationForm,
    CompanyLoginForm, CompanyRegistrationForm,
    AdminLoginForm
)

__all__ = [
    'db', 'Admin', 'Company', 'Student',
    'PlacementDrive', 'Application', 'Placement',
    'ApprovalStatus', 'DriveStatus', 'ApplicationStatus',
    'StudentLoginForm', 'StudentRegistrationForm',
    'CompanyLoginForm', 'CompanyRegistrationForm',
    'AdminLoginForm'
]
