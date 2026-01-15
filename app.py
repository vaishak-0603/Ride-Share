"""
Ride-Share Web Application - Main Application File

This is the main Flask application file that handles:
1. User authentication (register, login, logout)
2. Ride management (offer, search, book, cancel)
3. Database models and relationships
4. Form handling and validation
5. Route definitions and business logic

The application uses:
- Flask: Web framework
- SQLAlchemy: Database ORM
- Flask-Login: User session management
- Flask-WTF: Form handling and CSRF protection
- Bootstrap 5: Frontend styling

Author: Antigravity
Date: January 2026
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
import bcrypt
import os
from sqlalchemy import inspect, text
from datetime import datetime, timedelta, timezone
import bcrypt
import os
from sqlalchemy import inspect, text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def utc_now():
    """Return current UTC time as a naive datetime (for SQLite compatibility).
    This avoids the deprecation warning while maintaining compatibility with existing data."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Initialize Flask application and configure it
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rideshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Context processor to inject common variables into all templates
@app.context_processor
def inject_now():
    """Make 'now' available in all templates for footer copyright year etc."""
    return {'now': datetime.now()}

# Constants
FUEL_PRICES = {
    'petrol': 102.0,  # ₹102 per liter
    'diesel': 88.0,   # ₹88 per liter
    'electric': 10.0  # ₹10 per kWh
}

# Car Database with mileage and fuel type
CAR_DATABASE = {
    'Maruti': {
        'Swift': {'mileage': 23.2, 'fuel_type': 'petrol'},
        'Baleno': {'mileage': 22.35, 'fuel_type': 'petrol'},
        'Dzire': {'mileage': 24.12, 'fuel_type': 'petrol'},
        'Ertiga': {'mileage': 20.51, 'fuel_type': 'petrol'},
        'Brezza': {'mileage': 20.15, 'fuel_type': 'petrol'}
    },
    'Hyundai': {
        'i20': {'mileage': 20.28, 'fuel_type': 'petrol'},
        'Venue': {'mileage': 18.15, 'fuel_type': 'petrol'},
        'Creta': {'mileage': 17.0, 'fuel_type': 'petrol'},
        'Verna': {'mileage': 19.2, 'fuel_type': 'petrol'}
    },
    'Honda': {
        'City': {'mileage': 18.4, 'fuel_type': 'petrol'},
        'Amaze': {'mileage': 18.6, 'fuel_type': 'petrol'},
        'WRV': {'mileage': 16.5, 'fuel_type': 'petrol'},
        'Jazz': {'mileage': 17.1, 'fuel_type': 'petrol'}
    },
    'Toyota': {
        'Innova': {'mileage': 15.6, 'fuel_type': 'diesel'},
        'Fortuner': {'mileage': 14.4, 'fuel_type': 'diesel'},
        'Glanza': {'mileage': 22.35, 'fuel_type': 'petrol'},
        'Camry': {'mileage': 19.16, 'fuel_type': 'petrol'}
    },
    'Tata': {
        'Nexon': {'mileage': 17.4, 'fuel_type': 'petrol'},
        'Harrier': {'mileage': 16.35, 'fuel_type': 'diesel'},
        'Safari': {'mileage': 16.14, 'fuel_type': 'diesel'},
        'Altroz': {'mileage': 19.05, 'fuel_type': 'petrol'}
    }
}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Add package durations
PACKAGE_DURATIONS = {
    'daily': 1,
    'weekly': 7,
    'biweekly': 14,
    'monthly': 30
}

# Average speed for time estimation (km/h)
AVERAGE_SPEED = 40  # Considering city traffic and stops

# Time restrictions for different package types (in hours, 24-hour format)
TIME_RESTRICTIONS = {
    'daily': {
        'start_min': 4,  # 4 AM
        'start_max': 19,  # 7 PM
        'end_deadline': 20  # 8 PM - all rides must complete by this time
    },
    'weekly': {
        'start_min': 3,  # 3 AM
        'start_max': 21,  # 9 PM
        'end_deadline': 22  # 10 PM
    },
    'biweekly': {
        'start_min': 3,  # 3 AM
        'start_max': 21,  # 9 PM
        'end_deadline': 22  # 10 PM
    },
    'monthly': {
        'start_min': 3,  # 3 AM
        'start_max': 21,  # 9 PM
        'end_deadline': 22  # 10 PM
    }
}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file, prefix=''):
    """Save uploaded file with a unique name and return the file path."""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{prefix}_{uuid.uuid4().hex}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Return relative path for database storage
        return f"uploads/{unique_filename}"
    return None

def validate_ride_time(start_datetime, distance, package_type):
    """
    Validate if the ride can be offered based on time restrictions.
    
    Args:
        start_datetime: datetime object for ride start time
        distance: float - distance in km
        package_type: str - 'daily', 'weekly', 'biweekly', 'monthly'
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if package_type not in TIME_RESTRICTIONS:
        return False, f"Invalid package type: {package_type}"
    
    restrictions = TIME_RESTRICTIONS[package_type]
    start_hour = start_datetime.hour
    
    # Check if start time is within allowed range
    if start_hour < restrictions['start_min'] or start_hour >= restrictions['start_max']:
        if package_type == 'daily':
            return False, f"Daily rides can only start between 4:00 AM and 7:00 PM"
        else:
            return False, f"{package_type.capitalize()} rides can only start between 3:00 AM and 9:00 PM"
    
    # For daily rides, check if ride can complete within the time window
    if package_type == 'daily':
        # Calculate time available until deadline (8 PM)
        start_time_in_hours = start_hour + (start_datetime.minute / 60.0)
        deadline_hour = restrictions['end_deadline']
        available_hours = deadline_hour - start_time_in_hours
        
        # If negative or zero, ride can't be completed
        if available_hours <= 0:
            return False, f"Daily rides starting at {start_datetime.strftime('%I:%M %p')} cannot be completed before 8:00 PM deadline."
        
        # Calculate maximum distance that can be covered in available time
        max_distance = available_hours * AVERAGE_SPEED
        
        # Check if requested distance exceeds maximum
        if distance > max_distance:
            estimated_hours = distance / AVERAGE_SPEED
            return False, f"Daily rides starting at {start_datetime.strftime('%I:%M %p')} must complete by 8:00 PM. Maximum distance: {max_distance:.1f} km. Your ride: {distance:.1f} km (would take {estimated_hours:.1f} hours)."
    
    return True, None

class User(UserMixin, db.Model):
    """Model for user accounts."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    
    # Stats and ratings
    total_rides = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    green_flags = db.Column(db.Integer, default=0)
    red_flags = db.Column(db.Integer, default=0)
    
    # Relationships
    cars = db.relationship('Car', backref='owner', lazy=True)
    rides_offered = db.relationship('Ride', backref='driver', lazy=True, foreign_keys='Ride.driver_id')
    bookings = db.relationship('Booking', backref='passenger', lazy=True, foreign_keys='Booking.passenger_id')
    reviews_given = db.relationship('Review', backref='reviewer', lazy=True, foreign_keys='Review.reviewer_id')
    reviews_received = db.relationship('Review', backref='reviewed', lazy=True, foreign_keys='Review.reviewed_id')
    reports = db.relationship('Report', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
        
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
        
    @property
    def current_ride(self):
        """Get the user's current active ride (as driver or passenger)."""
        current_time = utc_now()
        
        # Check if user is driving any current rides
        driver_ride = next((ride for ride in self.rides_offered 
                          if ride.start_date <= current_time 
                          and ride.end_date >= current_time), None)
        if driver_ride:
            return driver_ride
            
        # Check if user is a passenger in any current rides
        passenger_booking = next((booking for booking in self.bookings 
                                if booking.status == Booking.STATUS_CONFIRMED
                                and booking.ride.start_date <= current_time 
                                and booking.ride.end_date >= current_time), None)
        if passenger_booking:
            return passenger_booking.ride
            
        return None

class Review(db.Model):
    """Model for user reviews."""
    # Review type constants
    TYPE_PASSENGER_TO_DRIVER = 'passenger_to_driver'
    TYPE_DRIVER_TO_PASSENGER = 'driver_to_passenger'
    
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    flag_type = db.Column(db.String(10), nullable=True)  # 'green' or 'red'
    review_type = db.Column(db.String(30), nullable=True)  # 'passenger_to_driver' or 'driver_to_passenger'
    created_at = db.Column(db.DateTime, default=utc_now)
    
    def __repr__(self):
        return f'<Review {self.reviewer_id} -> {self.reviewed_id}>'
    
    @property
    def is_driver_review(self):
        """Check if this is a review of a driver (by a passenger)."""
        return self.review_type == self.TYPE_PASSENGER_TO_DRIVER
    
    @property
    def is_passenger_review(self):
        """Check if this is a review of a passenger (by a driver)."""
        return self.review_type == self.TYPE_DRIVER_TO_PASSENGER

class Car(db.Model):
    """Model for user's cars."""
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)  # petrol, diesel, electric
    mileage = db.Column(db.Float, nullable=False)  # km per liter
    ac = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    
    def __repr__(self):
        return f'<Car {self.make} {self.model} ({self.license_plate})>'

