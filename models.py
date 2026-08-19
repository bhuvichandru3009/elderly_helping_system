from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

HELP_TYPES = [
    'Walking Assistance',
    'Food Assistance',
    'Medicine Assistance',
    'Hospital Assistance',
    'Shopping Assistance',
    'Household Assistance',
    'Reading Assistance',
    'General Assistance',
]

DISABILITY_TYPES = [
    'Walking Difficulty',
    'Hand Disability',
    'Visual Difficulty',
    'Hearing Difficulty',
    'Other',
    'None',
]

REQUEST_STATUSES = ['Pending', 'Accepted', 'Completed', 'Cancelled']


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    disability_type = db.Column(db.String(50), default='None')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship(
        'HelpRequest',
        backref='requester',
        foreign_keys='HelpRequest.user_id',
        lazy=True,
    )
    accepted_requests = db.relationship(
        'HelpRequest',
        backref='helper',
        foreign_keys='HelpRequest.helper_id',
        lazy=True,
    )

    def __repr__(self):
        return f'<User {self.email}>'


class HelpRequest(db.Model):
    __tablename__ = 'help_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    helper_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    request_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    emergency = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<HelpRequest {self.id} - {self.status}>'
