
import json
import os
from dateutil import parser
from app import app, db, User, Car, Ride, Booking, Review, Wallet, Expense

def import_data():
    logs = []
    def log(msg):
        logs.append(str(msg))
        print(msg)

    if not os.path.exists('rideshare_backup.json'):
        log("rideshare_backup.json not found!")
        return "\n".join(logs)

    with app.app_context():
        log("Importing data to configured database...")
        log(f"Target DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Ensure tables exist with correct schema
        log("Dropping existing tables (if any)...")
        try:
            db.drop_all()
            log("Tables dropped.")
        except Exception as e:
            log(f"Note: {e}")
        
        log("Creating database tables...")
        try:
            db.create_all()
            db.session.commit()
            log("Tables created successfully.")
        except Exception as e:
            log(f"Error creating tables: {e}")

        try:
            with open('rideshare_backup.json', 'r') as f:
                data = json.load(f)
        except Exception as e:
            log(f"Error loading backup file: {e}")
            return "\n".join(logs)

        # Users
        log(f"Importing {len(data['users'])} users...")
        for u_data in data['users']:
            if not User.query.get(u_data['id']):
                user = User(
                    id=u_data['id'],
                    username=u_data['username'],
                    email=u_data['email'],
                    password_hash=u_data['password_hash'],
                    phone=u_data['phone'],
                    is_admin=u_data['is_admin'],
                    created_at=parser.parse(u_data['created_at']),
                    total_rides=u_data.get('total_rides', 0),
                    rating=u_data.get('rating', 0.0),
                    green_flags=u_data.get('green_flags', 0),
                    red_flags=u_data.get('red_flags', 0)
                )
                db.session.add(user)
        db.session.commit()

        # Cars
        log(f"Importing {len(data['cars'])} cars...")
        for c_data in data['cars']:
            if not Car.query.get(c_data['id']):
                car = Car(
                    id=c_data['id'],
                    owner_id=c_data['owner_id'],
                    make=c_data['make'],
                    model=c_data['model'],
                    year=c_data['year'],
                    color=c_data['color'],
                    license_plate=c_data['license_plate'],
                    fuel_type=c_data['fuel_type'],
                    mileage=c_data['mileage'],
                    ac=c_data['ac'],
                    created_at=parser.parse(c_data['created_at'])
                )
                db.session.add(car)
        db.session.commit()

        # Rides
        log(f"Importing {len(data['rides'])} rides...")
        for r_data in data['rides']:
            if not Ride.query.get(r_data['id']):
                ride = Ride(
                    id=r_data['id'],
                    driver_id=r_data['driver_id'],
                    car_id=r_data['car_id'],
                    start_location=r_data['start_location'],
                    end_location=r_data['end_location'],
                    start_date=parser.parse(r_data['start_date']),
                    end_date=parser.parse(r_data['end_date']),
                    actual_start_time=parser.parse(r_data['actual_start_time']) if r_data.get('actual_start_time') and r_data['actual_start_time'] != 'None' else None,
                    actual_end_time=parser.parse(r_data['actual_end_time']) if r_data.get('actual_end_time') and r_data['actual_end_time'] != 'None' else None,
                    estimated_end_time=parser.parse(r_data['estimated_end_time']) if r_data.get('estimated_end_time') and r_data['estimated_end_time'] != 'None' else None,
                    error_buffer_minutes=r_data.get('error_buffer_minutes', 15),
                    available_seats=r_data['available_seats'],
                    price_per_seat=r_data['price_per_seat'],
                    status=r_data['status'],
                    distance=r_data['distance'],
                    created_at=parser.parse(r_data['created_at']),
                    auto_completed=r_data.get('auto_completed', False),
                    completed_by=r_data.get('completed_by'),
                    package_type=r_data.get('package_type'),
                    license_photo=r_data.get('license_photo'),
                    driver_photo=r_data.get('driver_photo'),
                    vehicle_photo=r_data.get('vehicle_photo')
                )
                db.session.add(ride)
        db.session.commit()

        # Bookings
        log(f"Importing {len(data['bookings'])} bookings...")
        for b_data in data['bookings']:
            if not Booking.query.get(b_data['id']):
                booking = Booking(
                    id=b_data['id'],
                    ride_id=b_data['ride_id'],
                    passenger_id=b_data['passenger_id'],
                    seats=b_data['seats'],
                    status=b_data['status'],
                    created_at=parser.parse(b_data['created_at']),
                    pickup_address=b_data['pickup_address'],
                    drop_address=b_data['drop_address'],
                    share=b_data.get('share'),
                    contact_number=b_data.get('contact_number'),
                    booking_date=parser.parse(b_data['booking_date']),
                    passenger_ride_status=b_data.get('passenger_ride_status'),
                    passenger_completed_at=parser.parse(b_data['passenger_completed_at']) if b_data.get('passenger_completed_at') and b_data['passenger_completed_at'] != 'None' else None
                )
                db.session.add(booking)
        db.session.commit()
        
        # Reviews
        log(f"Importing {len(data['reviews'])} reviews...")
        for rev_data in data['reviews']:
            if not Review.query.get(rev_data['id']):
                review = Review(
                    id=rev_data['id'],
                    reviewer_id=rev_data['reviewer_id'],
                    reviewed_id=rev_data['reviewed_id'],
                    booking_id=rev_data['booking_id'],
                    rating=rev_data['rating'],
                    comment=rev_data['comment'],
                    flag_type=rev_data.get('flag_type'),
                    review_type=rev_data.get('review_type'),
                    created_at=parser.parse(rev_data['created_at'])
                )
                db.session.add(review)
        db.session.commit()
        
        # Wallets
        log(f"Importing {len(data['wallets'])} wallets...")
        for w_data in data['wallets']:
            if not Wallet.query.get(w_data['id']):
                wallet = Wallet(
                    id=w_data['id'],
                    ride_id=w_data['ride_id'],
                    fuel_cost=w_data.get('fuel_cost', 0.0),
                    toll_cost=w_data.get('toll_cost', 0.0),
                    other_costs=w_data.get('other_costs', 0.0),
                    description=w_data.get('description'),
                    date_added=parser.parse(w_data['date_added'])
                )
                db.session.add(wallet)
        db.session.commit()
        
        # Expenses
        log(f"Importing {len(data['expenses'])} expenses...")
        for e_data in data['expenses']:
            if not Expense.query.get(e_data['id']):
                expense = Expense(
                    id=e_data['id'],
                    ride_id=e_data['ride_id'],
                    toll_cost=e_data.get('toll_cost', 0.0),
                    other_costs=e_data.get('other_costs', 0.0),
                    description=e_data.get('description'),
                    created_at=parser.parse(e_data['created_at'])
                )
                db.session.add(expense)
        db.session.commit()

        log("Data imported successfully!")

if __name__ == "__main__":
    import_data()
