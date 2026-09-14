"""Tjänster för statistik och diagramunderlag.

Den här filen ansvarar för att hämta statistikdata från databasen och
omvandla den till strukturer som statistikvyn kan använda direkt, till
exempel veckosummeringar och dagliga diagramvärden.
"""

from datetime import date, timedelta

from db import get_db


def get_statistics_data(user_id):
    with get_db() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(ROUND(w.met * wl.weight * wl.duration / 60.0)), 0)
            FROM workout_log wl
            JOIN workout w ON wl.workout_id = w.workout_id
            WHERE wl.user_id = %s AND DATE(wl.log_date) = CURRENT_DATE
        """,
            (user_id,),
        )
        calories_burned_today = int(cur.fetchone()[0])

        cur.execute(
            """
            SELECT
                COALESCE(SUM(f.calories * mli.amount / 100.0), 0),
                COALESCE(SUM(f.protein  * mli.amount / 100.0), 0),
                COALESCE(SUM(f.fat      * mli.amount / 100.0), 0),
                COALESCE(SUM(f.carbs    * mli.amount / 100.0), 0)
            FROM meal_log ml
            JOIN meal_log_item mli ON ml.log_id = mli.log_id
            JOIN food f ON mli.food_id = f.food_id
            WHERE ml.user_id = %s AND DATE(ml.log_date) = CURRENT_DATE
        """,
            (user_id,),
        )
        nutrition_today = cur.fetchone()

        cur.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(wl.duration), 0),
                COALESCE(SUM(w.met * wl.weight * wl.duration / 60.0), 0)
            FROM workout_log wl
            JOIN workout w ON wl.workout_id = w.workout_id
            WHERE wl.user_id = %s
            AND wl.log_date >= date_trunc('week', CURRENT_DATE)
        """,
            (user_id,),
        )
        workouts_week = cur.fetchone()

        cur.execute(
            """
            SELECT COALESCE(SUM(nr_of_glasses), 0)
            FROM water_log
            WHERE user_id = %s AND DATE(log_date) = CURRENT_DATE
        """,
            (user_id,),
        )
        water_today = cur.fetchone()[0]

        cur.execute(
            """
            SELECT
                DATE(ml.log_date),
                COALESCE(SUM(f.calories * mli.amount / 100.0), 0),
                COALESCE(SUM(f.protein  * mli.amount / 100.0), 0),
                COALESCE(SUM(f.fat      * mli.amount / 100.0), 0),
                COALESCE(SUM(f.carbs    * mli.amount / 100.0), 0)
            FROM meal_log ml
            JOIN meal_log_item mli ON ml.log_id = mli.log_id
            JOIN food f ON mli.food_id = f.food_id
            WHERE ml.user_id = %s
              AND ml.log_date >= CURRENT_DATE - INTERVAL '6 days'
            GROUP BY DATE(ml.log_date)
            ORDER BY DATE(ml.log_date) DESC
        """,
            (user_id,),
        )
        nutrition_last_7 = cur.fetchall()

        cur.execute(
            """
            SELECT
                COALESCE(SUM(f.calories * mli.amount / 100.0), 0),
                COALESCE(SUM(f.protein  * mli.amount / 100.0), 0),
                COALESCE(SUM(f.fat      * mli.amount / 100.0), 0),
                COALESCE(SUM(f.carbs    * mli.amount / 100.0), 0)
            FROM meal_log ml
            JOIN meal_log_item mli ON ml.log_id = mli.log_id
            JOIN food f ON mli.food_id = f.food_id
            WHERE ml.user_id = %s
            AND ml.log_date >= CURRENT_DATE - INTERVAL '6 days'
        """,
            (user_id,),
        )
        nutrition_week = cur.fetchone()

    return {
        "calories_burned_today": calories_burned_today,
        "nutrition_today": nutrition_today,
        "workouts_week": workouts_week,
        "water_today": water_today,
        "nutrition_last_7": nutrition_last_7,
        "nutrition_week": nutrition_week,
    }


def build_calorie_chart_days(nutrition_last_7):
    """Bygger en komplett lista med 7 dagar bakåt för kalorigrafen.

    Dagar utan loggad data fylls med nollvärden så att grafen alltid
    visar alla sju dagar i rätt ordning.
    """
    nutrition_map = {
        row[0]: {
            "calories": round(row[1] or 0),
            "protein": round(row[2] or 0, 1),
            "fat": round(row[3] or 0, 1),
            "carbs": round(row[4] or 0, 1),
        }
        for row in nutrition_last_7
    }

    calorie_chart_days = []
    for offset in range(6, -1, -1):
        current_day = date.today() - timedelta(days=offset)
        day_stats = nutrition_map.get(
            current_day,
            {
                "calories": 0,
                "protein": 0,
                "fat": 0,
                "carbs": 0,
            },
        )
        calorie_chart_days.append(
            {
                "date": current_day,
                "label": current_day.strftime("%a"),
                "calories": day_stats["calories"],
                "protein": day_stats["protein"],
                "fat": day_stats["fat"],
                "carbs": day_stats["carbs"],
            }
        )

    return calorie_chart_days
