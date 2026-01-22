"""
Create admin user for the Ride-Share application
Run this after the server is started
"""
from app import app, db, User

def create_admin():
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@rideshare.com').first()
        
        if admin:
            print(f"✅ Admin user already exists!")
            print(f"   Email: admin@rideshare.com")
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print(f"   Updated to admin privileges")
        else:
            # Create new admin
            admin = User(
                username='admin',
                email='admin@rideshare.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print(f"   Email: admin@rideshare.com")
            print(f"   Password: admin123")
        
        print("\n🔐 Login at: http://localhost:5000/login")
        print("   After login, you'll be automatically redirected to admin panel\n")

if __name__ == '__main__':
    create_admin()
