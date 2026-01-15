"""
Seed script to populate the database with sample data for testing.
Run this script to add test users, cars, rides, bookings, reviews, and reports.

Usage: python seed_data.py
"""

from app import app, db, User, Car, Ride, Booking, Review, Report, Wallet, Expense
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

def clear_data():
    """Clear existing data (optional - comment out if you want to keep existing data)."""
    print("Clearing existing data...")
    Review.query.delete()
    Report.query.delete()
    Wallet.query.delete()
    Expense.query.delete()
    Booking.query.delete()
    Ride.query.delete()
    Car.query.delete()
    # Keep admin user if exists, delete others
    User.query.filter(User.is_admin == False).delete()
    db.session.commit()
    print("Data cleared!")

def create_users():
    """Create sample users."""
    print("Creating users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@rideshare.com',
            'password': 'Prajithm1',
            'phone': '9999999999',
            'is_admin': True,
            'green_flags': 0,
            'red_flags': 0
        },
        {
            'username': 'rahul_driver',
            'email': 'rahul@example.com',
            'password': 'Prajithm1',
            'phone': '9876543210',
            'is_admin': False,
            'total_rides': 25,
            'rating': 4.5,
            'green_flags': 18,
            'red_flags': 2
        },
        {
            'username': 'priya_sharma',
            'email': 'priya@example.com',
            'password': 'Prajithm1',
            'phone': '9876543211',
            'is_admin': False,
            'total_rides': 15,
            'rating': 4.8,
            'green_flags': 12,
            'red_flags': 0
        },
        {
            'username': 'amit_kumar',
            'email': 'amit@example.com',
            'password': 'Prajithm1',
            'phone': '9876543212',
            'is_admin': False,
            'total_rides': 8,
            'rating': 4.2,
            'green_flags': 5,
            'red_flags': 1
        },
        {
            'username': 'sneha_patel',
            'email': 'sneha@example.com',
            'password': 'Prajithm1',
            'phone': '9876543213',
            'is_admin': False,
            'total_rides': 12,
            'rating': 4.6,
            'green_flags': 10,
            'red_flags': 0
        },
        {
            'username': 'vikram_singh',
            'email': 'vikram@example.com',
            'password': 'Prajithm1',
            'phone': '9876543214',
            'is_admin': False,
            'total_rides': 30,
            'rating': 4.9,
            'green_flags': 25,
            'red_flags': 1
        },
        {
            'username': 'anita_desai',
            'email': 'anita@example.com',
            'password': 'Prajithm1',
            'phone': '9876543215',
            'is_admin': False,
            'total_rides': 5,
            'rating': 3.8,
            'green_flags': 3,
            'red_flags': 2
        },
        {
            'username': 'rajesh_verma',
            'email': 'rajesh@example.com',
            'password': 'Prajithm1',
            'phone': '9876543216',
            'is_admin': False,
            'total_rides': 20,
            'rating': 4.4,
            'green_flags': 15,
            'red_flags': 1
        }
    ]
    
    users = []
    for user_data in users_data:
        # Check if user exists by username OR email
        existing = User.query.filter(
            (User.email == user_data['email']) | (User.username == user_data['username'])
        ).first()
        
        if existing:
            print(f"   User '{user_data['username']}' already exists, skipping...")
            users.append(existing)
            continue
            
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            phone=user_data['phone'],
            is_admin=user_data.get('is_admin', False),
            total_rides=user_data.get('total_rides', 0),
            rating=user_data.get('rating', 0.0),
            green_flags=user_data.get('green_flags', 0),
            red_flags=user_data.get('red_flags', 0)
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID
        users.append(user)
    
    db.session.commit()
    print(f"Created/Found {len(users)} users!")
    return users