class Wallet(db.Model):
    """Wallet model for storing ride expenses."""
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    fuel_cost = db.Column(db.Float, nullable=False, default=0.0)
    toll_cost = db.Column(db.Float, nullable=False, default=0.0)
    other_costs = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, nullable=False, default=utc_now)

class Ride(db.Model):
    """Model for rides."""
    # Status Constants
    STATUS_UPCOMING = 'UPCOMING'
    STATUS_ONGOING = 'ONGOING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    start_location = db.Column(db.String(200), nullable=False)
    end_location = db.Column(db.String(200), nullable=False)
    
    # Scheduled times
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Actual times
    actual_start_time = db.Column(db.DateTime, nullable=True)
    actual_end_time = db.Column(db.DateTime, nullable=True)
    
    # Estimated times
    estimated_end_time = db.Column(db.DateTime, nullable=True)
    error_buffer_minutes = db.Column(db.Integer, default=15)  # Buffer time in minutes
    
    available_seats = db.Column(db.Integer, nullable=False)
    price_per_seat = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='UPCOMING')  # UPCOMING, ONGOING, COMPLETED, CANCELLED
    distance = db.Column(db.Float, nullable=False)  # Distance in kilometers
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    
    # Completion tracking
    auto_completed = db.Column(db.Boolean, default=False)  # Track if auto-completed by time
    completed_by = db.Column(db.String(20), nullable=True)  # 'DRIVER', 'SYSTEM', 'AUTO'
    
    # Add package_type with nullable=True to handle existing records
    package_type = db.Column(db.String(20), nullable=True, default='weekly')  # weekly, biweekly, monthly
    
    # Safety images
    license_photo = db.Column(db.String(300), nullable=True)  # Driver's license photo
    driver_photo = db.Column(db.String(300), nullable=True)  # Driver's photo
    vehicle_photo = db.Column(db.String(300), nullable=True)  # Vehicle photo
    
    # Relationships
    bookings = db.relationship('Booking', backref='ride', lazy=True)
    car = db.relationship('Car', backref='rides', lazy=True)
    wallet = db.relationship('Wallet', backref='ride', lazy=True)
    reports = db.relationship('Report', backref='ride', lazy=True)
    expenses = db.relationship('Expense', backref='ride', lazy=True)
    
    def __repr__(self):
        return f'<Ride {self.id} {self.start_location} to {self.end_location}>'
    
    @property
    def origin(self):
        """Alias for start_location for template compatibility."""
        return self.start_location
    
    @property
    def destination(self):
        """Alias for end_location for template compatibility."""
        return self.end_location
    
    @property
    def seats(self):
        """Alias for available_seats for template compatibility."""
        return self.available_seats
    
    def get_total_wallet_expenses(self):
        """Calculate total expenses for this ride."""
        total = 0
        for wallet_entry in self.wallet:
            total += wallet_entry.fuel_cost + wallet_entry.toll_cost + wallet_entry.other_costs
        return total
        
    def get_estimated_total_cost(self):
        """Calculate estimated total cost for the ride (fuel only)."""
        # Get car and fuel details
        fuel_price = FUEL_PRICES.get(self.car.fuel_type.lower(), 100.0)  # Default to 100 if fuel type not found
        mileage = self.car.mileage or 15.0  # Default to 15 kmpl if mileage not set
        
        # Calculate fuel cost based on distance and mileage
        fuel_cost = (self.distance / mileage) * fuel_price
        
        return round(fuel_cost, 2)
        
    def get_average_cost_per_seat(self):
        """Calculate average cost per seat based on package type cost sharing."""
        total_cost = self.get_estimated_total_cost()
        
        if self.package_type == 'daily':
            # Daily: Driver pays 50%, passengers share 50%
            passenger_share = total_cost * 0.50
        else:
            # Weekly/Bi-weekly/Monthly: Driver pays 25%, passengers share 75%
            passenger_share = total_cost * 0.75
        
        # Price per seat = passenger share divided by available seats
        per_seat_cost = passenger_share / self.available_seats if self.available_seats > 0 else 0
        return round(per_seat_cost, 2)
        
    def calculate_fare_for_booking(self, booking):
        """Calculate fare for a specific booking."""
        # Only allow cancellation of pending/confirmed bookings
        if booking.status not in [Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]:
            return 0
            
        per_seat_cost = self.get_average_cost_per_seat()
        return round(per_seat_cost * booking.seats, 2)
        
    def get_estimated_time(self):
        """Calculate estimated time to reach destination in minutes."""
        if not self.distance:
            return 0
        # Calculate time in hours, then convert to minutes
        time_hours = self.distance / AVERAGE_SPEED
        return round(time_hours * 60)
    
    def get_estimated_end_time(self):
        """Calculate estimated end time of the ride."""
        if self.estimated_end_time:
            return self.estimated_end_time
        estimated_minutes = self.get_estimated_time()
        # Use actual_start_time if ride has started, otherwise use scheduled start_date
        start_time = self.actual_start_time if self.actual_start_time else self.start_date
        return start_time + timedelta(minutes=estimated_minutes)
    
    def get_max_completion_time(self):
        """Calculate maximum time for ride completion (estimated_end_time + error_buffer)."""
        estimated_end = self.get_estimated_end_time()
        buffer = self.error_buffer_minutes or 15
        return estimated_end + timedelta(minutes=buffer)
    
    def should_auto_complete(self):
        """Check if ride should be auto-completed based on time."""
        if self.status != self.STATUS_ONGOING:
            return False
        current_time = utc_now()
        max_time = self.get_max_completion_time()
        return current_time >= max_time
    
    def is_severely_overdue(self):
        """Check if UPCOMING ride is more than 1 hour overdue."""
        if self.status != self.STATUS_UPCOMING:
            return False
        current_time = utc_now()
        hours_overdue = (current_time - self.start_date).total_seconds() / 3600
        return hours_overdue > 1
    
    def can_start(self):
        """Check if ride can be started."""
        return self.status == self.STATUS_UPCOMING
    
    def can_end(self):
        """Check if ride can be ended."""
        return self.status == self.STATUS_ONGOING
    
    def start_ride(self):
        """Start the ride - change status to ONGOING."""
        if not self.can_start():
            return False, "Ride cannot be started"
        
        self.status = self.STATUS_ONGOING
        self.actual_start_time = utc_now()
        
        # Calculate estimated end time if not set
        if not self.estimated_end_time:
            self.estimated_end_time = self.get_estimated_end_time()
        
        # Set dynamic buffer based on distance
        if self.distance <= 50:
            self.error_buffer_minutes = 30
        elif self.distance <= 100:
            self.error_buffer_minutes = 45
        elif self.distance <= 200:
            self.error_buffer_minutes = 60
        else:
            self.error_buffer_minutes = 90
        
        # Update all confirmed bookings to ONGOING
        for booking in self.bookings:
            if booking.status == booking.STATUS_CONFIRMED:
                booking.passenger_ride_status = 'ONGOING'
        
        return True, "Ride started successfully"
    
    def end_ride(self, completed_by='DRIVER'):
        """End the ride - change status to COMPLETED."""
        if not self.can_end():
            return False, "Ride cannot be ended"
        
        self.status = self.STATUS_COMPLETED
        self.actual_end_time = utc_now()
        self.completed_by = completed_by
        
        # Mark all confirmed/ongoing bookings as completed
        for booking in self.bookings:
            if booking.status in [booking.STATUS_CONFIRMED]:
                booking.status = booking.STATUS_COMPLETED
                booking.passenger_ride_status = 'COMPLETED'
                if not booking.passenger_completed_at:
                    booking.passenger_completed_at = utc_now()
        
        return True, "Ride ended successfully"
    
    def auto_complete_ride(self):
        """Auto-complete ride when time exceeds buffer."""
        self.auto_completed = True
        return self.end_ride(completed_by='AUTO')
    
    def notify_passengers(self, message_type):
        """Send notification to all confirmed passengers."""
        # In production, this would send actual notifications (email/SMS/push)
        # For now, it logs the notification
        passengers = [b.passenger for b in self.bookings if b.status in [b.STATUS_CONFIRMED, b.STATUS_PENDING]]
        notification_messages = {
            'RIDE_STARTED': f'Your ride from {self.start_location} to {self.end_location} has started!',
            'RIDE_ENDED': f'Your ride from {self.start_location} to {self.end_location} has been completed.',
            'RIDE_CANCELLED': f'The ride from {self.start_location} to {self.end_location} has been cancelled.'
        }
        app.logger.info(f'Notification {message_type}: {notification_messages.get(message_type)} sent to {len(passengers)} passengers')
        return True
    
    def calculate_fare_distribution(self):
        """Calculate fare distribution for all passengers and driver."""
        total_cost = self.get_estimated_total_cost()
        
        # Get confirmed bookings
        confirmed_bookings = [b for b in self.bookings if b.status == b.STATUS_CONFIRMED]
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
    """Model for ride bookings."""
    # Status Constants
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_REJECTED = 'REJECTED'
    
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, CONFIRMED, CANCELLED, COMPLETED, REJECTED
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    pickup_address = db.Column(db.String(200), nullable=False)
    drop_address = db.Column(db.String(200), nullable=False)
    share = db.Column(db.Float, nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    booking_date = db.Column(db.DateTime, nullable=False, default=utc_now)
    
    # Individual passenger completion tracking
    passenger_ride_status = db.Column(db.String(20), default='UPCOMING')  # UPCOMING, ONGOING, COMPLETED
    passenger_completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    reviews = db.relationship('Review', backref='booking', lazy=True)
    
    def __repr__(self):
        return f'<Booking {self.id} {self.status}>'

    def can_cancel(self):
        """Check if booking can be cancelled."""
        return self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]
    
    def complete_passenger_ride(self):
        """Mark passenger's individual ride as completed."""
        if self.status != self.STATUS_CONFIRMED:
            return False, "Only confirmed bookings can be completed"
        
        if self.ride.status != self.ride.STATUS_ONGOING:
            return False, "Ride must be ongoing to complete"
        
        # Mark passenger as completed
        self.passenger_ride_status = 'COMPLETED'
        self.passenger_completed_at = utc_now()
        
        # Note: This doesn't change booking.status to COMPLETED
        # That only happens when driver ends the entire ride
        
        return True, "Your ride marked as completed"

