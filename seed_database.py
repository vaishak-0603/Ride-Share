"""
Database seeding script for Ride-Share application.
This script ensures essential data exists in the database.
Run this after database initialization to set up admin users and default data.
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def seed_admin_user():
    """Create default admin user if doesn't exist."""
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@rideshare.com').first()
        
        if not admin:
            admin = User(
                username='admin',
                email='admin@rideshare.com',
                is_admin=True,
                green_flags=0,
                red_flags=0,
                total_rides=0,
                rating=0.0
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user: admin@rideshare.com")
        else:
            # Ensure user has admin privileges
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print("✅ Updated user to admin: admin@rideshare.com")
            else:
                print("ℹ️  Admin user already exists: admin@rideshare.com")

def seed_database():
    """Main seeding function."""
    print("Starting database seeding...")
    print("-" * 50)
    
    seed_admin_user()
    
    print("-" * 50)
    print("✅ Database seeding complete!")
    print("\n🔐 Admin Login:")
    print("   URL: http://localhost:5000/login")
    print("   Email: admin@rideshare.com")
    print("   Password: admin123")

if __name__ == '__main__':
    seed_database()
