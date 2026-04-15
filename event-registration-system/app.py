import io
import os
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from models import db, Event, Workshop, Participant, Registration, WorkshopRegistration
from utils import export_to_csv, export_to_excel, validate_email, admin_required, get_registration_summary
from email_service import EmailService
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Flask-App Factory"""
    app = Flask(__name__)
    
    # Konfiguration
    from config import config
    app.config.from_object(config[config_name])
    
    # Datenbank initialisieren
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        _create_demo_data()
    
    # Routes
    
    @app.route('/')
    def index():
        """Startseite"""
        events = Event.query.all()
        return render_template('index.html', events=events)
    
    @app.route('/event/<int:event_id>')
    def event_detail(event_id):
        """Event-Details und Registrierungsformular"""
        event = Event.query.get_or_404(event_id)
        workshops = Workshop.query.filter_by(event_id=event_id).all()
        
        return render_template(
            'registration.html',
            event=event,
            workshops=workshops
        )
    
    @app.route('/api/workshop-status/<int:workshop_id>')
    def get_workshop_status(workshop_id):
        """Gibt Workshop-Verfügbarkeit als JSON zurück"""
        workshop = Workshop.query.get_or_404(workshop_id)
        
        return jsonify({
            'id': workshop.id,
            'name': workshop.name,
            'is_full': workshop.is_full(),
            'current_capacity': workshop.current_capacity,
            'max_capacity': workshop.max_capacity,
            'available_spots': workshop.get_available_spots()
        })
    
    @app.route('/api/register', methods=['POST'])
    def register_participant():
        """API für Teilnehmer-Registrierung"""
        try:
            data = request.get_json()
            
            # Validierung
            errors = []
            
            if not data.get('first_name'):
                errors.append('Vorname erforderlich')
            if not data.get('last_name'):
                errors.append('Nachname erforderlich')
            if not data.get('email') or not validate_email(data['email']):
                errors.append('Gültige Email erforderlich')
            if not data.get('workshops') or len(data['workshops']) == 0:
                errors.append('Mindestens ein Workshop erforderlich')
            
            if errors:
                return jsonify({'success': False, 'errors': errors}), 400
            
            # Duplikat-Prüfung
            existing = Participant.query.filter_by(email=data['email']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'errors': ['Email bereits registriert']
                }), 409
            
            # Teilnehmer erstellen
            participant = Participant(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone'),
                organization=data.get('organization'),
                dietary_restrictions=data.get('dietary_restrictions'),
                additional_info=data.get('additional_info')
            )
            db.session.add(participant)
            db.session.flush()
            
            # Event-Anmeldung erstellen
            event_id = data['event_id']
            registration = Registration(
                participant_id=participant.id,
                event_id=event_id,
                status='registered'
            )
            db.session.add(registration)
            db.session.flush()
            
            # Workshop-Auswahlen
            for workshop_id in data['workshops']:
                workshop = Workshop.query.get(workshop_id)
                if not workshop or workshop.is_full():
                    return jsonify({
                        'success': False,
                        'errors': [f'Workshop {workshop.name if workshop else "unbekannt"} ist voll']
                    }), 409
                
                workshop_reg = WorkshopRegistration(
                    registration_id=registration.id,
                    workshop_id=workshop_id,
                    participant_id=participant.id,
                    status='registered'
                )
                workshop.current_capacity += 1
                db.session.add(workshop_reg)
            
            db.session.commit()
            
            # Bestätigungsemail versenden
            event = Event.query.get(event_id)
            workshops = [wr.workshop for wr in registration.workshop_selections]
            
            if EmailService.send_confirmation_email(participant, event, workshops):
                participant.confirmation_sent = True
                participant.confirmation_date = datetime.utcnow()
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Anmeldung erfolgreich! Bestätigungsemail wurde versendet.',
                'participant_id': participant.id
            }), 201
        
        except Exception as e:
            logger.error(f"Registrierungsfehler: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'errors': ['Registrierung fehlgeschlagen']
            }), 500
    
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Admin-Login"""
        if request.method == 'POST':
            password = request.form.get('password')
            admin_pass = app.config.get('ADMIN_PASSWORD', 'admin')
            
            if password == admin_pass:
                session['admin_logged_in'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('admin_login.html', error='Falsches Passwort')
        
        return render_template('admin_login.html')
    
    @app.route('/admin/logout')
    def admin_logout():
        """Admin-Logout"""
        session.clear()
        return redirect(url_for('index'))
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        """Admin-Dashboard"""
        events = Event.query.all()
        registrations = Registration.query.all()
        
        return render_template(
            'admin_dashboard.html',
            events=events,
            registrations=registrations
        )
    
    @app.route('/admin/event/<int:event_id>')
    @admin_required
    def admin_event_details(event_id):
        """Admin-Details für Event"""
        event = Event.query.get_or_404(event_id)
        registrations = Registration.query.filter_by(event_id=event_id).all()
        workshops = Workshop.query.filter_by(event_id=event_id).all()
        
        summary = get_registration_summary(event)
        
        return render_template(
            'admin_event_details.html',
            event=event,
            registrations=registrations,
            workshops=workshops,
            summary=summary
        )
    
    @app.route('/admin/export-csv/<int:event_id>')
    @admin_required
    def export_csv(event_id):
        """CSV-Export"""
        registrations = Registration.query.filter_by(event_id=event_id).all()
        event = Event.query.get_or_404(event_id)
        
        csv_data = export_to_csv(registrations)
        
        return send_file(
            io.BytesIO(csv_data.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Anmeldungen_{event.name}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    @app.route('/admin/export-excel/<int:event_id>')
    @admin_required
    def export_excel(event_id):
        """Excel-Export"""
        registrations = Registration.query.filter_by(event_id=event_id).all()
        event = Event.query.get_or_404(event_id)
        
        excel_data = export_to_excel(registrations)
        
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'Anmeldungen_{event.name}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    
    @app.route('/admin/send-confirmations/<int:event_id>', methods=['POST'])
    @admin_required
    def send_confirmations(event_id):
        """Sendet Bestätigungen an alle Teilnehmer eines Events"""
        registrations = Registration.query.filter_by(event_id=event_id).all()
        success_count, total_count = EmailService.send_bulk_confirmations(registrations)
        
        return jsonify({
            'success': True,
            'message': f'{success_count} von {total_count} Bestätigungen versendet'
        })
    
    @app.route('/admin/create-event', methods=['GET', 'POST'])
    @admin_required
    def create_event():
        """Event erstellen"""
        if request.method == 'POST':
            try:
                event = Event(
                    name=request.form.get('name'),
                    description=request.form.get('description'),
                    date=datetime.fromisoformat(request.form.get('date')),
                    location=request.form.get('location'),
                    max_participants=int(request.form.get('max_participants', 100))
                )
                db.session.add(event)
                db.session.commit()
                
                return redirect(url_for('admin_event_details', event_id=event.id))
            except Exception as e:
                logger.error(f"Event-Erstellung fehlgeschlagen: {str(e)}")
        
        return render_template('create_event.html')
    
    @app.route('/admin/create-workshop/<int:event_id>', methods=['GET', 'POST'])
    @admin_required
    def create_workshop(event_id):
        """Workshop erstellen"""
        event = Event.query.get_or_404(event_id)
        
        if request.method == 'POST':
            try:
                workshop = Workshop(
                    event_id=event_id,
                    name=request.form.get('name'),
                    description=request.form.get('description'),
                    start_time=datetime.fromisoformat(request.form.get('start_time')),
                    end_time=datetime.fromisoformat(request.form.get('end_time')),
                    location=request.form.get('location'),
                    max_capacity=int(request.form.get('max_capacity'))
                )
                db.session.add(workshop)
                db.session.commit()
                
                return redirect(url_for('admin_event_details', event_id=event_id))
            except Exception as e:
                logger.error(f"Workshop-Erstellung fehlgeschlagen: {str(e)}")
        
        return render_template('create_workshop.html', event=event)
    
    return app

def _create_demo_data():
    """Erstellt Demo-Daten"""
    if Event.query.first() is None:
        # Demo-Event
        event = Event(
            name='BNE-Tag 2025',
            description='Bundeszentrale für Nachhaltige Entwicklung',
            date=datetime(2025, 5, 15, 9, 0),
            location='Berlin',
            max_participants=200
        )
        db.session.add(event)
        db.session.flush()
        
        # Demo-Workshops
        workshops = [
            Workshop(
                event_id=event.id,
                name='Nachhaltige Entwicklung I',
                description='Einführung in BNE',
                start_time=datetime(2025, 5, 15, 10, 0),
                end_time=datetime(2025, 5, 15, 11, 30),
                location='Raum A',
                max_capacity=30
            ),
            Workshop(
                event_id=event.id,
                name='Nachhaltige Entwicklung II',
                description='Praxisbeispiele',
                start_time=datetime(2025, 5, 15, 12, 0),
                end_time=datetime(2025, 5, 15, 13, 30),
                location='Raum B',
                max_capacity=25
            ),
            Workshop(
                event_id=event.id,
                name='Nachhaltige Entwicklung III',
                description='Umsetzung in der Praxis',
                start_time=datetime(2025, 5, 15, 14, 0),
                end_time=datetime(2025, 5, 15, 15, 30),
                location='Raum C',
                max_capacity=20
            ),
        ]
        
        for workshop in workshops:
            db.session.add(workshop)
        
        db.session.commit()

if __name__ == '__main__':
    import io
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
