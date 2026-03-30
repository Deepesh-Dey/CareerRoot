#CareerRoot - Placement Portal Application
import os
from flask import Flask
from core.database import db
from core.routes import register_routes
from core import hash_password

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'careerroot.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'careerroot-secret-key-dev'

app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
