# 🚗 Carpooling Web Application - Comprehensive Documentation

## 1. Abstract / Overview
The Carpooling Web Application is a modern, Flask-based platform designed to facilitate ride-sharing between drivers and passengers. In an era of increasing fuel costs and environmental concerns, this application provides a practical solution by allowing users to share rides, split costs, and reduce their carbon footprint. The platform connects vehicle owners (drivers) with commuters (passengers) traveling along similar routes, fostering a community-driven approach to transportation.

## 2. Problem Statement
Urban transportation faces several critical challenges:
*   **Rising Costs**: Fuel prices and maintenance costs are steadily increasing, making solo commuting expensive.
*   **Traffic Congestion**: excessive number of single-occupancy vehicles contribute significantly to traffic jams.
*   **Environmental Impact**: High carbon emissions from private transport worsen air quality and contribute to climate change.
*   **Inefficient Resource Usage**: Most private cars run with 3-4 empty seats, representing wasted capacity.

## 3. Objectives
*   **Cost Efficiency**: To enable drivers to offset vehicle running costs and offer passengers affordable travel alternatives.
*   **Sustainability**: To reduce the number of vehicles on the road, thereby lowering carbon emissions and traffic congestion.
*   **Connectivity**: To build a trusted community of commuters.
*   **Convenience**: To provide a seamless, user-friendly platform for finding and booking rides.

## 4. Scope of the Project
The project scope encompasses a web-based application serving two primary user roles: Drivers and Passengers.
*   **User Management**: Registration, authentication, and profile management.
*   **Ride Operations**: Creation of ride offers, searching, booking, and cancellation.
*   **Safety & Trust**: User verification, driver license/photo uploads, and a rating/review system.
*   **Financials**: Cost-calculation transparency (not payment processing).
*   **Platform**: Responsive web interface accessible on desktop and mobile browsers.

## 5. Technology Stack
### Backend
*   **Language**: Python 3.8+
*   **Framework**: Flask (Microframework)
*   **ORM**: SQLAlchemy (Database abstraction)
*   **Authentication**: Flask-Login
*   **Forms**: Flask-WTF & WTForms
*   **Environment**: Dotenv for configuration

### Frontend
*   **Templating**: Jinja2 (server-side rendering)
*   **Styling**: Bootstrap 5 (CSS Framework)
*   **Icons**: Bootstrap Icons
*   **Scripting**: Vanilla JavaScript
*   **Maps**: Google Maps API (for location services)

### Database
*   **Development**: SQLite
*   **Production**: PostgreSQL (Recommended)

## 6. System Architecture
The application follows the **Model-View-Controller (MVC)** architectural pattern:
*   **Model (`models.py`)**: Defines the data structure (User, Ride, Booking) and handles database interactions via SQLAlchemy.
*   **View (`templates/`)**: Renders the user interface using HTML/CSS and Jinja2 templates.
*   **Controller (`app.py`)**: Handles incoming HTTP requests, processes business logic, interacts with models, and returns the appropriate views.

The system is designed as a monolithic web application where the server handles both API logic and HTML rendering.

## 7. Modules and Features
### 7.1 User Module
*   **Registration/Login**: Secure access with email/password.
*   **Profile**: Manage personal details and view statistics (ratings, rides taken).

### 7.2 Ride Module
*   **Offer Ride**: Drivers can list rides with origin, destination, time, and seat availability.
*   **Search**: Advanced search filters (date, price, package type, amenities).
*   **Ride Management**: Start, end, or cancel rides.

### 7.3 Booking Module
*   **Book Ride**: Passengers can request seats.
*   **Approval**: Drivers can accept or reject booking requests.
*   **Status Tracking**: Track booking status (Pending, Confirmed, Completed).

### 7.4 Safety Module
*   **Verification**: Mandatory upload of license and vehicle photos for drivers.
*   **Report System**: Users can report issues or emergencies.

### 7.5 Review Module
*   **Ratings**: 1-5 star ratings.
*   **Comments**: Qualitative feedback.
*   **Two-way Reviews**: Drivers rate passengers and vice versa.

## 8. Workflow
1.  **Onboarding**: User registers and logs in.
2.  **Role Selection**: User can act as a driver (offering rides) or passenger (booking rides).
3.  **Ride Creation (Driver)**:
    *   Driver inputs route and car details.
    *   Uploads safety verification specific photos.
    *   System calculates estimated cost.
    *   Ride is published.
