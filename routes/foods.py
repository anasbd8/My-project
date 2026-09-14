"""Blueprint för livsmedelshantering.

Den här filen ansvarar för att visa sparade livsmedel och ta emot nya
livsmedel från formulär i webbgränssnittet. Själva databasoperationerna
delegeras vidare till tjänstelagret.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from psycopg2 import errors

from routes.auth import login_required
from services.food_service import add_food as add_food_record, get_all_foods

foods_bp = Blueprint("foods", __name__)


@foods_bp.route("/foods")
@login_required
def foods():
    """Visar alla livsmedel i databasen."""
    try:
        foods_list = get_all_foods()
    except Exception:
        flash("Could not retrieve foods", "danger")
        return redirect(url_for("dashboard.index"))

    return render_template("foods.html", foods=foods_list)


@foods_bp.route("/add_food", methods=["POST"])
@login_required
def add_food():
    """Lägger till ett nytt livsmedel i databasen."""
    name = request.form["name"].strip().lower()
    calories = request.form["calories"]
    protein = request.form["protein"]
    fat = request.form["fat"]
    carbs = request.form["carbs"]

    if not name.strip():
        flash("Name cannot be empty", "danger")
        return redirect(url_for("foods.foods"))

    try:
        calories_val = int(calories)
        protein_val = float(protein)
        fat_val = float(fat)
        carbs_val = float(carbs)
    except ValueError:
        flash("Calories, protein, fat and carbs must be valid numbers.", "danger")
        return redirect(url_for("foods.foods"))

    if calories_val <= 0:
        flash("Calories must be greater than 0", "danger")
        return redirect(url_for("foods.foods"))

    for value in [protein_val, fat_val, carbs_val]:
        if value < 0:
            flash("Nutritional values cannot be negative", "danger")
            return redirect(url_for("foods.foods"))
    if protein_val + fat_val + carbs_val > 100:
        flash("Protein, fat and carbs cannot exceed 100g combined.", "danger")
        return redirect(url_for("foods.foods"))

    try:
        add_food_record(name, calories_val, protein_val, fat_val, carbs_val)
        flash("Food added!", "success")
    except errors.UniqueViolation:
        flash("A food with that name already exists.", "danger")
        return redirect(url_for("foods.foods"))
    except errors.NumericValueOutOfRange:
        flash("One or more values are too large.", "danger")
        return redirect(url_for("foods.foods"))
    except Exception:
        flash("Database error when adding food.", "danger")
        return redirect(url_for("foods.foods"))

    return redirect(url_for("foods.foods"))
