#CareerRoot - Placement Portal Application
import os
from flask import Flask
from flask_login import LoginManager
from core.database import db
from core.routes import register_routes
from core import hash_password

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')

DATABASE_PATH = os.path.join(BASE_DIR, 'careerroot.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'careerroot-secret-key-dev'

app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from core.database.models import Admin, Company, Student
    # Try to find user in Admin table
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    # Try to find user in Company table
    company = Company.query.get(int(user_id))
    if company:
        return company
    # Try to find user in Student table
    student = Student.query.get(int(user_id))
    if student:
        return student
    return None

db.init_app(app)
register_routes(app)


def init_database():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
        from core.database import Admin
        existing_admin = Admin.query.filter_by(username='admin').first()
        if not existing_admin:
            admin = Admin(
                username='admin',
                password=hash_password('Admin@123'),
                email='admin@careerroot.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("\nDefault admin created!")
            print("  Username: admin")
            print("  Password: Admin@123\n")
        else:
            print("✓ Admin already exists!\n")


if __name__ == '__main__':
    init_database()
    
    print("=" * 50)
    print("  CareerRoot - Placement Portal Application")
    print("=" * 50)
    print("Starting Flask server...\n")
    
    app.run(debug=True, host='localhost', port=5000)