def create_cars(users):
    """Create sample cars for drivers."""
    print("Creating cars...")
    
    # Skip admin (index 0), create cars for other users
    cars_data = [
        # Rahul's cars
        {'owner_idx': 1, 'make': 'Maruti', 'model': 'Swift', 'year': 2022, 'color': 'White', 'license_plate': 'MH01AB1234', 'fuel_type': 'petrol', 'mileage': 18.0, 'ac': True},
        {'owner_idx': 1, 'make': 'Hyundai', 'model': 'Creta', 'year': 2023, 'color': 'Black', 'license_plate': 'MH01CD5678', 'fuel_type': 'diesel', 'mileage': 16.0, 'ac': True},
        # Priya's car
        {'owner_idx': 2, 'make': 'Honda', 'model': 'City', 'year': 2021, 'color': 'Silver', 'license_plate': 'MH02EF9012', 'fuel_type': 'petrol', 'mileage': 17.0, 'ac': True},
        # Amit's car
        {'owner_idx': 3, 'make': 'Tata', 'model': 'Nexon EV', 'year': 2024, 'color': 'Blue', 'license_plate': 'MH03GH3456', 'fuel_type': 'electric', 'mileage': 300.0, 'ac': True},
        # Sneha's car
        {'owner_idx': 4, 'make': 'Kia', 'model': 'Seltos', 'year': 2023, 'color': 'Red', 'license_plate': 'MH04IJ7890', 'fuel_type': 'diesel', 'mileage': 15.0, 'ac': True},
        # Vikram's cars
        {'owner_idx': 5, 'make': 'Toyota', 'model': 'Innova', 'year': 2022, 'color': 'Grey', 'license_plate': 'MH05KL1234', 'fuel_type': 'diesel', 'mileage': 12.0, 'ac': True},
        {'owner_idx': 5, 'make': 'Mahindra', 'model': 'XUV700', 'year': 2024, 'color': 'White', 'license_plate': 'MH05MN5678', 'fuel_type': 'diesel', 'mileage': 14.0, 'ac': True},
        # Rajesh's car
        {'owner_idx': 7, 'make': 'Maruti', 'model': 'Baleno', 'year': 2023, 'color': 'Blue', 'license_plate': 'MH07OP9012', 'fuel_type': 'petrol', 'mileage': 19.0, 'ac': True},
    ]
    
    cars = []
    for car_data in cars_data:
        # Check if car exists
        existing = Car.query.filter_by(license_plate=car_data['license_plate']).first()
        if existing:
            cars.append(existing)
            continue
            
        car = Car(
            owner_id=users[car_data['owner_idx']].id,
            make=car_data['make'],
            model=car_data['model'],
            year=car_data['year'],
            color=car_data['color'],
            license_plate=car_data['license_plate'],
            fuel_type=car_data['fuel_type'],
            mileage=car_data['mileage'],
            ac=car_data['ac']
        )
        db.session.add(car)
        cars.append(car)
    
    db.session.commit()
    print(f"Created {len(cars)} cars!")
    return cars

