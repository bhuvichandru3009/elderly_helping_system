import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import DISABILITY_TYPES, HELP_TYPES, HelpRequest, User, db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('You are not authorized to access this page.', 'danger')
                return redirect(url_for('dashboard_redirect_route'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def dashboard_redirect():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    if role == 'helper':
        return redirect(url_for('helper_dashboard'))
    if role == 'user':
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        account_type = request.form.get('account_type', '')
        disability_type = request.form.get('disability_type', 'None')

        if not all([name, email, phone, password, confirm_password, account_type]):
            flash('All fields are required.', 'danger')
            return render_template('register.html', disability_types=DISABILITY_TYPES)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', disability_types=DISABILITY_TYPES)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html', disability_types=DISABILITY_TYPES)

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('register.html', disability_types=DISABILITY_TYPES)

        role = 'user' if account_type == 'user' else 'helper'
        if role == 'helper':
            disability_type = 'None'

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            role=role,
            disability_type=disability_type,
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', disability_types=DISABILITY_TYPES)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['role'] = user.role
        flash(f'Welcome, {user.name}!', 'success')
        return dashboard_redirect()

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard_redirect_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return dashboard_redirect()


# ==================== USER ROUTES ====================

@app.route('/user/dashboard')
@login_required(role='user')
def user_dashboard():
    user_id = session['user_id']
    requests = HelpRequest.query.filter_by(user_id=user_id).order_by(
        HelpRequest.created_at.desc()
    ).limit(5).all()
    active_count = HelpRequest.query.filter(
        HelpRequest.user_id == user_id,
        HelpRequest.status.in_(['Pending', 'Accepted']),
    ).count()
    return render_template(
        'user_dashboard.html',
        requests=requests,
        active_count=active_count,
    )


@app.route('/user/create-request', methods=['GET', 'POST'])
@login_required(role='user')
def create_request():
    if request.method == 'POST':
        request_type = request.form.get('request_type', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        emergency = request.form.get('emergency') == 'yes'

        if not all([request_type, description, location]):
            flash('All fields are required.', 'danger')
            return render_template('create_request.html', help_types=HELP_TYPES)

        if request_type not in HELP_TYPES:
            flash('Invalid help request type.', 'danger')
            return render_template('create_request.html', help_types=HELP_TYPES)

        help_request = HelpRequest(
            user_id=session['user_id'],
            request_type=request_type,
            description=description,
            location=location,
            emergency=emergency,
            status='Pending',
        )
        db.session.add(help_request)
        db.session.commit()

        flash('Your help request has been submitted successfully.', 'success')
        return redirect(url_for('my_requests'))

    return render_template('create_request.html', help_types=HELP_TYPES)


@app.route('/user/sos', methods=['POST'])
@login_required(role='user')
def sos_emergency():
    help_request = HelpRequest(
        user_id=session['user_id'],
        request_type='General Assistance',
        description='EMERGENCY SOS - Immediate assistance needed!',
        location=request.form.get('location', 'Not specified').strip() or 'Not specified',
        emergency=True,
        status='Pending',
    )
    db.session.add(help_request)
    db.session.commit()
    flash('Emergency SOS request has been sent! A helper will respond soon.', 'danger')
    return redirect(url_for('user_dashboard'))


@app.route('/user/my-requests')
@login_required(role='user')
def my_requests():
    user_id = session['user_id']
    requests = HelpRequest.query.filter_by(user_id=user_id).order_by(
        HelpRequest.created_at.desc()
    ).all()
    return render_template('my_requests.html', requests=requests)


@app.route('/user/request/<int:request_id>')
@login_required(role='user')
def request_details(request_id):
    help_request = HelpRequest.query.get_or_404(request_id)
    if help_request.user_id != session['user_id']:
        flash('You are not authorized to view this request.', 'danger')
        return redirect(url_for('my_requests'))
    return render_template('request_details.html', req=help_request)


@app.route('/user/cancel/<int:request_id>', methods=['POST'])
@login_required(role='user')
def cancel_request(request_id):
    help_request = HelpRequest.query.get_or_404(request_id)
    if help_request.user_id != session['user_id']:
        flash('You are not authorized to cancel this request.', 'danger')
        return redirect(url_for('my_requests'))
    if help_request.status not in ['Pending', 'Accepted']:
        flash('This request cannot be cancelled.', 'warning')
        return redirect(url_for('request_details', request_id=request_id))

    help_request.status = 'Cancelled'
    db.session.commit()
    flash('Request has been cancelled.', 'info')
    return redirect(url_for('my_requests'))


# ==================== HELPER ROUTES ====================

@app.route('/helper/dashboard')
@login_required(role='helper')
def helper_dashboard():
    available = HelpRequest.query.filter_by(status='Pending').order_by(
        HelpRequest.emergency.desc(),
        HelpRequest.created_at.desc(),
    ).all()
    accepted_count = HelpRequest.query.filter_by(
        helper_id=session['user_id'],
        status='Accepted',
    ).count()
    completed_count = HelpRequest.query.filter_by(
        helper_id=session['user_id'],
        status='Completed',
    ).count()
    return render_template(
        'helper_dashboard.html',
        available=available,
        accepted_count=accepted_count,
        completed_count=completed_count,
    )


@app.route('/helper/available')
@login_required(role='helper')
def available_requests():
    available = HelpRequest.query.filter_by(status='Pending').order_by(
        HelpRequest.emergency.desc(),
        HelpRequest.created_at.desc(),
    ).all()
    return render_template('available_requests.html', available=available)


@app.route('/helper/accept/<int:request_id>', methods=['POST'])
@login_required(role='helper')
def accept_request(request_id):
    help_request = HelpRequest.query.get_or_404(request_id)
    if help_request.status != 'Pending':
        flash('This request is no longer available.', 'warning')
        return redirect(url_for('helper_dashboard'))

    help_request.helper_id = session['user_id']
    help_request.status = 'Accepted'
    db.session.commit()
    flash('Request accepted successfully!', 'success')
    return redirect(url_for('accepted_requests'))


@app.route('/helper/accepted')
@login_required(role='helper')
def accepted_requests():
    requests = HelpRequest.query.filter_by(
        helper_id=session['user_id'],
        status='Accepted',
    ).order_by(HelpRequest.created_at.desc()).all()
    return render_template('accepted_requests.html', requests=requests)


@app.route('/helper/complete/<int:request_id>', methods=['POST'])
@login_required(role='helper')
def complete_request(request_id):
    help_request = HelpRequest.query.get_or_404(request_id)
    if help_request.helper_id != session['user_id']:
        flash('You are not authorized to complete this request.', 'danger')
        return redirect(url_for('accepted_requests'))
    if help_request.status != 'Accepted':
        flash('This request cannot be marked as completed.', 'warning')
        return redirect(url_for('accepted_requests'))

    help_request.status = 'Completed'
    help_request.completed_at = datetime.utcnow()
    db.session.commit()
    flash('Request marked as completed!', 'success')
    return redirect(url_for('completed_requests'))


@app.route('/helper/completed')
@login_required(role='helper')
def completed_requests():
    requests = HelpRequest.query.filter_by(
        helper_id=session['user_id'],
        status='Completed',
    ).order_by(HelpRequest.completed_at.desc()).all()
    return render_template('completed_requests.html', requests=requests)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_helpers = User.query.filter_by(role='helper').count()
    pending_requests = HelpRequest.query.filter_by(status='Pending').count()
    completed_requests_count = HelpRequest.query.filter_by(status='Completed').count()
    recent_requests = HelpRequest.query.order_by(
        HelpRequest.created_at.desc()
    ).limit(10).all()
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_helpers=total_helpers,
        pending_requests=pending_requests,
        completed_requests=completed_requests_count,
        recent_requests=recent_requests,
    )


@app.route('/admin/users')
@login_required(role='admin')
def manage_users():
    users = User.query.filter(User.role != 'admin').order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required(role='admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin account.', 'danger')
        return redirect(url_for('manage_users'))

    HelpRequest.query.filter_by(user_id=user_id).delete()
    HelpRequest.query.filter_by(helper_id=user_id).update({'helper_id': None})
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('manage_users'))


