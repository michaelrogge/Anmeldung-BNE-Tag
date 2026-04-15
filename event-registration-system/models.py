from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Event(db.Model):
    """Veranstaltungsmodell"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    max_participants = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    workshops = db.relationship('Workshop', backref='event', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Event {self.name}>'

class Workshop(db.Model):
    """Workshop-Modell"""
    __tablename__ = 'workshops'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    max_capacity = db.Column(db.Integer, nullable=False)
    current_capacity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    registrations = db.relationship('WorkshopRegistration', backref='workshop', lazy=True, cascade='all, delete-orphan')
    
    def is_full(self):
        """Prüft, ob Workshop voll ist"""
        return self.current_capacity >= self.max_capacity
    
    def get_available_spots(self):
        """Gibt verfügbare Plätze zurück"""
        return max(0, self.max_capacity - self.current_capacity)
    
    def __repr__(self):
        return f'<Workshop {self.name}>'

class Participant(db.Model):
    """Teilnehmer-Modell"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20))
    organization = db.Column(db.String(255))
    dietary_restrictions = db.Column(db.String(255))
    additional_info = db.Column(db.Text)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    confirmation_sent = db.Column(db.Boolean, default=False)
    confirmation_date = db.Column(db.DateTime)
    
    # Beziehungen
    registrations = db.relationship('Registration', backref='participant', lazy=True, cascade='all, delete-orphan')
    workshop_registrations = db.relationship('WorkshopRegistration', backref='participant', lazy=True, cascade='all, delete-orphan')
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Participant {self.get_full_name()}>'

class Registration(db.Model):
    """Anmelde-Modell (Beziehung zwischen Teilnehmer und Event)"""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='registered')  # registered, confirmed, cancelled
    
    # Beziehung zu Workshop-Anmeldungen
    workshop_selections = db.relationship('WorkshopRegistration', backref='main_registration', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('participant_id', 'event_id', name='unique_participant_event'),)
    
    def __repr__(self):
        return f'<Registration {self.participant.get_full_name()} -> {self.event.name}>'

class WorkshopRegistration(db.Model):
    """Workshop-Auswahl durch Teilnehmer"""
    __tablename__ = 'workshop_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='registered')  # registered, waitlist, cancelled
    
    __table_args__ = (db.UniqueConstraint('participant_id', 'workshop_id', name='unique_participant_workshop'),)
    
    def __repr__(self):
        return f'<WorkshopRegistration {self.participant.get_full_name()} -> {self.workshop.name}>'