def create_rides(users, cars):
    """Create sample rides."""
    print("Creating rides...")
    
    now = datetime.utcnow()
    
    rides_data = [
        # Upcoming rides (future)
        {
            'driver_idx': 1, 'car_idx': 0,  # Rahul with Swift
            'origin': 'Andheri East, Mumbai', 'destination': 'Bandra Kurla Complex, Mumbai',
            'start_offset': timedelta(days=1, hours=8),
            'duration': timedelta(hours=1),
            'seats': 3, 'price': 150.0, 'distance': 12.0,
            'status': 'UPCOMING', 'package_type': 'daily'
        },
        {
            'driver_idx': 2, 'car_idx': 2,  # Priya with City
            'origin': 'Thane Station, Thane', 'destination': 'Nariman Point, Mumbai',
            'start_offset': timedelta(days=1, hours=9),
            'duration': timedelta(hours=1, minutes=30),
            'seats': 2, 'price': 250.0, 'distance': 28.0,
            'status': 'UPCOMING', 'package_type': 'weekly'
        },
        {
            'driver_idx': 5, 'car_idx': 5,  # Vikram with Innova
            'origin': 'Borivali West, Mumbai', 'destination': 'Lower Parel, Mumbai',
            'start_offset': timedelta(days=2, hours=7, minutes=30),
            'duration': timedelta(hours=1, minutes=45),
            'seats': 5, 'price': 200.0, 'distance': 22.0,
            'status': 'UPCOMING', 'package_type': 'monthly'
        },
        {
            'driver_idx': 3, 'car_idx': 3,  # Amit with Nexon EV
            'origin': 'Powai, Mumbai', 'destination': 'Worli, Mumbai',
            'start_offset': timedelta(days=3, hours=8, minutes=30),
            'duration': timedelta(hours=1),
            'seats': 3, 'price': 180.0, 'distance': 15.0,
            'status': 'UPCOMING', 'package_type': 'weekly'
        },
        
        # Ongoing ride (started today)
        {
            'driver_idx': 4, 'car_idx': 4,  # Sneha with Seltos
            'origin': 'Malad West, Mumbai', 'destination': 'Churchgate, Mumbai',
            'start_offset': timedelta(hours=-1),  # Started 1 hour ago
            'duration': timedelta(hours=2),
            'seats': 3, 'price': 220.0, 'distance': 25.0,
            'status': 'ONGOING', 'package_type': 'daily'
        },
        
        # Completed rides (past)
        {
            'driver_idx': 1, 'car_idx': 1,  # Rahul with Creta
            'origin': 'Goregaon East, Mumbai', 'destination': 'Fort, Mumbai',
            'start_offset': timedelta(days=-3, hours=8),
            'duration': timedelta(hours=1, minutes=30),
            'seats': 4, 'price': 280.0, 'distance': 30.0,
            'status': 'COMPLETED', 'package_type': 'weekly'
        },
        {
            'driver_idx': 5, 'car_idx': 6,  # Vikram with XUV700
            'origin': 'Kandivali East, Mumbai', 'destination': 'Dadar, Mumbai',
            'start_offset': timedelta(days=-5, hours=9),
            'duration': timedelta(hours=1, minutes=15),
            'seats': 5, 'price': 180.0, 'distance': 18.0,
            'status': 'COMPLETED', 'package_type': 'biweekly'
        },
        {
            'driver_idx': 7, 'car_idx': 7,  # Rajesh with Baleno
            'origin': 'Vashi, Navi Mumbai', 'destination': 'Andheri West, Mumbai',
            'start_offset': timedelta(days=-7, hours=7, minutes=30),
            'duration': timedelta(hours=1, minutes=45),
            'seats': 3, 'price': 300.0, 'distance': 35.0,
            'status': 'COMPLETED', 'package_type': 'monthly'
        },
        {
            'driver_idx': 2, 'car_idx': 2,  # Priya with City - completed
            'origin': 'Mulund West, Mumbai', 'destination': 'Colaba, Mumbai',
            'start_offset': timedelta(days=-10, hours=8),
            'duration': timedelta(hours=2),
            'seats': 2, 'price': 350.0, 'distance': 38.0,
            'status': 'COMPLETED', 'package_type': 'weekly'
        },
        
        # Cancelled ride
        {
            'driver_idx': 3, 'car_idx': 3,  # Amit cancelled
            'origin': 'Chembur, Mumbai', 'destination': 'Santacruz, Mumbai',
            'start_offset': timedelta(days=-2, hours=9),
            'duration': timedelta(hours=1),
            'seats': 3, 'price': 120.0, 'distance': 10.0,
            'status': 'CANCELLED', 'package_type': 'daily'
        },
    ]
    
    rides = []
    for ride_data in rides_data:
        start_time = now + ride_data['start_offset']
        end_time = start_time + ride_data['duration']
        
        ride = Ride(
            driver_id=users[ride_data['driver_idx']].id,
            car_id=cars[ride_data['car_idx']].id,
            start_location=ride_data['origin'],
            end_location=ride_data['destination'],
            start_date=start_time,
            end_date=end_time,
            estimated_end_time=end_time,
            available_seats=ride_data['seats'],
            price_per_seat=ride_data['price'],
            distance=ride_data['distance'],
            status=ride_data['status'],
            package_type=ride_data['package_type']
        )
        
        # Set actual times for completed/ongoing rides
        if ride_data['status'] == 'COMPLETED':
            ride.actual_start_time = start_time
            ride.actual_end_time = end_time
            ride.completed_by = 'DRIVER'
        elif ride_data['status'] == 'ONGOING':
            ride.actual_start_time = start_time
        
        db.session.add(ride)
        rides.append(ride)
    
    db.session.commit()
    print(f"Created {len(rides)} rides!")
    return rides