@app.route('/admin/requests')
@login_required(role='admin')
def manage_requests():
    requests = HelpRequest.query.order_by(HelpRequest.created_at.desc()).all()
    return render_template('requests.html', requests=requests)


@app.route('/admin/requests/delete/<int:request_id>', methods=['POST'])
@login_required(role='admin')
def delete_request(request_id):
    help_request = HelpRequest.query.get_or_404(request_id)
    db.session.delete(help_request)
    db.session.commit()
    flash('Request deleted successfully.', 'success')
    return redirect(url_for('manage_requests'))


def init_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                name='System Admin',
                email='admin@example.com',
                phone='9999999999',
                password=generate_password_hash('admin123'),
                role='admin',
                disability_type='None',
            )
            db.session.add(admin)

        if User.query.filter_by(role='user').count() == 0:
            sample_user = User(
                name='John Elder',
                email='user@example.com',
                phone='9876543210',
                password=generate_password_hash('user123'),
                role='user',
                disability_type='Walking Difficulty',
            )
            sample_helper = User(
                name='Mary Helper',
                email='helper@example.com',
                phone='9876543211',
                password=generate_password_hash('helper123'),
                role='helper',
                disability_type='None',
            )
            db.session.add(sample_user)
            db.session.add(sample_helper)
            db.session.commit()

            sample_requests = [
                HelpRequest(
                    user_id=sample_user.id,
                    request_type='Walking Assistance',
                    description='Need help going from my room to the hospital vehicle.',
                    location='Room 12, Block A',
                    emergency=False,
                    status='Pending',
                ),
                HelpRequest(
                    user_id=sample_user.id,
                    request_type='Medicine Assistance',
                    description='Need help picking up my prescription from the pharmacy.',
                    location='City Medical Store',
                    emergency=False,
                    status='Pending',
                ),
            ]
            for req in sample_requests:
                db.session.add(req)

        db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
