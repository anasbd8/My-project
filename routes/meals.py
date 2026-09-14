"""Blueprint för måltider och måltidsmallar.

Den här filen ansvarar för att visa, skapa, redigera, radera och logga
sparade måltider. Den kopplar ihop formulär och templates med tjänsterna
som hanterar databaslogiken.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.auth import login_required
from services.food_service import get_all_foods, get_food_id_by_name
from services.meal_service import (
    create_meal_with_ingredients,
    delete_meal_with_dependencies,
    get_meal_ingredients_detailed,
    get_meal_name,
    get_meal_owner,
    get_meals_dict,
    log_saved_meal,
    update_meal_name_and_ingredients,
)

meals_bp = Blueprint("meals", __name__)


@meals_bp.route("/meals")
@login_required
def meals():
    """Visar användarens måltider och tillgängliga livsmedel."""
    try:
        foods = get_all_foods()
        meals_dict = get_meals_dict(session["user_id"])
    except Exception:
        flash("Could not retrieve meals", "danger")
        return redirect(url_for("dashboard.index"))

    return render_template("meals.html", foods=foods, meals=meals_dict)


@meals_bp.route("/add_meal", methods=["POST"])
@login_required
def add_meal():
    """Skapar en måltid med valda ingredienser."""
    meal_name = request.form["meal_name"].strip().lower()
    food_names = request.form.getlist("food_name[]")
    amounts = request.form.getlist("amount[]")

    if not meal_name.strip():
        flash("Name cannot be empty", "danger")
        return redirect(url_for("meals.meals"))

    for amount in amounts:
        try:
            if float(amount) <= 0:
                flash("Amount must be greater than 0", "danger")
                return redirect(url_for("meals.meals"))
        except ValueError:
            flash("Amount must be a valid number.", "danger")
            return redirect(url_for("meals.meals"))

    try:
        ingredients = []
        for food_name, amount in zip(food_names, amounts):
            food = get_food_id_by_name(food_name.strip().lower())
            if not food:
                flash(f"Food '{food_name}' not found.", "danger")
                return redirect(url_for("meals.meals"))
            ingredients.append((food[0], amount))

        create_meal_with_ingredients(meal_name, session["user_id"], ingredients)
        flash("Meal added!", "success")
    except Exception:
        flash("Database error during creation of meal", "danger")
        return redirect(url_for("meals.meals"))

    return redirect(url_for("meals.meals"))


@meals_bp.route("/log_meal/<int:meal_id>", methods=["POST"])
@login_required
def log_meal(meal_id):
    """Loggar en sparad måltid för dagens datum."""
    try:
        meal = get_meal_name(meal_id)
        if not meal:
            flash("Meal could not be found", "danger")
            return redirect(url_for("meals.meals"))

        meal_category = request.form["meal_category"]
        log_saved_meal(meal_id, meal_category, session["user_id"])
    except Exception:
        flash("Database error during logging of meal.", "danger")
        return redirect(url_for("meals.meals"))

    flash("Meal registered!", "success")
    return redirect(url_for("dashboard.index"))


@meals_bp.route("/delete_meal/<int:meal_id>", methods=["POST"])
@login_required
def delete_meal(meal_id):
    """Tar bort en måltid"""
    try:
        meal = get_meal_owner(meal_id)
        if not meal or meal[0] != session["user_id"]:
            flash("Meal could not be found.", "danger")
            return redirect(url_for("meals.meals"))

        delete_meal_with_dependencies(meal_id)
    except Exception:
        flash("Database error during removal of meal.", "danger")
        return redirect(url_for("meals.meals"))

    flash("Meal deleted.", "success")
    return redirect(url_for("meals.meals"))


@meals_bp.route("/edit_meal/<int:meal_id>", methods=["GET", "POST"])
@login_required
def edit_meal(meal_id):
    """GET: visar redigeringsformulär. POST: sparar ändringar."""
    if request.method == "POST":
        meal_name = request.form["meal_name"].strip().lower()
        food_ids = request.form.getlist("food_id[]")
        amounts = request.form.getlist("amount[]")
        food_names = request.form.getlist("food_name[]")

        if not meal_name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("meals.edit_meal", meal_id=meal_id))

        for amount in amounts:
            try:
                if float(amount) <= 0:
                    flash("Amount must be greater than 0.", "danger")
                    return redirect(url_for("meals.edit_meal", meal_id=meal_id))
            except ValueError:
                flash("Amount must be a valid number.", "danger")
                return redirect(url_for("meals.edit_meal", meal_id=meal_id))

        try:
            meal = get_meal_owner(meal_id)
            if not meal or meal[0] != session["user_id"]:
                flash("Meal could not be found.", "danger")
                return redirect(url_for("meals.meals"))

            ingredients = [(food_id, amount) for food_id, amount in zip(food_ids, amounts)]
            extra_amounts = amounts[len(food_ids):]
            for food_name, amount in zip(food_names, extra_amounts):
                food = get_food_id_by_name(food_name.strip().lower())
                if not food:
                    flash(f"food '{food_name}' not found", "danger")
                    return redirect(url_for("meals.edit_meal", meal_id=meal_id))
                ingredients.append((food[0], amount))

            update_meal_name_and_ingredients(meal_id, meal_name, ingredients)
        except Exception:
            flash("Database error during updating meal.", "danger")
            return redirect(url_for("meals.edit_meal", meal_id=meal_id))

        flash("Meal updated!", "success")
        return redirect(url_for("meals.meals"))

    try:
        foods = get_all_foods()
        meal = get_meal_name(meal_id, session["user_id"])
        if not meal:
            flash("Meal could not be found.", "danger")
            return redirect(url_for("meals.meals"))

        ingredients = get_meal_ingredients_detailed(meal_id)
    except Exception:
        flash("Could not retrieve meal.", "danger")
        return redirect(url_for("meals.meals"))

    return render_template(
        "edit_meal.html",
        meal_id=meal_id,
        meal_name=meal[0],
        ingredients=ingredients,
        foods=foods,
    )
