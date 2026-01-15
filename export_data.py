
import json
import os
from app import app, db, User, Car, Ride, Booking, Review, Wallet, Expense
from datetime import datetime

def datetime_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)

def export_data():
    with app.app_context():
        print("Exporting data from SQLite...")
        
        data = {
            'users': [],
            'cars': [],
            'rides': [],
            'bookings': [],
            'reviews': [],
            'wallets': [],
            'expenses': []
        }

        # Users
        for user in User.query.all():
            data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'phone': user.phone,
                'is_admin': user.is_admin,
                'created_at': user.created_at,
                'total_rides': user.total_rides,
                'rating': user.rating,
                'green_flags': user.green_flags,
                'red_flags': user.red_flags
            })

        # Cars
        for car in Car.query.all():
            data['cars'].append({
                'id': car.id,
                'owner_id': car.owner_id,
                'make': car.make,
                'model': car.model,
                'year': car.year,
                'color': car.color,
                'license_plate': car.license_plate,
                'fuel_type': car.fuel_type,
                'mileage': car.mileage,
                'ac': car.ac,
                'created_at': car.created_at
            })

        # Rides
        for ride in Ride.query.all():
            data['rides'].append({
                'id': ride.id,
                'driver_id': ride.driver_id,
                'car_id': ride.car_id,
                'start_location': ride.start_location,
                'end_location': ride.end_location,
                'start_date': ride.start_date,
                'end_date': ride.end_date,
                'actual_start_time': ride.actual_start_time,
                'actual_end_time': ride.actual_end_time,
                'estimated_end_time': ride.estimated_end_time,
                'error_buffer_minutes': ride.error_buffer_minutes,
                'available_seats': ride.available_seats,
                'price_per_seat': ride.price_per_seat,
                'status': ride.status,
                'distance': ride.distance,
                'created_at': ride.created_at,
                'auto_completed': ride.auto_completed,
                'completed_by': ride.completed_by,
                'package_type': ride.package_type,
                'license_photo': ride.license_photo,
                'driver_photo': ride.driver_photo,
                'vehicle_photo': ride.vehicle_photo
            })

        # Bookings
        for booking in Booking.query.all():
            data['bookings'].append({
                'id': booking.id,
                'ride_id': booking.ride_id,
                'passenger_id': booking.passenger_id,
                'seats': booking.seats,
                'status': booking.status,
                'created_at': booking.created_at,
                'pickup_address': booking.pickup_address,
                'drop_address': booking.drop_address,
                'share': booking.share, # using 'share' column
                'contact_number': booking.contact_number,
                'booking_date': booking.booking_date,
                'passenger_ride_status': booking.passenger_ride_status,
                'passenger_completed_at': booking.passenger_completed_at
            })

        # Reviews
        for review in Review.query.all():
            data['reviews'].append({
                'id': review.id,
                'reviewer_id': review.reviewer_id,
                'reviewed_id': review.reviewed_id,
                'booking_id': review.booking_id,
                'rating': review.rating,
                'comment': review.comment,
                'flag_type': review.flag_type,
                'review_type': review.review_type,
                'created_at': review.created_at
            })
            
        # Wallets
        for wallet in Wallet.query.all():
            data['wallets'].append({
                'id': wallet.id,
                'ride_id': wallet.ride_id,
                'fuel_cost': wallet.fuel_cost,
                'toll_cost': wallet.toll_cost,
                'other_costs': wallet.other_costs,
                'description': wallet.description,
                'date_added': wallet.date_added
            })
            
        # Expenses
        try:
            for expense in Expense.query.all():
                 data['expenses'].append({
                    'id': expense.id,
                    'ride_id': expense.ride_id,
                    'toll_cost': expense.toll_cost,
                    'other_costs': expense.other_costs,
                    'description': expense.description,
                    'created_at': expense.created_at
                })
        except Exception as e:
            print(f"Skipping expenses (table might be missing): {e}")

        with open('rideshare_backup.json', 'w') as f:
            json.dump(data, f, default=datetime_serializer, indent=4)
            
        print("Data exported successfully to rideshare_backup.json")

if __name__ == "__main__":
    export_data()