def create_bookings(users, rides):
    """Create sample bookings."""
    print("Creating bookings...")
    
    bookings_data = [
        # Bookings for upcoming ride 0 (Rahul's ride)
        {'ride_idx': 0, 'passenger_idx': 3, 'seats': 1, 'status': 'CONFIRMED', 'pickup': 'Andheri Metro Station', 'drop': 'BKC Gate 5'},
        {'ride_idx': 0, 'passenger_idx': 4, 'seats': 2, 'status': 'PENDING', 'pickup': 'Chakala Junction', 'drop': 'BKC Connector'},
        
        # Bookings for upcoming ride 1 (Priya's ride)
        {'ride_idx': 1, 'passenger_idx': 6, 'seats': 1, 'status': 'CONFIRMED', 'pickup': 'Thane Station East', 'drop': 'Nariman Point Bus Stop'},
        
        # Bookings for upcoming ride 2 (Vikram's Innova)
        {'ride_idx': 2, 'passenger_idx': 3, 'seats': 2, 'status': 'CONFIRMED', 'pickup': 'Borivali Station', 'drop': 'Lower Parel Station'},
        {'ride_idx': 2, 'passenger_idx': 6, 'seats': 1, 'status': 'CONFIRMED', 'pickup': 'IC Colony, Borivali', 'drop': 'Phoenix Mills'},
        {'ride_idx': 2, 'passenger_idx': 7, 'seats': 1, 'status': 'PENDING', 'pickup': 'Borivali West Subway', 'drop': 'Palladium Mall'},
        
        # Bookings for ongoing ride 4 (Sneha's ride)
        {'ride_idx': 4, 'passenger_idx': 1, 'seats': 1, 'status': 'CONFIRMED', 'pickup': 'Malad Station West', 'drop': 'Churchgate Station', 'passenger_status': 'ONGOING'},
        {'ride_idx': 4, 'passenger_idx': 7, 'seats': 1, 'status': 'CONFIRMED', 'pickup': 'Evershine Nagar', 'drop': 'Eros Cinema', 'passenger_status': 'ONGOING'},
        
        # Bookings for completed ride 5 (Rahul's Creta)
        {'ride_idx': 5, 'passenger_idx': 2, 'seats': 2, 'status': 'COMPLETED', 'pickup': 'Goregaon Station', 'drop': 'Horniman Circle', 'passenger_status': 'COMPLETED'},
        {'ride_idx': 5, 'passenger_idx': 4, 'seats': 1, 'status': 'COMPLETED', 'pickup': 'Oberoi Mall', 'drop': 'Flora Fountain', 'passenger_status': 'COMPLETED'},
        
        # Bookings for completed ride 6 (Vikram's XUV)
        {'ride_idx': 6, 'passenger_idx': 3, 'seats': 2, 'status': 'COMPLETED', 'pickup': 'Kandivali Station', 'drop': 'Dadar TT', 'passenger_status': 'COMPLETED'},
        {'ride_idx': 6, 'passenger_idx': 6, 'seats': 1, 'status': 'COMPLETED', 'pickup': 'Thakur Village', 'drop': 'Shivaji Park', 'passenger_status': 'COMPLETED'},
        
        # Bookings for completed ride 7 (Rajesh's Baleno)
        {'ride_idx': 7, 'passenger_idx': 2, 'seats': 1, 'status': 'COMPLETED', 'pickup': 'Vashi Station', 'drop': 'DN Nagar Metro', 'passenger_status': 'COMPLETED'},
        
        # Bookings for completed ride 8 (Priya's past ride)
        {'ride_idx': 8, 'passenger_idx': 5, 'seats': 1, 'status': 'COMPLETED', 'pickup': 'Mulund Check Naka', 'drop': 'Gateway of India', 'passenger_status': 'COMPLETED'},
        
        # Cancelled bookings
        {'ride_idx': 0, 'passenger_idx': 7, 'seats': 1, 'status': 'CANCELLED', 'pickup': 'Western Express Highway', 'drop': 'BKC'},
        {'ride_idx': 9, 'passenger_idx': 4, 'seats': 1, 'status': 'CANCELLED', 'pickup': 'Chembur Station', 'drop': 'Santacruz West'},  # Ride was cancelled
    ]
    
    bookings = []
    for booking_data in bookings_data:
        booking = Booking(
            ride_id=rides[booking_data['ride_idx']].id,
            passenger_id=users[booking_data['passenger_idx']].id,
            seats=booking_data['seats'],
            status=booking_data['status'],
            pickup_address=booking_data['pickup'],
            drop_address=booking_data['drop'],
            contact_number=users[booking_data['passenger_idx']].phone,
            passenger_ride_status=booking_data.get('passenger_status', 'UPCOMING')
        )
        
        if booking_data['status'] == 'COMPLETED':
            booking.passenger_completed_at = rides[booking_data['ride_idx']].actual_end_time
        
        db.session.add(booking)
        bookings.append(booking)
    
    db.session.commit()
    print(f"Created {len(bookings)} bookings!")
    return bookings

