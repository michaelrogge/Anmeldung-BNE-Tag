# 🚀 Quick Start Guide

Schnelle Anleitung zum Starten des Anmeldesystems in 5 Minuten.

## 1️⃣ Vorbereitung

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

## 2️⃣ Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

## 3️⃣ .env Datei erstellen

```bash
# Kopieren Sie die Vorlage
cp .env.example .env

# OPTIONAL: Email konfigurieren (Gmail)
# Fügen Sie Ihre Daten ein:
# MAIL_USERNAME=ihre-email@gmail.com
# MAIL_PASSWORD=ihr-16-stelliges-app-passwort
```

## 4️⃣ Anwendung starten

```bash
python app.py
```

Öffnen Sie dann: **http://localhost:5000**

## 5️⃣ Admin-Bereich

- **Login-URL**: http://localhost:5000/admin/login
- **Standard-Passwort**: `admin`

> ⚠️ **IMPORTANT**: Ändern Sie das Passwort in `.env` für Production!

## 📝 Demo-Daten

Die Demo-Veranstaltung wird automatisch erstellt:
- **Name**: BNE-Tag 2025
- **Datum**: 15.05.2025, 09:00
- **Workshops**: 3 vorvorkonfigurierte Workshops

## 🔧 Häufige Aufgaben

### Neue Veranstaltung erstellen
1. Admin-Bereich öffnen
2. "Neue Veranstaltung" klicken
3. Details eingeben
4. Speichern → Workshops hinzufügen

### Datenbank zurücksetzen
```bash
rm event_registration.db
python app.py  # Neu starten
```

### Mit PostgreSQL arbeiten
```bash
# .env aktualisieren:
DATABASE_URL=postgresql://user:password@localhost:5432/registration

# psycopg2 installieren
pip install psycopg2-binary
```

### Production mit Gunicorn
```bash
# FLASK_ENV=production in .env setzen
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## 🐳 Mit Docker starten

```bash
# Alle Services starten
docker-compose up -d

# Anwendung ist verfügbar unter: http://localhost:5000
```

## ❓ Häufige Fragen

**F: Warum werden Emails nicht versendet?**
A: Überprüfen Sie `.env` und die SMTP-Einstellungen. Gmail erfordert spezifische App-Passwörter.

**F: Kann ich verschiedene Admin-Passwörter setzen?**
A: Ja, bearbeiten Sie `config.py` und nutzen Sie `generate_password_hash()`.

**F: Wie viele Teilnehmer kann das System handhaben?**
A: Mit SQLite bis ~50.000 Einträge. Verwenden Sie PostgreSQL für mehr.

**F: Kann ich das Design anpassen?**
A: Ja! Bearbeiten Sie die CSS in `templates/base.html`.

---

**Benötigen Sie Hilfe?** Schauen Sie sich die vollständige [README.md](README.md) an!
