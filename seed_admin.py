from app.extensions import db
from app.models.user import User
from app import create_app

def seed_admin():
    app = create_app()
    with app.app_context():
        admin_email = "admin@example.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            admin = User(username="admin", email=admin_email, role="admin")
            admin.set_password("admin123") 
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
        else:
            print("⚠️ Admin user already exists.")

if __name__ == "__main__":
    seed_admin()