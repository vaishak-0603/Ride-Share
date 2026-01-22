"""
Admin Routes for Ride-Share Application
This module contains all admin panel routes and functionality.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, text
from app import app, db, User, Ride, Booking, Report, AdminLog, utc_now


def admin_required(f):
    """Decorator to require admin privileges for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        if not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def log_admin_action(action, target_type=None, target_id=None, details=None):
    """Helper function to log admin actions."""
    try:
        log = AdminLog(
            admin_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Failed to log admin action: {str(e)}")


def _time_ago(dt):
    """Helper to calculate time ago."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds // 3600 > 0:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds // 60 > 0:
        return f"{diff.seconds // 60}m ago"
    else:
        return "just now"


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_admin:
                login_user(user)
                log_admin_action('Admin login', details=f'IP: {request.remote_addr}')
                flash('Welcome to the admin panel!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Access denied. Administrator privileges required.', 'error')
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
@admin_required
def admin_logout():
    """Admin logout."""
    log_admin_action('Admin logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics."""
    # Calculate statistics
    total_users = User.query.count()
    new_users_month = User.query.filter(
        User.created_at >= datetime.now() - timedelta(days=30)
    ).count()
    
    total_rides = Ride.query.count()
    active_rides = Ride.query.filter(
        Ride.status.in_([Ride.STATUS_UPCOMING, Ride.STATUS_ONGOING])
    ).count()
    
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status=Booking.STATUS_PENDING).count()
    
    # SOS and reports
    active_sos = Report.query.filter_by(
        report_type='emergency',
        status='pending'
    ).count()
    pending_reports = Report.query.filter_by(status='pending').count()
    
    # Trust metrics
    total_green_flags = db.session.query(func.sum(User.green_flags)).scalar() or 0
    total_red_flags = db.session.query(func.sum(User.red_flags)).scalar() or 0
    total_flags = total_green_flags + total_red_flags
    avg_trust_score = round((total_green_flags / total_flags * 100) if total_flags > 0 else 0, 1)
    
    stats = {
        'total_users': total_users,
        'new_users_month': new_users_month,
        'total_rides': total_rides,
        'active_rides': active_rides,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'active_sos': active_sos,
        'pending_reports': pending_reports,
        'total_green_flags': total_green_flags,
        'total_red_flags': total_red_flags,
        'avg_trust_score': avg_trust_score
    }
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_rides = Ride.query.order_by(Ride.created_at.desc()).limit(5).all()
    
    recent_activity = []
    for user in recent_users:
        recent_activity.append({
            'icon': 'person-plus',
            'color': 'primary',
            'title': f'New user: {user.username}',
            'description': f'Registered from {user.email}',
            'time_ago': _time_ago(user.created_at)
        })
    
    for ride in recent_rides:
        recent_activity.append({
            'icon': 'car-front',
            'color': 'success',
            'title': f'New ride: {ride.origin} → {ride.destination}',
            'description': f'By {ride.driver.username}',
            'time_ago': _time_ago(ride.created_at)
        })
    
    # Sort by time
    recent_activity.sort(key=lambda x: x['time_ago'])
    
    # User growth data (last 30 days)
    user_growth_labels = []
    user_growth_data = []
    for i in range(29, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        count = User.query.filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()
        user_growth_labels.append(day.strftime('%b %d'))
        user_growth_data.append(count)
    
    # Package distribution
    package_distribution = [
        Ride.query.filter_by(package_type='daily').count(),
        Ride.query.filter_by(package_type='weekly').count(),
        Ride.query.filter_by(package_type='biweekly').count(),
        Ride.query.filter_by(package_type='monthly').count()
    ]
    
    pending_sos_count = active_sos
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_activity=recent_activity,
                         user_growth_labels=user_growth_labels,
                         user_growth_data=user_growth_data,
                         package_distribution=package_distribution,
                         pending_sos_count=pending_sos_count)


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin user management page."""
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    if sort_by == 'username':
        query = query.order_by(User.username)
    elif sort_by == 'email':
        query = query.order_by(User.email)
    else:
        query = query.order_by(User.created_at.desc())
    
    users = query.paginate(page=request.args.get('page', 1, type=int), per_page=50, error_out=False)
    
    pending_sos_count = Report.query.filter_by(report_type='emergency', status='pending').count()
    
    return render_template('admin/users/list.html',
                         users=users,
                         search=search,
                         sort_by=sort_by,
                         pending_sos_count=pending_sos_count)


@app.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    """Admin user detail view."""
    user = User.query.get_or_404(user_id)
    
    rides_offered = Ride.query.filter_by(driver_id=user_id).count()
    rides_taken = Booking.query.filter_by(passenger_id=user_id, status=Booking.STATUS_COMPLETED).count()
    
    total_offered = Ride.query.filter_by(driver_id=user_id).count()
    completed_offered = Ride.query.filter_by(driver_id=user_id, status=Ride.STATUS_COMPLETED).count()
    completion_rate = round((completed_offered / total_offered * 100) if total_offered > 0 else 0, 1)
    
    pending_sos_count = Report.query.filter_by(report_type='emergency', status='pending').count()
    
    return render_template('admin/users/detail.html',
                         user=user,
                         rides_offered=rides_offered,
                         rides_taken=rides_taken,
                         completion_rate=completion_rate,
                         pending_sos_count=pending_sos_count)


@app.route('/admin/rides')
@login_required
@admin_required
def admin_rides():
    """Admin ride management page."""
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Ride.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.join(User).filter(
            db.or_(
                Ride.start_location.ilike(f'%{search}%'),
                Ride.end_location.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%')
            )
        )
    
    rides = query.order_by(Ride.start_date.desc()).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=50,
        error_out=False
    )
    
    pending_sos_count = Report.query.filter_by(report_type='emergency', status='pending').count()
    
    return render_template('admin/rides/list.html',
                         rides=rides,
                         status_filter=status_filter,
                         search=search,
                         pending_sos_count=pending_sos_count)


@app.route('/admin/rides/<int:ride_id>')
@login_required
@admin_required
def admin_ride_detail(ride_id):
    """Admin ride detail view."""
    ride = Ride.query.get_or_404(ride_id)
    pending_sos_count = Report.query.filter_by(report_type='emergency', status='pending').count()
    
    return render_template('admin/rides/detail.html',
                         ride=ride,
                         pending_sos_count=pending_sos_count)


@app.route('/admin/safety')
@login_required
@admin_required
def admin_safety():
    """Admin safety center - SOS alerts and reports."""
    sos_alerts = Report.query.filter_by(
        report_type='emergency',
        status='pending'
    ).order_by(Report.created_at.desc()).all()
    
    reports = Report.query.filter_by(
        status='pending'
    ).order_by(Report.created_at.desc()).limit(20).all()
    
    pending_sos_count = len(sos_alerts)
    
    return render_template('admin/safety/reports.html',
                         sos_alerts=sos_alerts,
                         reports=reports,
                         pending_sos_count=pending_sos_count)


@app.route('/admin/reports/<int:report_id>/resolve', methods=['POST'])
@login_required
@admin_required
def admin_resolve_report(report_id):
    """Resolve a report."""
    report = Report.query.get_or_404(report_id)
    report.status = 'resolved'
    report.resolved_at = utc_now()
    db.session.commit()
    
    log_admin_action('Resolved report', 'report', report_id, f'Type: {report.report_type}')
    
    flash('Report has been resolved.', 'success')
    return redirect(url_for('admin_safety'))


@app.route('/admin/reports/<int:report_id>/dismiss', methods=['POST'])
@login_required
@admin_required
def admin_dismiss_report(report_id):
    """Dismiss a report."""
    report = Report.query.get_or_404(report_id)
    report.status = 'dismissed'
    report.resolved_at = utc_now()
    db.session.commit()
    
    log_admin_action('Dismissed report', 'report', report_id, f'Type: {report.report_type}')
    
    flash('Report has been dismissed.', 'success')
    return redirect(url_for('admin_safety'))
