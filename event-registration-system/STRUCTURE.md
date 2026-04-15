# 📊 Projektstruktur

```
event-registration-system/
├── app.py                          # Flask-Hauptanwendung
├── models.py                       # SQLAlchemy Datenbank-Modelle
├── config.py                       # Konfigurationseinstellungen
├── utils.py                        # Hilfsfunktionen (Export, Validierung)
├── email_service.py                # Email-Versand Service
├── wsgi.py                         # WSGI Entry Point (Production)
├── requirements.txt                # Python Abhängigkeiten
├── Dockerfile                      # Docker Image Definition
├── docker-compose.yml              # Docker Compose Orchestration
├── .env.example                    # Umgebungsvariablen Vorlage
├── .gitignore                      # Git Ignore Datei
│
├── README.md                       # Ausführliche Dokumentation
├── QUICKSTART.md                   # Quick Start Guide
│
└── templates/                      # HTML Templates
    ├── base.html                   # Basis-Template mit Styling
    ├── index.html                  # Startseite
    ├── registration.html           # Anmeldeformular (Teilnehmer)
    ├── admin_login.html            # Admin-Login
    ├── admin_dashboard.html        # Admin-Übersicht
    ├── admin_event_details.html    # Admin-Event-Details
    ├── create_event.html           # Event erstellen (Admin)
    └── create_workshop.html        # Workshop erstellen (Admin)
```

## 📦 Kernkomponenten

### Backend (Flask)
- **app.py**: 13 Routen für Teilnehmer und Admin
- **models.py**: 5 SQLAlchemy Modelle (Event, Workshop, Participant, Registration, WorkshopRegistration)
- **email_service.py**: Asynchroner Email-Versand mit Threading
- **utils.py**: CSV/Excel Export, Validierung, QR-Code Generation

### Datenbank
- **SQLite** (Development) / **PostgreSQL** (Production)
- 5 normalisierte Tabellen
- Automatische Indizes auf häufig queried Spalten
- Cascade Delete für Datenbankintegrität

### Frontend
- **Responsive Design** mit CSS Grid/Flexbox
- **Live-Kapazitätsanzeige** pro Workshop
- **Formularvalidierung** (Client & Server)
- **Fehlerbehandlung** mit aussagekräftigen Messages

### Admin-Funktionen
- 🔐 Passwortgeschützter Zugang
- 📊 Statistik-Dashboard
- 📥 CSV & Excel Export
- 📧 Bulk Email-Versand
- ⚙️ Event & Workshop Management
