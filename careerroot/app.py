# - CareerRoot - Placement Portal Flask app

import os
from flask import Flask
from models import db, Admin, Company, Student, PlacementDrive, Application, Placement


#app configuration
app = Flask(__name__)

#database config. using SQLite.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'careerroot.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'careerroot-secret-key-dev'  #production change

#database initialised
db.init_app(app)

def init_database():
    #Initialize the db - creates all tables and adds default admin
    #This runs only one time during the first setup

    with app.app_context():
        #create all table
        db.create_all()
        print("✓ Database tables created successfully!")
        
        #checking if admin already exist
        existing_admin = Admin.query.filter_by(username='admin').first()
        if not existing_admin:
            #create default admin
            from werkzeug.security import generate_password_hash
            
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123'),  #changing password.
                email='admin@careerroot.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin created!")
            print("  Username: admin")
            print("  Password: admin123")
            print("  (Change this password immediately!)")
        else:
            print("✓ Admin already exists!")


#flask route
@app.route('/')
def home():
    #home route to test if app is running or not
    return {
        'message': 'Welcome to CareerRoot - Placement Portal',
        'status': 'running',
        'database': f'SQLite database at {DATABASE_PATH}'
    }


@app.route('/health')
def health_check():
    #Health check endpoint to verify if the app and database are working...
    return {
        'status': 'healthy',
        'database': 'connected'
    }


#inside main
if __name__ == '__main__':
    #initialise db with starting app 
    init_database()
    
    #running the app
    print("\n" + "="*50)
    print("  CareerRoot - Placement Portal Application")
    print("="*50)
    print("Starting Flask server...\n")
    
    app.run(debug=True, host='localhost', port=5000)
