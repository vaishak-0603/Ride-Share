"""
Fix admin user - Updates existing admin user or creates new one
"""

from app import app, db, User

def fix_admin_user():
    with app.app_context():
        # Try to find admin by email first
        admin = User.query.filter_by(email='admin@rideshare.com').first()
        
        if admin:
            # User exists with this email - update password and ensure admin flag
            print(f"Found user with email admin@rideshare.com")
            print(f"  Username: {admin.username}")
            admin.is_admin = True
            admin.set_password('admin123')
            db.session.commit()
            print("✅ Updated existing user to admin with password 'admin123'")
        else:
            # No user with this email - check if username 'admin' exists
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                # Username exists - update it
                print(f"Found user with username 'admin'")
                print(f"  Email: {admin.email}")
                admin.is_admin = True
                admin.set_password('admin123')
                db.session.commit()
                print(f"✅ Updated user '{admin.username}' to admin")
                print(f"   Email: {admin.email}")
                print(f"   Password: admin123")
            else:
                # Create new admin user
                admin = User(
                    username='admin',
                    email='admin@rideshare.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Created new admin user")
                print("   Email: admin@rideshare.com")
                print("   Password: admin123")
        
        print("\n🔐 Login at: http://localhost:5000/login")
        print(f"   Email: {admin.email}")
        print("   Password: admin123")

if __name__ == '__main__':
    fix_admin_user()