class Report(db.Model):
    """Model for user reports and feedback."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=True)
    report_type = db.Column(db.String(20), nullable=False)  # 'emergency', 'feedback', 'complaint'
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, resolved, dismissed
    created_at = db.Column(db.DateTime, default=utc_now)
    resolved_at = db.Column(db.DateTime)
    emergency_type = db.Column(db.String(50))  # For emergency reports: 'medical', 'accident', 'breakdown', etc.
    location = db.Column(db.String(200))  # Location when emergency/incident occurred

class Expense(db.Model):
    """Model for ride expenses."""
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    toll_cost = db.Column(db.Float, default=0.0)
    other_costs = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=utc_now)
    
class ReportForm(FlaskForm):
    """Form for submitting reports and feedback."""
    report_type = SelectField('Report Type', choices=[
        ('emergency', 'Emergency'),
        ('feedback', 'General Feedback'),
        ('complaint', 'Complaint')
    ], validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    emergency_type = SelectField('Emergency Type', choices=[
        ('', 'Select Emergency Type'),
        ('medical', 'Medical Emergency'),
        ('accident', 'Accident'),
        ('breakdown', 'Vehicle Breakdown'),
        ('safety', 'Safety Concern'),
        ('other', 'Other')
    ])
    location = StringField('Location')
    submit = SubmitField('Submit Report')

    def validate_emergency_type(self, field):
        if self.report_type.data == 'emergency' and not field.data:
            raise ValidationError('Please select the type of emergency')

# Form Classes
class RegistrationForm(FlaskForm):
    """Form for user registration with validation."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, field):
        """Validate if the username is already taken."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already taken')

    def validate_email(self, field):
        """Validate if the email is already registered."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already registered')

class LoginForm(FlaskForm):
    """Form for user login with validation."""
    email = StringField('Email', validators=[
        DataRequired(message='Please enter your email'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password')
    ])
    submit = SubmitField('Log In')

class RideForm(FlaskForm):
    """Form for offering a new ride with validation."""
    origin = StringField('Origin', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    start_date = DateTimeField('Start Date and Time', 
                        format='%Y-%m-%dT%H:%M',
                        validators=[DataRequired()],
                        render_kw={"type": "datetime-local"})
    package_type = SelectField('Package Type', validators=[DataRequired()], 
                     choices=[('weekly', 'Weekly'), ('biweekly', 'Bi-Weekly'), ('monthly', 'Monthly')])
    seats = IntegerField('Available Seats', validators=[
        DataRequired(),
        NumberRange(min=1, max=8, message='Number of seats must be between 1 and 8')
    ])
    car = SelectField('Car Model', validators=[DataRequired()], 
                     choices=[])
    distance = FloatField('Distance (km)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Distance cannot be negative')
    ])
    submit = SubmitField('Offer Ride')

    def validate_start_date(self, field):
        """Validate if the ride start date is in the future."""
        if field.data <= datetime.now():
            raise ValidationError('Ride start date must be in the future')

class BookingForm(FlaskForm):
    """Form for booking a ride with validation."""
    seats = IntegerField('Number of Seats', validators=[
        DataRequired(),
        NumberRange(min=1, max=8, message='Number of seats must be between 1 and 8')
    ])
    contact_number = StringField('Contact Number', validators=[
        DataRequired(),
        Length(min=10, max=15, message='Please enter a valid contact number')
    ])
    pickup_address = StringField('Pickup Address', validators=[
        DataRequired(),
        Length(max=200, message='Address is too long (maximum 200 characters)')
    ])
    drop_address = StringField('Drop Address', validators=[
        DataRequired(),
        Length(max=200, message='Address is too long (maximum 200 characters)')
    ])
    submit = SubmitField('Confirm Booking')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))

