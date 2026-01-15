from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Fuel prices for cost calculation
FUEL_PRICES = {
    'petrol': 96.0,
    'diesel': 87.0,
    'electric': 8.0,  # per kWh
    'hybrid': 96.0
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rides_offered = db.relationship('Ride', backref='driver', lazy=True)
    bookings = db.relationship('Booking', backref='passenger', lazy=True)

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    origin = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='ride', lazy=True)
    
    # Additional fields that might be needed
    distance = db.Column(db.Float, nullable=True)  # Distance in kilometers
    package_type = db.Column(db.String(20), nullable=True, default='weekly')
    expenses = db.relationship('Expense', backref='ride', lazy=True)

    @property
    def available_seats(self):
        booked_seats = sum(booking.seats for booking in self.bookings if booking.status != 'cancelled')
        return self.seats - booked_seats

    def get_estimated_total_cost(self):
        """Calculate estimated total cost for the ride."""
        if not self.distance:
            return 0.0
            
        # Default fuel price and mileage if not available
        fuel_price = FUEL_PRICES.get('petrol', 100.0)
        mileage = 15.0  # Default to 15 kmpl
        
        # Calculate fuel cost based on distance and mileage
        fuel_cost = (self.distance / mileage) * fuel_price
        
        # Add maintenance cost (10% of fuel cost)
        maintenance_cost = fuel_cost * 0.10
        
        # Add toll charges (estimated 50 per 100km)
        toll_charges = (self.distance / 100) * 50
        
        total_cost = fuel_cost + maintenance_cost + toll_charges
        return round(total_cost, 2)

    def calculate_fare_distribution(self):
        """Calculate fare distribution for all passengers and driver."""
        total_cost = self.get_estimated_total_cost()
        
        # Get confirmed bookings
        confirmed_bookings = [b for b in self.bookings if b.status == 'confirmed']
        total_booked_seats = sum(b.seats for b in confirmed_bookings)
        
        # Calculate per seat cost (including driver's seat)
        total_seats = total_booked_seats + 1  # +1 for driver
        per_seat_cost = total_cost / total_seats if total_seats > 0 else 0
        
        # Calculate driver's share
        driver_share = per_seat_cost
        
        # Calculate each passenger's share
        booking_shares = []
        for booking in confirmed_bookings:
            booking_share = per_seat_cost * booking.seats
            booking_shares.append({
                'passenger_id': booking.passenger_id,
                'passenger_name': booking.passenger.username,
                'seats': booking.seats,
                'share': round(booking_share, 2)
            })
        
        return {
            'total_cost': round(total_cost, 2),
            'driver_share': round(driver_share, 2),
            'per_seat_cost': round(per_seat_cost, 2),
            'bookings': booking_shares
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def can_cancel(self):
        return self.status == 'pending' or (self.status == 'confirmed' and self.ride.start_date > datetime.utcnow())

class Expense(db.Model):
    """Model for ride expenses."""
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    toll_cost = db.Column(db.Float, default=0.0)
    other_costs = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
