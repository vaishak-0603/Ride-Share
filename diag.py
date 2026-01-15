from app import app, db, Ride, Booking
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

with app.app_context():
    print("--- RIDES ---")
    rides = []
    for r in Ride.query.all():
        rides.append({
            'id': r.id,
            'origin': r.origin,
            'destination': r.destination,
            'status': r.status,
            'start_date': r.start_date
        })
    print(json.dumps(rides, indent=2, cls=DateTimeEncoder))
    
    print("\n--- BOOKINGS ---")
    bookings = []
    for b in Booking.query.all():
        bookings.append({
            'id': b.id,
            'ride_id': b.ride_id,
            'status': b.status,
            'passenger_ride_status': b.passenger_ride_status
        })
    print(json.dumps(bookings, indent=2))
