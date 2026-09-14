"""Blueprint för statistikvyn.

Den här filen ansvarar för att hämta och presentera sammanställd statistik
för kost, träning och mål, samt att skicka färdig data vidare till
statistiktemplaten.
"""

from flask import Blueprint, flash, redirect, render_template, session, url_for

from routes.auth import login_required
from services.statistics_service import build_calorie_chart_days, get_statistics_data
from services.user_service import get_calorie_goal

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/statistics")
@login_required
def statistics():
    """Statistik sida som visar en översikt för användaren."""
    user_id = session["user_id"]

    try:
        statistics_data = get_statistics_data(user_id)
        calorie_goal = get_calorie_goal(user_id) + statistics_data["calories_burned_today"]
        weekly_goal = calorie_goal * 7
    except Exception:
        flash("Could not retrieve statistics.", "danger")
        return redirect(url_for("dashboard.index"))

    calorie_chart_days = build_calorie_chart_days(statistics_data["nutrition_last_7"])
    calorie_chart_max = max(
        [day["calories"] for day in calorie_chart_days] + [round(calorie_goal or 0), 1]
    )

    return render_template(
        "statistics.html",
        calories_today=round(statistics_data["nutrition_today"][0] or 0),
        protein_today=round(statistics_data["nutrition_today"][1] or 0, 1),
        fat_today=round(statistics_data["nutrition_today"][2] or 0, 1),
        carbs_today=round(statistics_data["nutrition_today"][3] or 0, 1),
        workouts_this_week=statistics_data["workouts_week"][0] or 0,
        workout_minutes_this_week=round(statistics_data["workouts_week"][1] or 0),
        workout_calories_this_week=round(statistics_data["workouts_week"][2] or 0),
        water_today=statistics_data["water_today"] or 0,
        calorie_chart_days=calorie_chart_days,
        calorie_chart_max=calorie_chart_max,
        calories_week=round(statistics_data["nutrition_week"][0] or 0),
        protein_week=round(statistics_data["nutrition_week"][1] or 0, 1),
        fat_week=round(statistics_data["nutrition_week"][2] or 0, 1),
        carbs_week=round(statistics_data["nutrition_week"][3] or 0, 1),
        weekly_goal=weekly_goal,
        calorie_goal=calorie_goal,
    )
