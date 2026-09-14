"""Startpunkt för Flask-applikationen.

Den här filens ansvar är att skapa Flask-appen, ladda grundläggande
konfiguration och registrera alla blueprints som tillsammans bygger upp
applikationens webbroutes.
"""

from flask import Flask

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.foods import foods_bp
from routes.meals import meals_bp
from routes.profile import profile_bp
from routes.statistics import statistics_bp
from routes.workouts import workouts_bp


app = Flask(__name__)
app.secret_key = "secret_key"

app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(foods_bp)
app.register_blueprint(meals_bp)
app.register_blueprint(workouts_bp)
app.register_blueprint(statistics_bp)


if __name__ == "__main__":
    app.run(debug=True)
