# 🚗 Ride-Share Web Application

A modern, full-featured Ride-Share platform built with Flask that connects drivers and passengers for shared rides. This application helps users save money, reduce environmental impact, and build community connections through ride-sharing.

## ✨ Features

### 🎯 Core Features
- **User Authentication & Profiles**: Secure registration, login, and detailed user profiles
- **Ride Management**: Offer rides, search for rides, and manage bookings
- **Booking System**: Request, confirm, and cancel ride bookings
- **Two-Way Review System**: Passengers rate drivers AND drivers rate passengers after completed rides
- **Car Management**: Register and manage multiple vehicles
- **Wallet & Expense Tracking**: Track ride expenses and cost distribution
- **Safety Features**: User verification, reporting system, and emergency contacts

### 🎨 Modern UI/UX Features
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern Dashboard**: Statistics cards, activity feeds, and quick actions
- **Advanced Search**: Multiple filters, sorting options, and auto-complete
- **Interactive Cards**: Hover effects, animations, and smooth transitions
- **Accessibility**: ARIA labels, keyboard navigation, and screen reader support
- **Dark/Light Theme Support**: CSS custom properties for easy theming

### 🔍 Enhanced Search & Filtering
- **Location Auto-complete**: Smart suggestions for cities and locations
- **Advanced Filters**: Package type, price range, seats needed, fuel type, AC preference
- **Sorting Options**: By date, price (low/high), distance
- **Grid/List View**: Toggle between different viewing modes
- **Real-time Results**: Instant search with dynamic filtering

### 📊 Analytics & Statistics
- **User Statistics**: Total rides, bookings, reviews, and cars
- **Ride Analytics**: Cost breakdown, fare distribution, and expense tracking
- **Performance Metrics**: User ratings, green/red flags, and trust scores
- **Dashboard Insights**: Visual charts and progress indicators

### 🛡️ Safety & Trust Features
- **User Verification**: Profile verification and identity checks
- **Flag System**: Green flags for great experiences, red flags for concerns
- **Trust Score**: Calculated from green/red flag ratio
- **Reporting System**: Easy reporting for safety concerns and violations
- **Emergency Contacts**: Quick access to emergency support

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- SQLite (included with Python)

### Installation (Windows)

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd carpooling
   ```

2. **Create and activate a virtual environment**
   ```powershell
   # PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Command Prompt
   python -m venv venv
   venv\Scripts\activate.bat
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```

5. **Run the application**
   The database will be created automatically on first run.
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

### Test Accounts (if seeded)
| Role | Email | Password |
|------|-------|----------|
| User | prajithm23@gmail.com | Prajithm1 |
| User | karthikprakash@gmail.com | Prajithm1 |

## 📱 How to Use

### For Passengers

1. **Create an Account**
   - Register with your email and create a profile
   - Add your contact information and preferences

2. **Search for Rides**
   - Use the search form on the homepage or dashboard
   - Apply filters for location, date, price, and preferences
   - View ride details and driver information

3. **Book a Ride**
   - Select your desired ride
   - Choose number of seats needed
   - Provide pickup and drop-off addresses
   - Submit booking request

4. **Manage Bookings**
   - View all your bookings in the dashboard
   - Cancel bookings if needed
   - Rate drivers after completed rides

4. **Rate Passengers (for Drivers)**
   - After a ride is completed, drivers can rate passengers
   - View ride details and click "Rate Passenger"
   - Provide feedback on punctuality and behavior

### For Drivers

1. **Register Your Car**
   - Add car details including make, model, fuel type, and mileage
   - Upload car photos and documents
   - Set your preferences and availability

2. **Offer Rides**
   - Create ride offers with route, date, and pricing
   - Choose package types (weekly, bi-weekly, monthly)
   - Set available seats and pickup points

3. **Manage Ride Requests**
   - Review booking requests from passengers
   - Accept or reject requests
   - Communicate with passengers

4. **Track Expenses**
   - Log fuel costs, toll charges, and other expenses
   - View cost distribution and earnings
   - Generate expense reports

## 🏗️ Project Structure

```
carpooling/
├── app.py                 # Main Flask application
├── models.py              # Database models and relationships
├── forms.py               # Form definitions and validation
├── requirements.txt       # Python dependencies
├── init_db.py            # Database initialization
├── migrate_db.py         # Database migration script
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── maps.js       # JavaScript functionality
│   └── img/
│       └── carpool.svg   # Application logo
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── dashboard.html    # User dashboard
│   ├── search_rides.html # Ride search page
│   ├── user_profile.html # User profile page
│   └── admin/           # Admin templates
└── instance/            # Database files
    └── carpooling.db    # SQLite database
