# 📋 Veranstaltungsanmeldesystem

Ein webbasiertes, vollständiges Anmeldesystem für Veranstaltungen mit Workshop-Auswahl, Datenbankenverwaltung, Email-Versand und Admin-Panel.

## ✨ Features

### Für Teilnehmer
- ✅ Einfaches Anmeldeformular mit Validierung
- ✅ Workshop-Auswahl mit Live-Kapazitätsanzeige
- ✅ Automatische Teilnahmebestätigung per Email
- ✅ Responsive, benutzerfreundliche Oberfläche
- ✅ Unterstützung für besondere Wünsche (vegetarisch, glutenfrei, etc.)

### Für Administratoren
- 🔐 Passwortgeschütztes Admin-Dashboard
- 📊 Übersicht alle Anmeldungen und Workshops
- 📥 Export zu CSV und Excel
- 📧 Bulk-Email-Versand mit Bestätigungen
- ➕ Veranstaltungen und Workshops verwalten
- 📈 Echtzeit-Kapazitätsüberwachung

## 🛠️ Technologie-Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask 3.0
- **Datenbank**: SQLite (SQLAlchemy ORM)
- **Email**: SMTP (mit Unterstützung für Gmail, SendGrid, etc.)
- **Export**: CSV, Excel (OpenPyXL)

## 📦 Installation

### Schritt 1: Repository klonen
```bash
git clone <repository-url>
cd event-registration-system
```

### Schritt 2: Virtual Environment erstellen
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

### Schritt 3: Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### Schritt 4: Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env`-Datei im Projektverzeichnis basierend auf `.env.example`:

```bash
cp .env.example .env
```

Bearbeiten Sie `.env` mit Ihren Einstellungen:

```env
# Flask
SECRET_KEY=ein-sehr-sicherer-zufallsstring

# Datenbank
DATABASE_URL=sqlite:///event_registration.db

# Email-Einstellungen (Gmail-Beispiel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=ihre-email@gmail.com
MAIL_PASSWORD=ihr-app-spezifisches-passwort

# Admin-Passwort
ADMIN_PASSWORD=ihr-wunsch-passwort
```

### Email-Konfiguration für Gmail

1. Google-Konto mit **2FA** aktivieren
2. Gehen Sie zu: https://myaccount.google.com/apppasswords
3. Wählen Sie "Mail" und "Windows-Computer"
4. Kopieren Sie das generierte 16-stellige Passwort in `MAIL_PASSWORD`

Alternativ können Sie jeden SMTP-Server verwenden (Outlook, Sendgrid, etc.).

### Schritt 5: Datenbank initialisieren

```bash
python app.py
```

Die Datenbank wird automatisch mit Demo-Daten erstellt.

## 🚀 Starten der Anwendung

### Entwicklungsmodus
```bash
python app.py
```

Die Anwendung läuft dann unter: `http://localhost:5000`

### Mit Gunicorn (Produktion)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## 📖 Benutzerhandbuch

### Teilnehmer-Bereich

1. **Startseite**: Verfügbare Veranstaltungen durchsuchen
2. **Anmeldung**: 
   - Persönliche Daten eingeben
   - Mindestens einen Workshop wählen
   - Besondere Wünsche eintragen (optional)
   - Anmeldung abschließen
3. **Bestätigung**: Sofortige Email mit allen Details

### Admin-Bereich

**Login**: http://localhost:5000/admin/login
- Standardpasswort: `admin` (in `.env` ändern!)

**Dashboard**:
- Alle Veranstaltungen überblicken
- Statistiken pro Event
- Teilnehmerlisten exportieren
- Bestätigungsmails versenden

**Veranstaltung erstellen**:
1. Admin → "Neue Veranstaltung"
2. Details eingeben (Name, Datum, Ort, Max. Teilnehmer)
3. Workshops hinzufügen (mit Kapazität und Zeitfenstern)

## 📊 API-Endpoints

### Öffentliche Endpoints
- `GET /` - Startseite
- `GET /event/<id>` - Anmeldeformular
- `POST /api/register` - Registrierung (JSON)
- `GET /api/workshop-status/<id>` - Workshop-Verfügbarkeit

