"""Blueprint för autentisering och sessionsflöden.

Den här filen ansvarar för routes kring start, inloggning, registrering,
utloggning och kontoavslut, samt decoratorn som skyddar routes som kräver
att användaren är inloggad.
"""

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.user_service import create_user, get_user_for_login, email_exists

import re


auth_bp = Blueprint("auth", __name__)


def login_required(f):
    """Skyddar routes som kräver inloggning."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.start_page"))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/start")
def start_page():
    """Visar startsida för icke-inloggade användare."""
    return render_template("start_page.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = get_user_for_login(email, password)
        except Exception:
            flash("Database error in login.", "danger")
            return render_template("login.html")

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("dashboard.index"))

        flash("Wrong email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Hanterar registrering av användare."""
    if request.method == "GET":
        return render_template("register.html")
    
    form_data = request.form

    name = form_data.get("name", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "")
    confirm_password = form_data.get("confirm_password", "")
    gender = form_data.get("gender", "")
    height = form_data.get("height", "")
    weight = form_data.get("weight", "")
    activity_level = form_data.get("activity_level", "")
    birthdate = form_data.get("birthdate", "")
    weight_goal = form_data.get("weight_goal", "")

    def fail(message):
        return render_template("register.html", form_data=form_data, error=message)
    
    # Textfält
    if not name:
        return fail("Name cannot be empty.")
    if not email:
        return fail("Email cannot be empty.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return fail("Please enter a valid email address.")

    # Lösenord
    if not password:
        return fail("Password cannot be empty.")
    if len(password) < 8:
        return fail("Password must be at least 8 characters.")
    if not any(c.isupper() for c in password):
        return fail("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        return fail("Password must contain at least one number.")
    if password != confirm_password:
        return fail("Passwords do not match.")
    
    # Numeriska fält
    try:
        height_value = int(height)
        if height_value <= 0:
            return fail("Height must be a positive number.")
    except ValueError:
        return fail("Height must be a whole number.")

    try:
        weight_value = float(weight)
        if weight_value <= 0:
            return fail("Weight must be a positive number.")
    except ValueError:
        return fail("Weight must be a valid number.")

    # Obligatoriska val
    if not gender:
        return fail("Gender is required.")
    if not activity_level:
        return fail("Activity level is required.")
    if not birthdate:
        return fail("Date of birth is required.")
    if not weight_goal:
        return fail("Weight goal is required.")

    # Databasoperationer
    try:
        if email_exists(email):
            return fail("Email already registered.")
        create_user(name, email, password, gender, height_value, weight_value, activity_level, birthdate, weight_goal)
    except Exception:
        return fail("Database error during registration.")

    flash("Account created! You can now log in.", "success")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
