# MacroPW

En webbaserad applikation för kost- och träningsloggning, byggd med Flask, Bootstrap och PostgreSQL.

## Innehåll

- [Funktioner](#funktioner)
- [Teknikstack](#teknikstack)
- [Förutsättningar](#förutsättningar)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Starta applikationen](#starta-applikationen)
- [Testanvändare](#testanvändare)
- [Projektstruktur](#projektstruktur)


## Funktioner

- Registrering och inloggning av användare
- Loggning av måltider med kalori- och makroberäkning
- Hantering av livsmedel
- Skapande och redigering av sparade måltider
- Träningsloggning
- Statistiksida med daglig och veckovis översikt
- Personligt kalorimål beräknat utifrån användarprofil

## Teknikstack

| Kategori       | Teknik                              |
|----------------|-------------------------------------|
| Backend        | Python 3, Flask                     |
| Databas        | PostgreSQL, psycopg2                |
| Frontend       | Jinja2, Bootstrap, CSS, JavaScript  |

## Förutsättningar

- Python 3.x
- En körande PostgreSQL-instans med projektets databas

## Installation

1. Klona repot:
   ```bash
   git clone https://github.com/Lindbergviktor/MacroPW.git
   cd MacroPW
   ```

2. Installera beroenden:
   ```bash
   pip install flask psycopg2-binary
   ```

## Konfiguration

Applikationen ansluter till databasen via filen `config.ini`. De korrekta värdena tillhandahålls separat.

Fyll i rätt värden i `config.ini.example` i mappen (samma mapp som `app.py`).

Ändra namnet till `config.ini` innan du startar applikationen.

> **OBS:** `config.ini` är listad i `.gitignore` och ska aldrig checkas in i versionshanteringen eftersom den innehåller känsliga uppgifter.

## Starta applikationen

```bash
python app.py
```

Öppna sedan webbläsaren och gå till: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Testanvändare

För att testa applikationen utan att registrera ett nytt konto:

| Fält     | Värde           |
|----------|-----------------|
| E-post   | demo1@mail.com  |
| Lösenord | Test1234        |

## Projektstruktur

```
├── app.py                    # Applikationens entry point
├── db.py                     # Databasanslutning
├── nutrition.py              # Beräkningar för kalorimål och ålder
├── config.ini                # Databasuppgifter (ingår ej i repo)
├── config.ini.example        # Mall för konfiguration
├── routes/                   # Flask Blueprints – en fil per funktionsområde
│   ├── auth.py               # Inloggning och registrering
│   ├── dashboard.py          # Dashboard/startsida för inloggad användare
│   ├── foods.py              # Livsmedelshantering
│   ├── meals.py              # Måltidsloggning
│   ├── profile.py            # Användarprofil och inställningar
│   ├── statistics.py         # Statistik och diagram
│   └── workouts.py           # Träningsloggning
├── services/                 # Affärslogik separerad från routes
│   ├── dashboard_service.py
│   ├── food_service.py
│   ├── meal_service.py
│   ├── statistics_service.py
│   ├── user_service.py
│   └── workout_service.py
├── static/
│   ├── style.css             # Global stilsättning
│   ├── common.js             # Delad JavaScript-logik
│   ├── dashboard.js
│   ├── meals.js
│   ├── statistics.js
│   └── images/               # Bilder (logga, bakgrund m.m.)
└── templates/                # Jinja2-mallar (HTML)
    ├── index.html            # Dashboard
    ├── start_page.html       # Landningssida (ej inloggad)
    ├── login.html
    ├── register.html
    ├── profile.html
    ├── meals.html
    ├── edit_meal.html
    ├── foods.html
    ├── statistics.html
    └── add_workout.html
```