# Route handlers
@app.route('/')
def index():
    """Home page route."""
    return redirect(url_for('search_rides'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route with form handling."""
    if current_user.is_authenticated:
        # If already logged in and there's a next parameter, redirect there
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            # Preserve next parameter when redirecting to login
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(url_for('login', next=next_page))
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route with authentication."""
    if current_user.is_authenticated:
        # If already logged in and there's a next parameter, redirect there
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page and next_page.startswith('/') else url_for('dashboard'))
        flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing offered and booked rides."""
    current_time = utc_now()
    
    # Auto-handle overdue rides
    # 1. Auto-complete ONGOING rides that exceeded their buffer time
    ongoing_rides = Ride.query.filter(Ride.status == Ride.STATUS_ONGOING).all()
    for ride in ongoing_rides:
        if ride.should_auto_complete():
            ride.auto_complete_ride()
    
    # 2. Auto-start and complete UPCOMING rides that are severely overdue (>1 hour past start)
    # This ensures both drivers and passengers see correct status
    overdue_rides = Ride.query.filter(
        Ride.status == Ride.STATUS_UPCOMING,
        Ride.start_date < current_time - timedelta(hours=1)
    ).all()
    
    for ride in overdue_rides:
        app.logger.info(f"Auto-completing overdue ride {ride.id}")
        ride.start_ride()
        ride.auto_complete_ride()
        
        # Explicitly handle PENDING bookings that wouldn't be caught by end_ride
        for booking in ride.bookings:
            if booking.status == Booking.STATUS_PENDING:
                booking.status = Booking.STATUS_REJECTED
    
    db.session.commit()
    
    # Get active rides (UPCOMING or ONGOING rides)
    active_rides = [ride for ride in current_user.rides_offered 
                   if ride.status in [Ride.STATUS_UPCOMING, Ride.STATUS_ONGOING]]
    
    # Get past rides (COMPLETED or CANCELLED rides)
    past_rides = [ride for ride in current_user.rides_offered 
                 if ride.status in [Ride.STATUS_COMPLETED, Ride.STATUS_CANCELLED]]
    
    # Get active and past bookings
    active_bookings = [booking for booking in current_user.bookings 
                      if booking.status in [Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED] and 
                      booking.passenger_ride_status != 'COMPLETED']
    past_bookings = [booking for booking in current_user.bookings 
                    if booking.status in [Booking.STATUS_COMPLETED, Booking.STATUS_CANCELLED, Booking.STATUS_REJECTED] or
                    booking.passenger_ride_status == 'COMPLETED']
    
    # Sort rides and bookings by date
    active_rides.sort(key=lambda x: x.start_date)
    past_rides.sort(key=lambda x: x.start_date, reverse=True)
    active_bookings.sort(key=lambda x: x.ride.start_date)
    past_bookings.sort(key=lambda x: x.ride.start_date, reverse=True)
    
    # Calculate total passengers (confirmed bookings)
    total_passengers = sum(
        booking.seats for booking in current_user.bookings 
        if booking.status == 'confirmed'
    )
    
    return render_template('dashboard.html', 
                         active_rides=active_rides,
                         past_rides=past_rides,
                         active_bookings=active_bookings,
                         past_bookings=past_bookings,
                         rides_offered=current_user.rides_offered,
                         current_time=current_time,
                         total_passengers=total_passengers)

@app.route('/offer-ride', methods=['GET', 'POST'])
@login_required
def offer_ride():
    """Offer a new ride."""
    # Get user's cars and create car choices with mileage information
    user_cars = Car.query.filter_by(owner_id=current_user.id).all()
    car_choices = [(str(car.id), f"{car.make} {car.model} ({car.license_plate})", car.mileage) for car in user_cars]
    
    if request.method == 'POST':
        try:
            # Get form data
            car_type = request.form.get('carType', 'userCar')
            start_location = request.form.get('origin')
            end_location = request.form.get('destination')
            start_date_str = request.form.get('start_date')
            available_seats = request.form.get('seats')
            distance = request.form.get('distance')
            package_type = request.form.get('package_type', 'weekly')
            
            # Debug logging
            app.logger.info(f"Form data: {request.form}")
            
            # Validate inputs
            if not all([start_location, end_location, start_date_str, available_seats, distance, package_type]):
                missing = []
                if not start_location: missing.append("Origin")
                if not end_location: missing.append("Destination")
                if not start_date_str: missing.append("Start Date")
                if not available_seats: missing.append("Available Seats")
                if not distance: missing.append("Distance")
                if not package_type: missing.append("Package Type")
                
                raise ValueError(f"The following fields are required: {', '.join(missing)}")
            
            # Check for required image uploads
            license_photo = request.files.get('license_photo')
            driver_photo = request.files.get('driver_photo')
            vehicle_photo = request.files.get('vehicle_photo')
            
            if not license_photo or not license_photo.filename:
                raise ValueError("Driver's license photo is required for safety verification")
            if not driver_photo or not driver_photo.filename:
                raise ValueError("Driver's photo is required for safety verification")
            if not vehicle_photo or not vehicle_photo.filename:
                raise ValueError("Vehicle photo is required for safety verification")
            
            # Validate file types
            if not allowed_file(license_photo.filename):
                raise ValueError("License photo must be an image file (png, jpg, jpeg, gif)")
            if not allowed_file(driver_photo.filename):
                raise ValueError("Driver photo must be an image file (png, jpg, jpeg, gif)")
            if not allowed_file(vehicle_photo.filename):
                raise ValueError("Vehicle photo must be an image file (png, jpg, jpeg, gif)")
            
            # Convert types
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                available_seats = int(available_seats)
                distance = float(distance)
            except ValueError:
                raise ValueError("Invalid date, seats, or distance format")
                
            if available_seats < 1:
                raise ValueError("Must offer at least 1 seat")
                
            if distance <= 0:
                raise ValueError("Distance must be greater than 0")
                
            if package_type not in PACKAGE_DURATIONS:
                raise ValueError("Invalid package type")
            
            # Validate date range based on package type
            now = datetime.now()
            if package_type == 'daily':
                # Daily rides: Only today and tomorrow
                tomorrow_end = datetime(now.year, now.month, now.day, 23, 59, 59) + timedelta(days=1)
                if start_date < now:
                    raise ValueError("Cannot offer rides in the past")
                if start_date > tomorrow_end:
                    raise ValueError("Daily rides can only be offered for today or tomorrow")
            else:
                # Other packages: Today to 30 days from now
                max_date = datetime(now.year, now.month, now.day, 23, 59, 59) + timedelta(days=30)
                if start_date < now:
                    raise ValueError("Cannot offer rides in the past")
                if start_date > max_date:
                    raise ValueError(f"{package_type.capitalize()} rides can only be offered up to 30 days in advance")
            
            # Validate ride time based on package type
            is_valid_time, time_error = validate_ride_time(start_date, distance, package_type)
            if not is_valid_time:
                raise ValueError(time_error)
            
            # Save uploaded images
            license_photo_path = save_upload_file(license_photo, 'license')
            driver_photo_path = save_upload_file(driver_photo, 'driver')
            vehicle_photo_path = save_upload_file(vehicle_photo, 'vehicle')
            
            if not all([license_photo_path, driver_photo_path, vehicle_photo_path]):
                raise ValueError("Failed to upload one or more images. Please try again.")
            
            # Calculate end date based on package type
            package_days = PACKAGE_DURATIONS[package_type]
            end_date = start_date + timedelta(days=package_days)
            
            # Handle car selection based on car type
            if car_type == 'userCar':
                car_id = request.form.get('car')
                if not car_id:
                    raise ValueError("Please select a car from your cars")
                
                # Get car and validate ownership
                car = Car.query.get(car_id)
                if not car or car.owner_id != current_user.id:
                    raise ValueError("Invalid car selected")
            else:  # commonCar
                # Handle common car selection
                car_make = request.form.get('carMake')
                car_model = request.form.get('carModel')
                
                if not car_make or not car_model:
                    raise ValueError("Please select both car make and model")
                
                # Check if car exists in database
                if car_make not in CAR_DATABASE or car_model not in CAR_DATABASE[car_make]:
                    raise ValueError("Invalid car make or model selected")
                
                # Create a temporary car for the ride
                car_details = CAR_DATABASE[car_make][car_model]
                
                # Check if user already has this car registered
                existing_car = Car.query.filter_by(
                    owner_id=current_user.id,
                    make=car_make,
                    model=car_model
                ).first()
                
                if existing_car:
                    car = existing_car
                else:
                    # Create a new car entry
                    car = Car(
                        owner_id=current_user.id,
                        make=car_make,
                        model=car_model,
                        year=datetime.now().year,  # Default to current year
                        color="Not specified",
                        license_plate=f"TEMP-{car_make[:3]}{car_model[:3]}-{current_user.id}",
                        fuel_type=car_details['fuel_type'],
                        mileage=car_details['mileage'],
                        ac=True
                    )
                    db.session.add(car)
                    db.session.flush()  # Get the ID without committing
            
            # Create ride
            ride = Ride(
                driver_id=current_user.id,
                car_id=car.id,
                start_location=start_location,
                end_location=end_location,
                start_date=start_date,
                end_date=end_date,  # Set based on package type
                available_seats=available_seats,
                price_per_seat=0.0,  # Will be calculated based on distance and fuel cost
                status=Ride.STATUS_UPCOMING,
                distance=distance,
                package_type=package_type,  # Store the package type
                license_photo=license_photo_path,
                driver_photo=driver_photo_path,
                vehicle_photo=vehicle_photo_path
            )
            
            # Calculate total distance for the entire package period
            total_distance = distance * PACKAGE_DURATIONS[package_type]
            
            # Calculate total cost (only fuel cost)
            fuel_price = FUEL_PRICES.get(car.fuel_type.lower(), 100.0)
            fuel_cost = (total_distance / car.mileage) * fuel_price
            total_cost = fuel_cost
            
            # Calculate price per seat based on package type
            if package_type == 'daily':
                # Daily: Driver pays 50%, passengers share 50%
                # Each seat costs: (50% of total) / available_seats
                passenger_share = total_cost * 0.50
                price_per_seat = passenger_share / available_seats
            else:
                # Weekly/Bi-weekly/Monthly: Driver pays 25%, passengers share 75%
                # Each seat costs: (75% of total) / available_seats
                passenger_share = total_cost * 0.75
                price_per_seat = passenger_share / available_seats
            
            ride.price_per_seat = price_per_seat
            
            db.session.add(ride)
            db.session.commit()
            
            flash('Ride offered successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(str(e), 'error')
            app.logger.error(f"Validation error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while offering the ride. Please try again.', 'error')
            app.logger.error(f"Error offering ride: {str(e)}")
    
    return render_template('offer_ride.html', 
                         car_choices=car_choices,
                         google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'],
                         now=datetime.now(),
                         timedelta=timedelta)

@app.route('/search-rides')
def search_rides():
    """Route for searching available rides with advanced filters."""
    # Get search parameters
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    date = request.args.get('date', '')
    package_type = request.args.get('package_type', '')
    max_price = request.args.get('max_price', '')
    seats_needed = request.args.get('seats_needed', '')
    sort_by = request.args.get('sort_by', 'date')
    fuel_type = request.args.get('fuel_type', '')
    ac_preference = request.args.get('ac_preference', '')
    driver_rating = request.args.get('driver_rating', '')
    
    # Base query - only UPCOMING rides (exclude COMPLETED and CANCELLED)
    query = Ride.query.filter(
        Ride.start_date > utc_now(),
        Ride.status == Ride.STATUS_UPCOMING
    )
    
    # Apply filters
    if origin:
        query = query.filter(Ride.start_location.ilike(f'%{origin}%'))
    if destination:
        query = query.filter(Ride.end_location.ilike(f'%{destination}%'))
    if date:
        try:
            search_date = datetime.strptime(date, '%Y-%m-%d')
            query = query.filter(db.func.date(Ride.start_date) == search_date.date())
        except ValueError:
            pass
    
    # Apply additional filters
    if package_type:
        query = query.filter(Ride.package_type == package_type)
    
    if max_price:
        try:
            max_price_float = float(max_price)
            query = query.filter(Ride.price_per_seat <= max_price_float)
        except ValueError:
            pass
    
    if seats_needed:
        try:
            seats_int = int(seats_needed)
            query = query.filter(Ride.available_seats >= seats_int)
        except ValueError:
            pass
    
    if fuel_type:
        query = query.join(Car).filter(Car.fuel_type == fuel_type)
    
    if ac_preference:
        query = query.join(Car)
        if ac_preference == 'ac':
            query = query.filter(Car.ac == True)
        elif ac_preference == 'non_ac':
            query = query.filter(Car.ac == False)
    
    if driver_rating:
        try:
            min_rating = float(driver_rating)
            query = query.join(User, Ride.driver_id == User.id).filter(User.rating >= min_rating)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Ride.price_per_seat.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Ride.price_per_seat.desc())
    elif sort_by == 'distance':
        query = query.order_by(Ride.distance.asc())
    else:  # default: date
        query = query.order_by(Ride.start_date.asc())
    
    rides = query.all()
    return render_template('search_rides.html', rides=rides, now=utc_now())

@app.route('/book-ride/<int:ride_id>', methods=['GET', 'POST'])
@login_required
def book_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    
    # Check if ride is still available
    if ride.start_date < utc_now():
        flash('This ride has already started.', 'error')
        return redirect(url_for('search_rides'))
    
    # Check if ride is cancelled or completed
    if ride.status in [Ride.STATUS_CANCELLED, Ride.STATUS_COMPLETED]:
        flash('This ride is no longer available.', 'error')
        return redirect(url_for('search_rides'))
        
    # Check if user is trying to book their own ride
    if ride.driver_id == current_user.id:
        flash('You cannot book your own ride.', 'error')
        return redirect(url_for('search_rides'))
        
    # Check if user already has a booking for this ride
    existing_booking = Booking.query.filter_by(
        ride_id=ride_id,
        passenger_id=current_user.id
    ).first()
    
    if existing_booking and existing_booking.status in [Booking.STATUS_CONFIRMED, Booking.STATUS_PENDING]:
        flash('You already have a booking for this ride.', 'error')
        return redirect(url_for('search_rides'))
    
    if request.method == 'POST':
        try:
            seats = int(request.form.get('seats', 1))
            pickup_address = request.form.get('pickup_address')
            drop_address = request.form.get('drop_address')
            contact = request.form.get('contact')
            
            # Validate inputs
            if not all([pickup_address, drop_address, contact]):
                flash('Please fill in all required fields.', 'error')
                return render_template('book_ride.html', ride=ride)
            
            if seats < 1 or seats > ride.available_seats:
                flash(f'Please select between 1 and {ride.available_seats} seats.', 'error')
                return render_template('book_ride.html', ride=ride)
            
            if not contact.isdigit() or len(contact) != 10:
                flash('Please enter a valid 10-digit contact number.', 'error')
                return render_template('book_ride.html', ride=ride)
            
            # Create booking
            booking = Booking(
                ride_id=ride.id,
                passenger_id=current_user.id,
                seats=seats,
                status=Booking.STATUS_PENDING,
                pickup_address=pickup_address,
                drop_address=drop_address,
                created_at=utc_now()
            )
            
            # Reduce available seats immediately (even for pending bookings)
            ride.available_seats -= seats
            
            db.session.add(booking)
            db.session.commit()
            
            flash('Booking request sent successfully! The driver will confirm your booking.', 'success')
            return redirect(url_for('my_bookings'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while booking. Please try again.', 'error')
            app.logger.error(f"Booking error: {str(e)}")
    
    return render_template('book_ride.html', ride=ride)

@app.route('/my-bookings')
@login_required
def my_bookings():
    """Route for viewing user's bookings."""
    current_time = utc_now()
    
    # Get active and past bookings based on status
    active_bookings = Booking.query.filter_by(passenger_id=current_user.id)\
        .filter(Booking.status.in_([Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]))\
        .join(Ride)\
        .order_by(Ride.start_date).all()
        
    past_bookings = Booking.query.filter_by(passenger_id=current_user.id)\
        .filter(Booking.status.in_([Booking.STATUS_COMPLETED, Booking.STATUS_CANCELLED, Booking.STATUS_REJECTED]))\
        .join(Ride)\
        .order_by(Ride.start_date.desc()).all()
    
    return render_template('my_bookings.html', 
                         active_bookings=active_bookings,
                         past_bookings=past_bookings,
                         current_time=current_time)

@app.route('/booking/<int:booking_id>/details')
@login_required
def booking_details(booking_id):
    """View details of a specific booking including co-passengers."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is the passenger for this booking
    if booking.passenger_id != current_user.id:
        flash('You are not authorized to view this booking.', 'error')
        return redirect(url_for('my_bookings'))
    
    # Get all confirmed bookings for this ride (co-passengers)
    co_passengers = Booking.query.filter_by(ride_id=booking.ride_id)\
        .filter(Booking.status.in_([Booking.STATUS_CONFIRMED, Booking.STATUS_COMPLETED]))\
        .filter(Booking.id != booking_id)\
        .all()
    
    return render_template('booking_details.html',
                         booking=booking,
                         co_passengers=co_passengers,
                         current_time=utc_now())

@app.route('/booking/<int:booking_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    """Confirm a booking request."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the current user is the ride's driver
    if booking.ride.driver_id != current_user.id:
        flash('You are not authorized to confirm this booking.', 'error')
        return redirect(url_for('dashboard'))
        
    # Check if the booking is still pending
    if booking.status != Booking.STATUS_PENDING:
        flash('This booking cannot be confirmed.', 'error')
        return redirect(url_for('dashboard'))
        
    # Check if there are enough seats available
    if booking.seats > booking.ride.available_seats:
        flash('Not enough seats available.', 'error')
        return redirect(url_for('dashboard'))
        
    # Confirm the booking (seats already reduced when booking was created)
    booking.status = Booking.STATUS_CONFIRMED
    db.session.commit()
    
    # Send notification to passenger (you can implement this later)
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/booking/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject_booking(booking_id):
    """Reject a booking request."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the current user is the ride's driver
    if booking.ride.driver_id != current_user.id:
        flash('You are not authorized to reject this booking.', 'error')
        return redirect(url_for('dashboard'))
        
    # Check if the booking is still pending
    if booking.status != Booking.STATUS_PENDING:
        flash('This booking cannot be rejected.', 'error')
        return redirect(url_for('dashboard'))
        
    # Restore seats since this was a pending booking
    booking.ride.available_seats += booking.seats
    
    # Reject the booking
    booking.status = Booking.STATUS_REJECTED
    db.session.commit()
    
    # Send notification to passenger (you can implement this later)
    flash('Booking rejected.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/booking/<int:booking_id>/remove', methods=['POST'])
@login_required
def remove_passenger(booking_id):
    """Remove a passenger from a ride."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is the driver
    if booking.ride.driver_id != current_user.id:
        flash('You are not authorized to remove this passenger.', 'error')
        return redirect(url_for('dashboard'))
        
    # Check if booking is confirmed
    if booking.status != Booking.STATUS_CONFIRMED:
        flash('Can only remove confirmed passengers.', 'error')
        return redirect(url_for('dashboard'))
        
    # Store passenger info for flash message
    passenger_name = booking.passenger.username
    
    # Restore the seats since this was a confirmed booking
    booking.ride.available_seats += booking.seats
    
    # Mark booking as cancelled
    booking.status = Booking.STATUS_CANCELLED
    db.session.commit()
    
    flash(f'Passenger {passenger_name} has been removed from the ride.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Route for cancelling a booking."""
    try:
        booking = Booking.query.get_or_404(booking_id)
        if booking.passenger_id != current_user.id:
            flash('You are not authorized to cancel this booking.', 'danger')
        elif not booking.can_cancel():
            flash('This booking cannot be cancelled.', 'danger')
        else:
            # If booking was confirmed, restore the seats
            if booking.status == Booking.STATUS_CONFIRMED:
                booking.ride.available_seats += booking.seats
            elif booking.status == Booking.STATUS_PENDING:
                # Also restore seats for pending bookings since they reduce seats too
                booking.ride.available_seats += booking.seats
            
            booking.status = Booking.STATUS_CANCELLED
            db.session.commit()
            flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling the booking. Please try again.', 'danger')
        app.logger.error(f'Booking cancellation error: {str(e)}')
    
    return redirect(url_for('dashboard'))

@app.route('/ride/<int:ride_id>/mark-complete', methods=['POST'])
@login_required
def mark_ride_complete(ride_id):
    """Driver marks ride as complete."""
    try:
        ride = Ride.query.get_or_404(ride_id)
        
        # Check if current user is the driver
        if ride.driver_id != current_user.id:
            flash('Only the driver can mark this ride as complete.', 'error')
            return redirect(url_for('dashboard'))
        
        # Driver can instantly complete the ride
        ride.marked_complete_by_driver = True
        ride.driver_completed_at = utc_now()
        ride.mark_as_completed(auto=False)
        
        flash('Ride marked as completed! You can now review your passengers.', 'success')
        db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')
        app.logger.error(f'Mark ride complete error: {str(e)}')
    
    return redirect(url_for('dashboard'))

@app.route('/ride/<int:ride_id>/start', methods=['POST'])
@login_required
def start_ride(ride_id):
    """Driver starts the ride."""
    try:
        ride = Ride.query.get_or_404(ride_id)
        
        # Check if current user is the driver
        if ride.driver_id != current_user.id:
            flash('Only the driver can start this ride.', 'error')
            return redirect(url_for('dashboard'))
        
        # Start the ride
        success, message = ride.start_ride()
        
        if success:
            db.session.commit()
            # Notify passengers
            ride.notify_passengers('RIDE_STARTED')
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')
        app.logger.error(f'Start ride error: {str(e)}')
    
    return redirect(url_for('dashboard'))

@app.route('/ride/<int:ride_id>/end', methods=['POST'])
@login_required
def end_ride(ride_id):
    """Driver ends the ride."""
    try:
        ride = Ride.query.get_or_404(ride_id)
        
        # Check if current user is the driver
        if ride.driver_id != current_user.id:
            flash('Only the driver can end this ride.', 'error')
            return redirect(url_for('dashboard'))
        
        # End the ride
        success, message = ride.end_ride(completed_by='DRIVER')
        
        if success:
            db.session.commit()
            # Notify passengers
            ride.notify_passengers('RIDE_ENDED')
            flash(message + ' You can now review your passengers.', 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')
        app.logger.error(f'End ride error: {str(e)}')
    
    return redirect(url_for('dashboard'))

@app.route('/booking/<int:booking_id>/mark-complete', methods=['POST'])
@login_required
def mark_booking_complete(booking_id):
    """Passenger marks their individual ride as complete."""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if current user is the passenger
        if booking.passenger_id != current_user.id:
            flash('You are not authorized to mark this booking as complete.', 'error')
            return redirect(url_for('my_bookings'))
        
        # Use new complete_passenger_ride method
        success, message = booking.complete_passenger_ride()
        
        if success:
            db.session.commit()
            flash(message + ' You can now review your driver.', 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')
        app.logger.error(f'Mark booking complete error: {str(e)}')
    
    return redirect(url_for('my_bookings'))

@app.route('/check-completed-rides')
def check_completed_rides():
    """Background task to auto-complete rides based on time."""
    try:
        # Get all ONGOING rides that should be auto-completed
        rides = Ride.query.filter(Ride.status == Ride.STATUS_ONGOING).all()
        
        completed_count = 0
        for ride in rides:
            if ride.should_auto_complete():
                ride.auto_complete_ride()
                completed_count += 1
        
        if completed_count > 0:
            db.session.commit()
            
        return jsonify({
            'success': True,
            'completed_rides': completed_count
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Auto-complete rides error: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/bookings')
@login_required
def bookings():
    """Redirect to my-bookings for consistency."""
    return redirect(url_for('my_bookings'))

@app.route('/booking/<int:booking_id>/review', methods=['GET', 'POST'])
@login_required
def submit_review(booking_id):
    """Submit a review for a ride (passenger reviewing driver)."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is the passenger
    if booking.passenger_id != current_user.id:
        flash('You are not authorized to review this booking.', 'error')
        return redirect(url_for('my_bookings'))
    
    reviewed_id = booking.ride.driver_id
    review_type = Review.TYPE_PASSENGER_TO_DRIVER
    
    # Check if ride is completed (either ride status or passenger ride status)
    if booking.ride.status != Ride.STATUS_COMPLETED and booking.passenger_ride_status != 'COMPLETED':
        flash('You can only review completed rides.', 'error')
        return redirect(url_for('my_bookings'))
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(
        booking_id=booking_id,
        reviewer_id=current_user.id,
        review_type=review_type
    ).first()
    
    if existing_review:
        flash('You have already reviewed this driver.', 'error')
        return redirect(url_for('my_bookings'))
    
    if request.method == 'POST':
        try:
            flag_type = request.form.get('flag')  # 'green' or 'red'
            comment = request.form.get('comment', '').strip()
            
            if flag_type not in ['green', 'red']:
                flash('Please select a green or red flag.', 'error')
            else:
                # Create the review (rating defaults to flag-based: green=5, red=1)
                rating = 5 if flag_type == 'green' else 1
                
                review = Review(
                    reviewer_id=current_user.id,
                    reviewed_id=reviewed_id,
                    booking_id=booking_id,
                    rating=rating,
                    comment=comment,
                    flag_type=flag_type,
                    review_type=review_type
                )
                
                db.session.add(review)
                
                # Update user flags
                reviewed_user = User.query.get(reviewed_id)
                if flag_type == 'green':
                    reviewed_user.green_flags = (reviewed_user.green_flags or 0) + 1
                elif flag_type == 'red':
                    reviewed_user.red_flags = (reviewed_user.red_flags or 0) + 1
                
                # Update user rating based on flags
                user_reviews = Review.query.filter_by(reviewed_id=reviewed_id).all()
                total_rating = sum(r.rating for r in user_reviews) + rating
                reviewed_user.rating = total_rating / (len(user_reviews) + 1)
                
                db.session.commit()
                
                flash('Thank you for your review!', 'success')
                return redirect(url_for('my_bookings'))
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your review. Please try again.', 'error')
            app.logger.error(f"Review error: {str(e)}")
    
    return render_template('submit_review.html', booking=booking, review_target='driver')


@app.route('/booking/<int:booking_id>/rate-passenger', methods=['GET', 'POST'])
@login_required
def rate_passenger(booking_id):
    """Driver rates a passenger after ride completion."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if current user is the driver of this ride
    if booking.ride.driver_id != current_user.id:
        flash('Only the driver can rate passengers.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if ride is completed
    if booking.ride.status != Ride.STATUS_COMPLETED:
        flash('You can only rate passengers after the ride is completed.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if booking was confirmed (passenger actually took the ride)
    if booking.status not in [Booking.STATUS_CONFIRMED, Booking.STATUS_COMPLETED]:
        flash('This passenger did not complete the ride.', 'error')
        return redirect(url_for('view_ride', ride_id=booking.ride_id))
    
    reviewed_id = booking.passenger_id
    review_type = Review.TYPE_DRIVER_TO_PASSENGER
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(
        booking_id=booking_id,
        reviewer_id=current_user.id,
        review_type=review_type
    ).first()
    
    if existing_review:
        flash('You have already rated this passenger.', 'error')
        return redirect(url_for('view_ride', ride_id=booking.ride_id))
    
    if request.method == 'POST':
        try:
            flag_type = request.form.get('flag')  # 'green' or 'red'
            comment = request.form.get('comment', '').strip()
            
            if flag_type not in ['green', 'red']:
                flash('Please select a green or red flag.', 'error')
            else:
                # Create the review (rating defaults to flag-based: green=5, red=1)
                rating = 5 if flag_type == 'green' else 1
                
                review = Review(
                    reviewer_id=current_user.id,
                    reviewed_id=reviewed_id,
                    booking_id=booking_id,
                    rating=rating,
                    comment=comment,
                    flag_type=flag_type,
                    review_type=review_type
                )
                
                db.session.add(review)
                
                # Update passenger flags
                passenger = User.query.get(reviewed_id)
                if flag_type == 'green':
                    passenger.green_flags = (passenger.green_flags or 0) + 1
                elif flag_type == 'red':
                    passenger.red_flags = (passenger.red_flags or 0) + 1
                
                # Update passenger rating based on flags
                user_reviews = Review.query.filter_by(reviewed_id=reviewed_id).all()
                total_rating = sum(r.rating for r in user_reviews) + rating
                passenger.rating = total_rating / (len(user_reviews) + 1)
                
                db.session.commit()
                
                flash(f'Thank you for rating {passenger.username}!', 'success')
                return redirect(url_for('view_ride', ride_id=booking.ride_id))
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your rating. Please try again.', 'error')
            app.logger.error(f"Passenger rating error: {str(e)}")
    
    return render_template('submit_review.html', booking=booking, review_target='passenger')

@app.route('/report', methods=['GET', 'POST'])
@login_required
def submit_report():
    """Submit a new report or feedback."""
    form = ReportForm()
    
    # If user is in an active ride, pre-fill ride information
    active_booking = Booking.query.filter_by(
        passenger_id=current_user.id,
        status=Booking.STATUS_CONFIRMED
    ).join(Ride).filter(
        Ride.start_date <= utc_now(),
        Ride.end_date >= utc_now()
    ).first()
    
    if request.method == 'POST' and form.validate_on_submit():
        report = Report(
            user_id=current_user.id,
            ride_id=active_booking.ride_id if active_booking else None,
            report_type=form.report_type.data,
            subject=form.subject.data,
            description=form.description.data,
            emergency_type=form.emergency_type.data if form.report_type.data == 'emergency' else None,
            location=form.location.data
        )
        
        db.session.add(report)
        db.session.commit()
        
        if form.report_type.data == 'emergency':
            flash('Emergency report submitted! Our team will contact you immediately.', 'warning')
            # TODO: Implement emergency notification system
        else:
            flash('Your report has been submitted successfully.', 'success')
        
        return redirect(url_for('dashboard'))
    
    return render_template('submit_report.html', form=form, active_booking=active_booking)

@app.route('/get-car-models/<make>')
def get_car_models(make):
    """Get car models for a given make."""
    if make in CAR_DATABASE:
        return jsonify(list(CAR_DATABASE[make].keys()))
    return jsonify([])

@app.route('/get-car-details/<make>/<model>')
def get_car_details(make, model):
    """Get car details for a given make and model."""
    if make in CAR_DATABASE and model in CAR_DATABASE[make]:
        return jsonify(CAR_DATABASE[make][model])
    return jsonify({})

@app.route('/add-car', methods=['GET', 'POST'])
@login_required
def add_car():
    """Add a new car."""
    if request.method == 'POST':
        try:
            # Get form data
            make = request.form.get('make')
            model = request.form.get('model')
            year = int(request.form.get('year'))
            color = request.form.get('color')
            license_plate = request.form.get('license_plate').upper()
            
            # Validate inputs
            if not all([make, model, year, color, license_plate]):
                raise ValueError("All fields are required")
                
            if year < 1900 or year > datetime.now().year + 1:
                raise ValueError("Invalid year")
                
            # Check if license plate is already registered
            if Car.query.filter_by(license_plate=license_plate).first():
                raise ValueError("This license plate is already registered")
            
            # Get car details from database
            if make not in CAR_DATABASE or model not in CAR_DATABASE[make]:
                raise ValueError("Invalid car make/model selected")
                
            car_details = CAR_DATABASE[make][model]
            
            # Create car
            car = Car(
                owner_id=current_user.id,
                make=make,
                model=model,
                year=year,
                color=color,
                license_plate=license_plate,
                fuel_type=car_details['fuel_type'],
                mileage=car_details['mileage'],
                ac=True,
                created_at=utc_now()
            )
            
            db.session.add(car)
            db.session.commit()
            
            flash('Car added successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while adding the car. Please try again.', 'error')
    
    return render_template('add_car.html', 
                         now=datetime.now(),
                         car_makes=list(CAR_DATABASE.keys()))

@app.route('/ride/<int:ride_id>')
@login_required
def view_ride(ride_id):
    """View details of a specific ride."""
    ride = Ride.query.get_or_404(ride_id)
    
    # Check if user is the driver
    is_driver = ride.driver_id == current_user.id
    
    # If user is driver, show detailed view with passengers (for active, completed, or cancelled rides)
    if is_driver:
        # Get all bookings for this ride
        bookings = Booking.query.filter_by(ride_id=ride_id).order_by(Booking.created_at).all()
        
        # Check which passengers have been reviewed by driver (driver-to-passenger reviews)
        reviewed_passengers = set()
        for booking in bookings:
            existing_review = Review.query.filter_by(
                booking_id=booking.id,
                reviewer_id=current_user.id,
                review_type=Review.TYPE_DRIVER_TO_PASSENGER
            ).first()
            if existing_review:
                reviewed_passengers.add(booking.passenger_id)
        
        return render_template('ride_detail.html', 
                             ride=ride, 
                             bookings=bookings,
                             reviewed_passengers=reviewed_passengers)
    
    # Otherwise redirect to book_ride for regular view
    return redirect(url_for('book_ride', ride_id=ride_id))

@app.route('/ride/<int:ride_id>/cancel', methods=['POST'])
@login_required
def cancel_ride(ride_id):
    """Cancel a ride."""
    ride = Ride.query.get_or_404(ride_id)
    
    # Check if user is the driver
    if ride.driver_id != current_user.id:
        flash('You can only cancel rides you are driving.', 'error')
        return redirect(url_for('my_rides'))
    
    # Check if ride can be cancelled
    if ride.start_date <= utc_now():
        flash('Cannot cancel a ride that has already started.', 'error')
        return redirect(url_for('my_rides'))
    
    # Cancel all pending and confirmed bookings and restore seats
    for booking in ride.bookings:
        if booking.status in [Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]:
            # Restore seats
            ride.available_seats += booking.seats
            booking.status = Booking.STATUS_CANCELLED
    
    ride.status = Ride.STATUS_CANCELLED
    db.session.commit()
    
    flash('Ride cancelled successfully.', 'success')
    return redirect(url_for('my_rides'))

@app.route('/user/<int:user_id>/reviews')
@login_required
def user_reviews(user_id):
    """View reviews for a specific user."""
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(reviewed_id=user_id).order_by(Review.created_at.desc()).all()
    
    return render_template('reviews.html', user=user, reviews=reviews)

@app.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    """View a user's profile."""
    user = User.query.get_or_404(user_id)
    
    # Get user's rides (if driver) and bookings (if passenger)
    rides_as_driver = Ride.query.filter_by(driver_id=user_id).order_by(Ride.start_date.desc()).all()
    bookings_as_passenger = Booking.query.filter_by(passenger_id=user_id).order_by(Booking.created_at.desc()).all()
    
    # Get user's reviews
    reviews = Review.query.filter_by(reviewed_id=user_id).order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template(
        'user_profile.html', 
        user=user, 
        rides=rides_as_driver, 
        bookings=bookings_as_passenger,
        reviews=reviews,
        current_time=utc_now()
    )

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handle chatbot requests with Gemini AI."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        if not app.config['GEMINI_API_KEY']:
            return jsonify({
                'response': 'I apologize, but the chatbot service is currently unavailable. Please contact support for assistance.'
            }), 200
        
        # Create Gemini client with new API
        client = genai.Client(api_key=app.config['GEMINI_API_KEY'])
        
        # System prompt for the chatbot
        system_instruction = """You are RideShareBot, an AI assistant for a Ride-Share web application. The app allows users to register, log in, offer rides, search for rides, book rides, manage bookings, add cars, review other users, and submit reports or feedback. Users can be drivers or passengers. The app uses Google Maps, supports file uploads (such as license and vehicle photos), and has a wallet for ride expenses.

Your tasks:
- Answer questions about using the site (e.g., how to register, offer a ride, book a ride, cancel a booking, add a car, submit a review, or report an issue).
- Explain features like ride packages (daily, weekly, biweekly, monthly), wallet/expenses, and user reviews.
- Help users troubleshoot common issues (e.g., login problems, booking errors, uploading documents).
- Guide users to the correct page or form for their needs.
- Be friendly, concise, and clear. If you don't know the answer, suggest contacting support.

Always answer as if you are part of the Ride-Share site's support team. If a user asks about something outside the Ride-Share app, politely decline to answer.

If you need more information, ask the user for clarification."""
        
        # Generate response using new API
        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=user_message,
            config={
                'system_instruction': system_instruction,
                'temperature': 0.7,
            }
        )
        
        return jsonify({
            'response': response.text
        }), 200
        
    except Exception as e:
        app.logger.error(f'Chatbot error: {str(e)}')
        return jsonify({
            'response': 'I apologize, but I encountered an error. Please try again or contact support if the issue persists.'
        }), 200

# ============================================
# MAP FEATURES ROUTES
# ============================================

@app.route('/admin/map')
@login_required
def admin_map():
    """Admin map dashboard showing all rides and SOS emergencies."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all active rides
    rides = Ride.query.filter(
        Ride.status.in_(['UPCOMING', 'ONGOING'])
    ).all()
    
    # Get all SOS alerts
    sos_users = User.query.filter_by(sos_active=True).all()
    
    return render_template('admin_map.html', rides=rides, sos_users=sos_users)

@app.route('/api/rides/map')
@login_required
def get_rides_for_map():
    """API endpoint to get ride data for map display."""
    rides = Ride.query.filter(
        Ride.status.in_(['UPCOMING', 'ONGOING'])
    ).all()
    
    rides_data = []
    for ride in rides:
        rides_data.append({
            'id': ride.id,
            'driver': {
                'id': ride.driver.id,
                'username': ride.driver.username,
                'email': ride.driver.email
            },
            'start_location': ride.start_location,
            'end_location': ride.end_location,
            'start_lat': ride.start_lat if hasattr(ride, 'start_lat') else 19.0760,
            'start_lng': ride.start_lng if hasattr(ride, 'start_lng') else 72.8777,
            'end_lat': ride.end_lat if hasattr(ride, 'end_lat') else 19.0760,
            'end_lng': ride.end_lng if hasattr(ride, 'end_lng') else 72.8777,
            'available_seats': ride.available_seats,
            'price_per_seat': ride.price_per_seat,
            'start_date': ride.start_date.isoformat(),
            'status': ride.status
        })
    
    return jsonify(rides_data)

@app.route('/api/sos/trigger', methods=['POST'])
@login_required
def trigger_sos():
    """Trigger SOS emergency alert."""
    data = request.get_json()
    
    current_user.sos_active = True
    current_user.sos_location = data.get('location', 'Unknown')
    current_user.sos_timestamp = utc_now()
    current_user.sos_message = data.get('message', 'Emergency!')
    
    db.session.commit()
    
    app.logger.warning(f'🚨 SOS ALERT: User {current_user.username} at {current_user.sos_location}')
    
    return jsonify({'success': True, 'message': 'SOS alert sent to admin'})

@app.route('/api/sos/cancel', methods=['POST'])
@login_required
def cancel_sos():
    """Cancel SOS emergency alert."""
    current_user.sos_active = False
    current_user.sos_location = None
    current_user.sos_timestamp = None
    current_user.sos_message = None
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'SOS alert cancelled'})

# ============================================
# END OF MAP FEATURES ROUTES
# ============================================

# Application entry point
if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        inspector = inspect(db.engine)
        if not inspector.has_table('user'):
            db.create_all()
            print("Database tables created.")
        
        # Add migrations for new columns
        try:
            # Check if package_type column exists in ride table
            columns = [col['name'] for col in inspector.get_columns('ride')]
            if 'package_type' not in columns:
                print("Adding package_type column to ride table...")
                db.engine.execute('ALTER TABLE ride ADD COLUMN package_type VARCHAR(20) NOT NULL DEFAULT "weekly"')
                print("Migration completed successfully.")
        except Exception as e:
            print(f"Migration error: {e}")
        
        # Add new columns with migrations
        booking_columns = [col['name'] for col in inspector.get_columns('booking')]
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        
        # Add share column to booking table
        if 'share' not in booking_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE booking ADD COLUMN share FLOAT DEFAULT NULL'))
                conn.commit()
        
        # Add contact_number and booking_date to booking table
        if 'contact_number' not in booking_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE booking ADD COLUMN contact_number VARCHAR(20) DEFAULT NULL'))
                conn.commit()
        
        if 'booking_date' not in booking_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE booking ADD COLUMN booking_date DATETIME DEFAULT NULL'))
                conn.commit()
                # Update existing records to use created_at
                conn.execute(text('UPDATE booking SET booking_date = created_at WHERE booking_date IS NULL'))
                conn.commit()
        
        # Add flag columns to user table
        if 'green_flags' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE user ADD COLUMN green_flags INTEGER DEFAULT 0'))
                conn.commit()
        if 'red_flags' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE user ADD COLUMN red_flags INTEGER DEFAULT 0'))
                conn.commit()
        
        # Add flag_type and review_type to review table
        try:
            review_columns = [col['name'] for col in inspector.get_columns('review')]
            if 'flag_type' not in review_columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE review ADD COLUMN flag_type VARCHAR(10) DEFAULT NULL'))
                    conn.commit()
                    print("Added flag_type column to review table.")
            if 'review_type' not in review_columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE review ADD COLUMN review_type VARCHAR(30) DEFAULT NULL'))
                    conn.commit()
                    print("Added review_type column to review table.")
                    # Update existing reviews to set review_type based on booking relationship
                    conn.execute(text("""
                        UPDATE review SET review_type = 'passenger_to_driver' 
                        WHERE review_type IS NULL
                    """))
                    conn.commit()
                    print("Updated existing reviews with default review_type.")
        except Exception as e:
            print(f"Migration error for review table: {e}")
        
        # Add completion tracking fields to ride table
        try:
            ride_columns = [col['name'] for col in inspector.get_columns('ride')]
            if 'marked_complete_by_driver' not in ride_columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE ride ADD COLUMN marked_complete_by_driver BOOLEAN DEFAULT 0'))
                    conn.commit()
                    print("Added marked_complete_by_driver column to ride table.")
            if 'driver_completed_at' not in ride_columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE ride ADD COLUMN driver_completed_at DATETIME DEFAULT NULL'))
                    conn.commit()
                    print("Added driver_completed_at column to ride table.")
            if 'auto_completed' not in ride_columns:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE ride ADD COLUMN auto_completed BOOLEAN DEFAULT 0'))
                    conn.commit()
                    print("Added auto_completed column to ride table.")
        except Exception as e:
            print(f"Migration error for ride table: {e}")
        
        # Add completion tracking fields to booking table
        if 'marked_complete_by_passenger' not in booking_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE booking ADD COLUMN marked_complete_by_passenger BOOLEAN DEFAULT 0'))
                conn.commit()
                print("Added marked_complete_by_passenger column to booking table.")
        if 'passenger_completed_at' not in booking_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE booking ADD COLUMN passenger_completed_at DATETIME DEFAULT NULL'))
                conn.commit()
                print("Added passenger_completed_at column to booking table.")
        
    app.run(debug=True)