### Admin-Endpoints (geschützt)
- `GET /admin` - Dashboard
- `GET /admin/event/<id>` - Event-Details
- `POST /admin/send-confirmations/<id>` - Bestätigungen versenden
- `GET /admin/export-csv/<id>` - CSV-Export
- `GET /admin/export-excel/<id>` - Excel-Export
- `POST /admin/create-event` - Event erstellen
- `POST /admin/create-workshop/<id>` - Workshop erstellen

## 🗄️ Datenbankschema

### Tabellen

**events**
- id, name, description, date, location, max_participants

**workshops**
- id, event_id, name, description, start_time, end_time, location, max_capacity, current_capacity

**participants**
- id, first_name, last_name, email, phone, organization, dietary_restrictions, registration_date

**registrations**
- id, participant_id, event_id, registration_date, status

**workshop_registrations**
- id, registration_id, workshop_id, participant_id, registration_date, status

## 🔒 Sicherheit

### Empfohlene Maßnahmen

1. **Production-Deploy**:
   ```bash
   # Nutzen Sie HTTPS
   # Setzen Sie DEBUG=False
   # Ändern Sie SECRET_KEY
   # Nutzen Sie starke Admin-Passwörter
   ```

2. **Passwort-Hashing**:
   ```python
   # Admin-Passwort in Production hashen
   from werkzeug.security import generate_password_hash
   hashed = generate_password_hash('passwort', method='pbkdf2:sha256')
   ```

3. **CSRF-Schutz**: Wird automatisch von Flask-WTF gehandhabt

4. **SQL-Injection**: SQLAlchemy ORM schützt automatisch

5. **Session-Sicherheit**:
   - `SESSION_COOKIE_SECURE=True` in Production
   - `SESSION_COOKIE_HTTPONLY=True`
   - `SESSION_COOKIE_SAMESITE='Strict'`

## 📧 Email-Vorlagen

Die Emails werden automatisch generiert und beinhalten:
- Bestätigungsmeldung
- Workshop-Liste mit Zeiten
- Veranstaltungsinformationen
- Kontaktinformationen

### Email-Anpassung

Bearbeiten Sie `email_service.py` → `send_confirmation_email()` für Custom-Vorlagen:

```python
html_content = """
<!-- Ihre Custom-HTML-Vorlage -->
"""
```

## 🚨 Troubleshooting

### Email wird nicht versendet
1. Überprüfen Sie `.env` Einstellungen
2. Gmail: Stellen Sie sicher, dass "Weniger sichere Apps" aktiviert ist
3. Firewall: Port 587 (TLS) oder 465 (SSL) muss offen sein
4. Logs prüfen: `python app.py` startet mit Debug-Output

### Workshop-Kapazität synchronisiert nicht
- Aktualisieren Sie die Browser-Seite
- Oder fügen Sie Auto-Refresh hinzu:
```javascript
setInterval(() => location.reload(), 5000);  // 5 Sekunden
```

### Datenbankfehler
```bash
# Datenbank zurücksetzen
rm event_registration.db
python app.py  # Neu initialisieren
```

## 🚀 Deployment

### Heroku-Deployment

```bash
# requirements.txt sollte bereits vorhanden sein
echo "web: gunicorn app:create_app()" > Procfile

# Heroku Config setzen
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<secure-random-key>
heroku config:set MAIL_USERNAME=<your-email>
heroku config:set MAIL_PASSWORD=<your-app-password>

# Deployen
git push heroku main
```

### Docker-Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
```

```bash
docker build -t registration-system .
docker run -p 8000:8000 -e FLASK_ENV=production registration-system
```

## 📈 Performance-Tipps

1. **Datenbank-Indexe**:
   ```python
   # Bereits implementiert für:
   # - participants.email
   # - workshop_registrations
   ```

2. **Caching**:
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

3. **Batch-Email-Versand**: Das System versendet Emails asynchron

## 🤝 Beitragen

Willkommen! Bitte erstellen Sie einen Pull Request für Verbesserungen.

## 📄 Lizenz

MIT License

## 📞 Support

Bei Fragen öffnen Sie bitte ein Issue im Repository.

---

**Viel Spaß mit Ihrem Anmeldesystem!** 🎉
