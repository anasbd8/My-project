"""Blueprint för användarprofilen.

Den här filen ansvarar för visning och uppdatering av användarens
profiluppgifter, såsom namn, kroppsdata, aktivitetsnivå och mål.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.auth import login_required
from services.user_service import (
    count_user_data,
    delete_user_account,
    get_user_profile_row,
    update_user_profile,
    verify_user_password,
)

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Profilsida för användaren med deras personliga information"""
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        gender = request.form["gender"]
        height = request.form["height"]
        weight = request.form["weight"]
        weight_goal = request.form["weight_goal"]
        activity_level = request.form["activity_level"]
        birthdate = request.form["birthdate"]

        try:
            height_value = int(height)
            if height_value <= 0 or height_value > 300:
                flash("Height must be between 1 and 300 cm.", "danger")
                return redirect(url_for("profile.profile"))
        except ValueError:
            flash("Height must be a whole number.", "danger")
            return redirect(url_for("profile.profile"))

        try:
            weight_value = float(weight)
            if weight_value <= 0 or weight_value > 999.9:
                flash("Weight must be between 1 and 999.9 kg.", "danger")
                return redirect(url_for("profile.profile"))
        except ValueError:
            flash("Weight must be a valid number.", "danger")
            return redirect(url_for("profile.profile"))

        update_user_profile(
            user_id,
            name,
            email,
            gender,
            height,
            weight,
            weight_goal,
            activity_level,
            birthdate,
        )

        flash("Profile updated!", "success")
        return redirect(url_for("profile.profile"))

    row, cols = get_user_profile_row(user_id)
    user = dict(zip(cols, row))
    data_counts = count_user_data(user_id)
    return render_template("profile.html", user=user, data_counts=data_counts)


@profile_bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    """Raderar användarens konto och all tillhörande data efter verifiering."""
    user_id = session["user_id"]
    password = request.form.get("password", "")
    confirmation = request.form.get("confirmation", "")

    if confirmation != "DELETE":
        flash("You must type DELETE to confirm account deletion.", "danger")
        return redirect(url_for("profile.profile"))

    if not verify_user_password(user_id, password):
        flash("Incorrect password. Account not deleted.", "danger")
        return redirect(url_for("profile.profile"))

    try:
        delete_user_account(user_id)
    except Exception:
        flash("An error occurred. Account was not deleted.", "danger")
        return redirect(url_for("profile.profile"))

    session.clear()
    flash("Your account and all associated data have been permanently deleted.", "success")
    return redirect(url_for("auth.start_page"))
