# Routes package - Register all route blueprints

from .auth import auth_bp
from .admin import admin_bp
from .company import company_bp
from .student import student_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    
    # Utility routes
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'database': 'connected'
        }

__all__ = ['register_routes']