def create_reviews(users, bookings):
    """Create sample reviews for completed bookings."""
    print("Creating reviews...")
    
    # Only create reviews for completed bookings
    completed_bookings = [b for b in bookings if b.status == 'COMPLETED']
    
    reviews = []
    comments_positive = [
        "Great driver, very punctual!",
        "Smooth ride, highly recommended.",
        "Very friendly and professional.",
        "Car was clean and comfortable.",
        "Excellent experience, will book again!",
        "Safe driving, good music!",
        "On time and courteous.",
        "Best Ride-Share experience ever!",
    ]
    
    comments_negative = [
        "Driver was late by 15 minutes.",
        "Could improve cleanliness.",
        "Drove a bit fast for my comfort.",
    ]
    
    for booking in completed_bookings:
        # Passenger reviews driver
        is_positive = random.random() > 0.15  # 85% positive
        flag = 'green' if is_positive else 'red'
        rating = 5 if is_positive else 1
        comment = random.choice(comments_positive if is_positive else comments_negative)
        
        review = Review(
            reviewer_id=booking.passenger_id,
            reviewed_id=booking.ride.driver_id,
            booking_id=booking.id,
            rating=rating,
            comment=comment,
            flag_type=flag,
            review_type=Review.TYPE_PASSENGER_TO_DRIVER
        )
        db.session.add(review)
        reviews.append(review)
        
        # Driver reviews passenger (50% of the time)
        if random.random() > 0.5:
            is_positive = random.random() > 0.1  # 90% positive for passengers
            flag = 'green' if is_positive else 'red'
            rating = 5 if is_positive else 1
            
            passenger_comments = [
                "Great passenger, very polite!",
                "On time and friendly.",
                "Pleasant company during the ride.",
                "Would be happy to share ride again!",
            ]
            
            review = Review(
                reviewer_id=booking.ride.driver_id,
                reviewed_id=booking.passenger_id,
                booking_id=booking.id,
                rating=rating,
                comment=random.choice(passenger_comments),
                flag_type=flag,
                review_type=Review.TYPE_DRIVER_TO_PASSENGER
            )
            db.session.add(review)
            reviews.append(review)
    
    db.session.commit()
    print(f"Created {len(reviews)} reviews!")
    return reviews

