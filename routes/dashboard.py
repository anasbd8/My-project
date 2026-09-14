"""Blueprint för startsidan och dagens loggning.

Den här filen ansvarar för dashboarden på `/`, inklusive visning av dagens
mat- och träningsdata samt routes för att logga, redigera och ta bort
dagliga måltidsloggar.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.auth import login_required
from services.dashboard_service import build_logged_by_category, get_dashboard_data
from services.food_service import get_all_foods
from services.meal_service import (
    delete_log as delete_logged_meal,
    delete_log_item as delete_logged_meal_item,
    get_log_owner,
    get_meals_dict,
    log_meal_with_optional_items,
    update_log_item_amount,
)
from services.user_service import get_macro_goals
from services.dashboard_service import build_logged_by_category, get_dashboard_data, get_water_today, set_water_today

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Startsida för användaren."""
    try:
        dashboard_data = get_dashboard_data(session["user_id"])
        meals = get_meals_dict(session["user_id"])
        foods = get_all_foods()
        workouts_today = dashboard_data["workouts_today"]
        calories_burned_today = sum(w[2] for w in workouts_today)
        macro_goals = get_macro_goals(session["user_id"], calories_burned_today)
        water_today = get_water_today(session["user_id"])
    except Exception:
        flash("Could not receive data.", "danger")
        return redirect(url_for("auth.start_page"))

    category_calories = {row[0]: round(row[1]) for row in dashboard_data["category_rows"]}
    logged_by_category = build_logged_by_category(dashboard_data["logged_items"])

    return render_template(
        "index.html",
        calories=round(dashboard_data["totals"][0]),
        protein=round(dashboard_data["totals"][1]),
        fat=round(dashboard_data["totals"][2]),
        carbs=round(dashboard_data["totals"][3]),
        category_calories=category_calories,
        foods=foods,
        meals=meals,
        workouts_today=workouts_today,
        macro_goals=macro_goals,
        logged_by_category=logged_by_category,
        water_today=water_today,
    )


@dashboard_bp.route("/log_meal_index", methods=["POST"])
@login_required
def log_meal_index():
    """Loggar måltid ifrån startsidan"""
    category = request.form["meal_category"]
    meal_id = request.form.get("meal_id") or None
    food_ids = request.form.getlist("food_id[]")
    amounts = request.form.getlist("amount[]")

    paired = list(zip(food_ids, amounts))

    for fid, amt in paired:
        if fid and not amt:
            flash("You selected a food but left the amount empty.", "danger")
            return redirect(url_for("dashboard.index"))
        if amt and not fid:
            flash("You entered an amount but did not select a food.", "danger")
            return redirect(url_for("dashboard.index"))

    food_list = [(fid, amt) for fid, amt in paired if fid and amt]

    if not meal_id and not food_list:
        flash("Please select a meal or a food with an amount.", "danger")
        return redirect(url_for("dashboard.index"))

    for _, amt in food_list:
        try:
            if float(amt) <= 0:
                flash("Amount must be greater than 0.", "danger")
                return redirect(url_for("dashboard.index"))
        except ValueError:
            flash("Amount must be a valid number.", "danger")
            return redirect(url_for("dashboard.index"))

    try:
        log_meal_with_optional_items(category, meal_id, session["user_id"], food_list)
    except Exception:
        flash("Database error.", "danger")
        return redirect(url_for("dashboard.index"))

    flash("Food logged successfully!", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/delete_log/<int:log_id>", methods=["POST"])
@login_required
def delete_log(log_id):
    """Tar bort en loggad måltid på startsidan från dagens datum."""
    try:
        log = get_log_owner(log_id)
        if not log or log[0] != session["user_id"]:
            flash("Could not find log entry.", "danger")
            return redirect(url_for("dashboard.index"))
        delete_logged_meal(log_id)
    except Exception:
        flash("Database error during deletion.", "danger")
        return redirect(url_for("dashboard.index"))

    flash("Removed.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/delete_log_item/<int:log_id>/<int:food_id>", methods=["POST"])
@login_required
def delete_log_item(log_id, food_id):
    """Tar bort EN enskild ingrediens från en loggad måltid."""
    try:
        log = get_log_owner(log_id)
        if not log or log[0] != session["user_id"]:
            flash("Could not find log entry.", "danger")
            return redirect(url_for("dashboard.index"))
        delete_logged_meal_item(log_id, food_id)
    except Exception:
        flash("Database error during deletion.", "danger")
        return redirect(url_for("dashboard.index"))

    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/edit_log_item/<int:log_id>/<int:food_id>", methods=["POST"])
@login_required
def edit_log_item(log_id, food_id):
    """Uppdaterar mängden på en enskild ingrediens i en loggad måltid."""
    amount = request.form.get("amount")
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            flash("Amount must be greater than 0.", "danger")
            return redirect(url_for("dashboard.index"))
    except (TypeError, ValueError):
        flash("Amount must be a valid number.")
        return redirect(url_for("dashboard.index"))

    try:
        log = get_log_owner(log_id)
        if not log or log[0] != session["user_id"]:
            flash("Could not find log entry.", "danger")
            return redirect(url_for("dashboard.index"))
        update_log_item_amount(log_id, food_id, amount_val)
    except Exception:
        flash("Database error during update.", "danger")
        return redirect(url_for("dashboard.index"))

    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/water", methods=["POST"])
@login_required
def update_water():
    """Uppdaterar vatten mängden för användaren"""
    glasses = request.form.get("glasses", type=int)
    if glasses is not None and glasses >= 0:
        set_water_today(session["user_id"], glasses)
    return "", 204