```

## 🎨 UI/UX Enhancements

### Modern Design Elements
- **Gradient Backgrounds**: Beautiful color gradients throughout the application
- **Card-based Layout**: Clean, organized information presentation
- **Hover Effects**: Interactive elements with smooth animations
- **Icon Integration**: Bootstrap Icons for consistent visual language
- **Typography**: Modern font hierarchy and spacing

### Accessibility Features
- **ARIA Labels**: Proper labeling for screen readers
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: High contrast ratios for readability
- **Focus Indicators**: Clear focus states for interactive elements
- **Semantic HTML**: Proper HTML structure for accessibility

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Flexible Grid**: Bootstrap grid system for responsive layouts
- **Touch-Friendly**: Large touch targets for mobile users
- **Adaptive Navigation**: Collapsible navigation for small screens

## 🔧 Technical Features

### Backend Features
- **Flask Framework**: Lightweight and flexible web framework
- **SQLAlchemy ORM**: Database abstraction and relationship management
- **Flask-Login**: User authentication and session management
- **WTForms**: Form handling and validation
- **SQLite Database**: Lightweight, file-based database

### Frontend Features
- **Bootstrap 5**: Modern CSS framework for responsive design
- **Bootstrap Icons**: Comprehensive icon library
- **Custom CSS**: Tailored styling with CSS custom properties
- **JavaScript**: Interactive features and form validation
- **AJAX**: Dynamic content loading and form submission

### Security Features
- **Password Hashing**: Secure password storage with bcrypt
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Server-side form validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Output escaping and sanitization

## 📊 Database Schema

### Core Tables
- **Users**: User accounts, profiles, and authentication
- **Rides**: Ride offers with routes, dates, and pricing
- **Bookings**: Passenger bookings and ride requests
- **Cars**: Vehicle information and specifications
- **Reviews**: User ratings and feedback
- **Reports**: Safety reports and user complaints
- **Expenses**: Ride cost tracking and distribution
- **Wallets**: Financial tracking and transactions

### Key Relationships
- Users can offer multiple rides (one-to-many)
- Users can make multiple bookings (one-to-many)
- Rides can have multiple bookings (one-to-many)
- Users can have multiple cars (one-to-many)
- Users can give/receive multiple reviews (many-to-many)

## 🚀 Deployment

### Local Development
```bash
# Run in development mode
export FLASK_ENV=development
python app.py
```

### Production Deployment
1. **Set up a production server** (e.g., Ubuntu with Nginx)
2. **Install Python and dependencies**
3. **Configure environment variables**
4. **Set up a production database** (PostgreSQL recommended)
5. **Configure Nginx as reverse proxy**
6. **Use Gunicorn as WSGI server**

### Environment Variables
```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/carpooling
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bootstrap**: For the responsive CSS framework
- **Bootstrap Icons**: For the comprehensive icon library
- **Flask**: For the web framework
- **SQLAlchemy**: For the ORM and database management
- **Community**: For feedback and suggestions

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Email: support@rideshare-app.com
- Documentation: [docs.carpooling-app.com](https://docs.carpooling-app.com)

## 🔮 Future Enhancements

### Planned Features
- **Real-time Chat**: In-app messaging between users
- **Payment Integration**: Online payment processing
- **Mobile App**: Native iOS and Android applications
- **AI Matching**: Smart ride matching algorithms
- **Route Optimization**: GPS integration and route planning
- **Social Features**: User groups and community features
- **Analytics Dashboard**: Advanced reporting and insights
- **API Integration**: Third-party service integrations

### Technical Improvements
- **Microservices Architecture**: Scalable service-based design
- **Caching Layer**: Redis for improved performance
- **Message Queue**: Celery for background tasks
- **Monitoring**: Application performance monitoring
- **Testing**: Comprehensive test suite
- **CI/CD**: Automated deployment pipeline

---

**Made with ❤️ for the carpooling community**