4.  **Booking Process (Passenger)**:
    *   Passenger searches for a ride.
    *   Sends a booking request for `N` seats.
    *   Driver confirms the request.
5.  **The Journey**:
    *   Driver starts the ride on the app.
    *   Journey takes place.
    *   Driver ends the ride upon arrival.
6.  **Post-Ride**:
    *   System marks rides/bookings as completed.
    *   Users leave reviews for each other.

## 9. Security Features
*   **Password Hashing**: Uses `bcrypt` to salt and hash passwords before storage.
*   **Session Management**: Secure session handling via `Flask-Login`.
*   **CSRF Protection**: All forms are protected against Cross-Site Request Forgery using `Flask-WTF`.
*   **Input Validation**: Strict validation on client and server sides to prevent injection attacks.
*   **Secure File Uploads**: Filenames are sanitized, and unique IDs are verified to prevent file overwrites or malicious uploads.
*   **Access Control**: Route decorators (`@login_required`) ensure unauthorized users cannot access restricted pages.

## 10. Database Information
The database schema consists of several relational tables:
*   **Users**: Stores user credentials and profile stats.
*   **Cars**: Stores vehicle details (Make, Model, Plate, Fuel Type).
*   **Rides**: Core entity linking Drivers, Cars, and Routes.
*   **Bookings**: Junction table linking Passengers to Rides with status.
*   **Reviews**: Stores ratings and feedback text.
*   **Wallets/Expenses**: Tables for tracking cost metrics.

Relationships are managed via Foreign Keys, ensuring data integrity (e.g., a Ride must belong to a valid User).

## 11. UI Description
The User Interface is built with **Bootstrap 5**, ensuring a responsive and modern aesthetic.
*   **Dashboard**: A centralized hub displaying active rides, booking status, and quick action cards.
*   **Forms**: Clean, validated input fields with clear error messaging.
*   **Cards**: Rides are displayed as interactive cards showing key details (Price, Time, Driver) at a glance.
*   **Navigation**: A responsive navbar that collapses on mobile devices.
*   **Color Palette**: Uses semantic colors (Green for success/available, Red for actions/errors, Blue for primary actions).

## 12. Testing
*   **Unit Testing**: Python's `unittest` framework can be used to test individual models and route logic.
*   **Manual Testing**: Rigorous manual testing has been performed on:
    *   Authentication flows.
    *   Ride lifecycle (Start -> End).
    *   Booking concurrency (preventing overbooking).
    *   File upload constraints.

## 13. Deployment Details
*   **Environment Variables**: Configuration is separated from code using `.env` files.
*   **Web Server**: Recommendations include using Gunicorn (WSGI HTTP Server) behind Nginx (Reverse Proxy).
*   **Database Migration**: Scripts provided (`fix_sequences.py`) to handle database state transitions.
*   **Static Files**: Configured to be served efficiently by the web server in production.

## 14. Advantages
*   **Economic**: Significant cost savings for all parties.
*   **Ecological**: Reduces carbon footprint per traveler.
*   **Social**: Reduces traffic congestion and builds community.
*   **Flexibility**: Users can choose rides based on specific needs (AC, Luggage, Time).

## 15. Disadvantages
*   **Trust Barrier**: Users may be hesitant to travel with strangers (mitigated by verification).
*   **Schedule Rigidity**: Carpooling requires adherence to fixed items, offering less flexibility than solo driving or on-demand cabs.
*   **Dependency**: Passengers are dependent on the driver's reliability.

## 16. Future Implementations
*   **Real-time Chat**: Integrated messaging for coordination.
*   **Payment Gateway**: Integrated stripe/Razorpay for automatic fare splitting.
*   **Mobile Application**: Native iOS/Android apps for better location tracking.
*   **Live Tracking**: Real-time GPS tracking of the ride on the map.
*   **AI Matching**: Smart algorithms to suggest best ride matches based on historic routes.

## 17. Conclusion
The Carpooling Web Application serves as a robust prototype for a community-led transport solution. It successfully implements the core logic of ride-sharing—discovery, booking, and management—wrapped in a secure and user-friendly interface. By addressing the key pillars of cost, convenience, and sustainability, it lays a strong foundation for a scalable transportation platform.