def create_reports(users, rides):
    """Create sample reports."""
    print("Creating reports...")
    
    reports_data = [
        {
            'user_idx': 3, 'ride_idx': 5,
            'report_type': 'feedback',
            'subject': 'Excellent Service',
            'description': 'Just wanted to say the Ride-Share service has been great! Very convenient for my daily commute.',
            'status': 'resolved'
        },
        {
            'user_idx': 6, 'ride_idx': 6,
            'report_type': 'complaint',
            'subject': 'AC was not working properly',
            'description': 'The AC in the car was not cooling well during the ride. It was uncomfortable.',
            'status': 'pending'
        },
        {
            'user_idx': 4, 'ride_idx': None,
            'report_type': 'feedback',
            'subject': 'App Feature Request',
            'description': 'It would be nice to have a chat feature to communicate with the driver before the ride.',
            'status': 'pending'
        },
        {
            'user_idx': 2, 'ride_idx': 5,
            'report_type': 'emergency',
            'subject': 'Minor Road Incident',
            'description': 'There was a minor traffic incident during the ride. No injuries but wanted to report.',
            'status': 'resolved',
            'emergency_type': 'accident',
            'location': 'Western Express Highway near Goregaon'
        },
    ]
    
    reports = []
    for report_data in reports_data:
        report = Report(
            user_id=users[report_data['user_idx']].id,
            ride_id=rides[report_data['ride_idx']].id if report_data['ride_idx'] is not None else None,
            report_type=report_data['report_type'],
            subject=report_data['subject'],
            description=report_data['description'],
            status=report_data['status'],
            emergency_type=report_data.get('emergency_type'),
            location=report_data.get('location')
        )
        
        if report_data['status'] == 'resolved':
            report.resolved_at = datetime.utcnow() - timedelta(days=1)
        
        db.session.add(report)
        reports.append(report)
    
    db.session.commit()
    print(f"Created {len(reports)} reports!")
    return reports

def create_wallet_entries(rides):
    """Create sample wallet/expense entries for completed rides."""
    print("Creating wallet entries...")
    
    completed_rides = [r for r in rides if r.status == 'COMPLETED']
    
    wallets = []
    for ride in completed_rides:
        # Calculate estimated fuel cost
        fuel_cost = ride.get_estimated_total_cost()
        toll_cost = random.choice([0, 50, 100, 150]) if ride.distance > 20 else 0
        other_costs = random.choice([0, 20, 50]) if random.random() > 0.7 else 0
        
        wallet = Wallet(
            ride_id=ride.id,
            fuel_cost=fuel_cost,
            toll_cost=toll_cost,
            other_costs=other_costs,
            description='Ride expenses'
        )
        db.session.add(wallet)
        wallets.append(wallet)
    
    db.session.commit()
    print(f"Created {len(wallets)} wallet entries!")
    return wallets

def seed_database():
    """Main function to seed the database."""
    print("\n" + "="*50)
    print("🚗 RIDE-SHARE DATABASE SEEDER")
    print("="*50 + "\n")
    
    with app.app_context():
        # Uncomment the line below to clear existing data first
        # clear_data()
        
        users = create_users()
        cars = create_cars(users)
        rides = create_rides(users, cars)
        bookings = create_bookings(users, rides)
        reviews = create_reviews(users, bookings)
        reports = create_reports(users, rides)
        wallets = create_wallet_entries(rides)
        
        print("\n" + "="*50)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"   • Users: {len(users)}")
        print(f"   • Cars: {len(cars)}")
        print(f"   • Rides: {len(rides)}")
        print(f"   • Bookings: {len(bookings)}")
        print(f"   • Reviews: {len(reviews)}")
        print(f"   • Reports: {len(reports)}")
        print(f"   • Wallet Entries: {len(wallets)}")
        
        print("\n🔑 Test Accounts:")
        print("   Admin:    admin@rideshare.com / admin123")
        print("   Driver:   rahul@example.com / password123")
        print("   Passenger: priya@example.com / password123")
        print("\n   All other users have password: password123")
        print("="*50 + "\n")

if __name__ == '__main__':
    seed_database()
