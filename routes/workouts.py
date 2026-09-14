"""Blueprint för träningsloggning.

Den här filen ansvarar för träningssidan där användaren kan visa tillgängliga
övningar och spara träningspass med längd och datum.
"""

from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.auth import login_required
from services.workout_service import add_workout_log, get_workouts_for_user

workouts_bp = Blueprint("workouts", __name__)


@workouts_bp.route("/add_workout", methods=["GET", "POST"])
@login_required
def add_workout():
    """Lägger till ett loggat träningspass för användaren"""
    if request.method == "POST":
        workout_id = request.form.get("workout_id")
        duration = request.form.get("duration")
        log_date = request.form.get("log_date") or date.today().isoformat()

        if not workout_id:
            flash("Choose a workout.", "danger")
            return redirect(url_for("workouts.add_workout"))

        try:
            duration_val = float(duration)
        except (TypeError, ValueError):
            flash("Duration must be a valid number.", "danger")
            return redirect(url_for("workouts.add_workout"))

        if duration_val <= 0:
            flash("Duration must be greater than 0.", "danger")
            return redirect(url_for("workouts.add_workout"))

        try:
            add_workout_log(duration_val, session["user_id"], workout_id, log_date)
        except Exception:
            flash("Database error during saving workouts.", "danger")
            return redirect(url_for("workouts.add_workout"))

        flash("Workout saved.", "success")
        return redirect(url_for("workouts.add_workout"))

    try:
        workouts = get_workouts_for_user(session["user_id"])
    except Exception:
        flash("Could not retrieve workouts", "danger")
        return redirect(url_for("dashboard.index"))

    return render_template("add_workout.html", workouts=workouts, today=date.today().isoformat())
