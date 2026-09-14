"""Tjänster för måltider och måltidsloggar.

Den här filen ansvarar för databaslogik kring sparade måltider,
ingredienser och loggning av måltider i användarens dagliga historik.
"""

from db import get_db


def get_meals_dict(user_id):
    """Tar fram en dict på måltider med ingredienser och makrovärden."""
    with get_db() as cur:
        cur.execute(
            """
            SELECT m.meal_id, m.name, f.name, mi.amount,
                   f.calories, f.protein, f.fat, f.carbs
                   FROM meal m
                   JOIN meal_ingredient mi ON m.meal_id = mi.meal_id
                   JOIN food f ON mi.food_id = f.food_id
                   WHERE m.user_id = %s
                   ORDER BY m.meal_id
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    meals_dict = {}
    for meal_id, meal_name, food_name, amount, cal, prot, fat, carbs in rows:
        if meal_id not in meals_dict:
            meals_dict[meal_id] = {
                "name": meal_name,
                "meal_id": meal_id,
                "ingredients": [],
                "total_calories": 0,
                "total_protein": 0,
                "total_fat": 0,
                "total_carbs": 0,
            }
        meals_dict[meal_id]["ingredients"].append({"food": food_name, "amount": amount})
        meals_dict[meal_id]["total_calories"] += cal * amount / 100
        meals_dict[meal_id]["total_protein"] += prot * amount / 100
        meals_dict[meal_id]["total_fat"] += fat * amount / 100
        meals_dict[meal_id]["total_carbs"] += carbs * amount / 100

    return list(meals_dict.values())


def create_meal(name, user_id):
    with get_db() as cur:
        cur.execute(
            "INSERT INTO meal (name, user_id) VALUES (%s, %s) RETURNING meal_id",
            (name, user_id),
        )
        return cur.fetchone()[0]


def add_meal_ingredient(meal_id, food_id, amount):
    """Skapar en måltidsmall med ingredienser i en transaktion. Returnerar meal_id."""
    with get_db() as cur:
        cur.execute(
            "INSERT INTO meal_ingredient (meal_id, food_id, amount) VALUES (%s, %s, %s)",
            (meal_id, food_id, amount),
        )


def create_meal_with_ingredients(name, user_id, ingredients):
    with get_db() as cur:
        cur.execute(
            "INSERT INTO meal (name, user_id) VALUES (%s, %s) RETURNING meal_id",
            (name, user_id),
        )
        meal_id = cur.fetchone()[0]
        for food_id, amount in ingredients:
            cur.execute(
                "INSERT INTO meal_ingredient (meal_id, food_id, amount) VALUES (%s, %s, %s)",
                (meal_id, food_id, amount),
            )
        return meal_id


def get_meal_owner(meal_id):
    """Returnerar user_id för ägaren till en måltidsmall. Används för behörighetskontroll."""
    with get_db() as cur:
        cur.execute("SELECT user_id FROM meal WHERE meal_id = %s", (meal_id,))
        return cur.fetchone()


def get_meal_name(meal_id, user_id=None):
    """Hämtar namnet på en måltidsmall. Om user_id anges kontrolleras även ägarskap."""
    with get_db() as cur:
        if user_id is None:
            cur.execute("SELECT name FROM meal WHERE meal_id = %s", (meal_id,))
        else:
            cur.execute(
                "SELECT name FROM meal WHERE meal_id = %s AND user_id = %s",
                (meal_id, user_id),
            )
        return cur.fetchone()


def get_meal_ingredients(meal_id):
    """Hämtar ingredienser med livsmedelsnamn som lista av (food_id, namn, amount)."""
    """Hämtar ingredienser för en måltidsmall som lista av (food_id, amount)."""
    with get_db() as cur:
        cur.execute("SELECT food_id, amount FROM meal_ingredient WHERE meal_id = %s", (meal_id,))
        return cur.fetchall()


def get_meal_ingredients_detailed(meal_id):
    with get_db() as cur:
        cur.execute(
            """
            SELECT mi.food_id, f.name, mi.amount
            FROM meal_ingredient mi
            JOIN food f ON mi.food_id = f.food_id
            WHERE mi.meal_id = %s
        """,
            (meal_id,),
        )
        return cur.fetchall()


def delete_meal_with_dependencies(meal_id):
    """Tar bort en måltidsmall med alla beroenden.

    Sätter meal_id till NULL i meal_log, tar sedan bort ingredienser
    och slutligen mallen själv.
    """
    with get_db() as cur:
        cur.execute("UPDATE meal_log SET meal_id = NULL WHERE meal_id = %s", (meal_id,))
        cur.execute("DELETE FROM meal_ingredient WHERE meal_id = %s", (meal_id,))
        cur.execute("DELETE FROM meal WHERE meal_id = %s", (meal_id,))


def update_meal_name_and_ingredients(meal_id, name, ingredients):
    """Uppdaterar namn och ingredienser för en måltidsmall.

    Ersätter alla ingredienser med DELETE följt av INSERT för att
    slippa jämföra skillnader rad för rad.
    """
    with get_db() as cur:
        cur.execute("UPDATE meal SET name = %s WHERE meal_id = %s", (name, meal_id))
        cur.execute("DELETE FROM meal_ingredient WHERE meal_id = %s", (meal_id,))
        for food_id, amount in ingredients:
            cur.execute(
                "INSERT INTO meal_ingredient (meal_id, food_id, amount) VALUES (%s, %s, %s)",
                (meal_id, food_id, amount),
            )


def create_logged_meal(category, meal_id, user_id):
    """Skapar en måltidslogg utan maträtter. Returnerar log_id."""
    with get_db() as cur:
        cur.execute(
            "INSERT INTO meal_log (name, meal_id, user_id) VALUES (%s, %s, %s) RETURNING log_id",
            (category, meal_id, user_id),
        )
        return cur.fetchone()[0]


def create_logged_meal_with_items(category, meal_id, user_id, items):
    """Skapar en måltidslogg med maträtter i en transaktion. Returnerar log_id."""
    with get_db() as cur:
        cur.execute(
            "INSERT INTO meal_log (name, meal_id, user_id) VALUES (%s, %s, %s) RETURNING log_id",
            (category, meal_id, user_id),
        )
        log_id = cur.fetchone()[0]
        for food_id, amount in items:
            cur.execute(
                "INSERT INTO meal_log_item (log_id, food_id, amount) VALUES (%s, %s, %s)",
                (log_id, food_id, amount),
            )
        return log_id


def add_logged_meal_items(log_id, items):
    with get_db() as cur:
        for food_id, amount in items:
            cur.execute(
                "INSERT INTO meal_log_item (log_id, food_id, amount) VALUES (%s, %s, %s)",
                (log_id, food_id, amount),
            )


def log_meal_with_optional_items(category, meal_id, user_id, items):
    """Loggar en måltid och lägger till maträtter från två källor.

    Om meal_id anges kopieras ingredienser från mallen. Därefter läggs
    eventuella extra items till. Returnerar log_id.
    """
    with get_db() as cur:
        cur.execute(
            "INSERT INTO meal_log (name, meal_id, user_id) VALUES (%s, %s, %s) RETURNING log_id",
            (category, meal_id, user_id),
        )
        log_id = cur.fetchone()[0]

        if meal_id:
            cur.execute("SELECT food_id, amount FROM meal_ingredient WHERE meal_id = %s", (meal_id,))
            for food_id, amount in cur.fetchall():
                cur.execute(
                    "INSERT INTO meal_log_item (log_id, food_id, amount) VALUES (%s, %s, %s)",
                    (log_id, food_id, amount),
                )

        for food_id, amount in items:
            cur.execute(
                "INSERT INTO meal_log_item (log_id, food_id, amount) VALUES (%s, %s, %s)",
                (log_id, food_id, amount),
            )

        return log_id


def log_saved_meal(meal_id, meal_category, user_id):
    """Loggar en sparad måltidsmall och kopierar alla ingredienser till loggen. Returnerar log_id."""
    with get_db() as cur:
        cur.execute("INSERT INTO meal_log (name, meal_id, user_id) VALUES (%s, %s, %s) RETURNING log_id",
                    (meal_category, meal_id, user_id))
        log_id = cur.fetchone()[0]

        cur.execute("SELECT food_id, amount FROM meal_ingredient WHERE meal_id = %s", (meal_id,))
        ingredients = cur.fetchall()

        for food_id, amount in ingredients:
            cur.execute(
                "INSERT INTO meal_log_item (log_id, food_id, amount) VALUES (%s, %s, %s)",
                (log_id, food_id, amount),
            )

        return log_id


def copy_meal_ingredients_to_log(log_id, meal_id):
    """Kopierar ingredienser från en måltidsmall till en befintlig måltidslogg."""
    with get_db() as cur:
        cur.execute("SELECT food_id, amount FROM meal_ingredient WHERE meal_id = %s", (meal_id,))
        for food_id, amount in cur.fetchall():
            cur.execute(
                "INSERT INTO meal_log_item (log_id, food_id, amount) VALUES (%s, %s, %s)",
                (log_id, food_id, amount),
            )


def get_log_owner(log_id):
    """Returnerar user_id för ägaren till en måltidslogg. Används för behörighetskontroll."""
    with get_db() as cur:
        cur.execute("SELECT user_id FROM meal_log WHERE log_id = %s", (log_id,))
        return cur.fetchone()


def delete_log(log_id):
    """Tar bort en måltidslogg och alla tillhörande maträtter."""
    with get_db() as cur:
        cur.execute("DELETE FROM meal_log_item WHERE log_id = %s", (log_id,))
        cur.execute("DELETE FROM meal_log WHERE log_id = %s", (log_id,))


def delete_log_item(log_id, food_id):
    """Tar bort ett livsmedel från en måltidslogg."""
    with get_db() as cur:
        cur.execute(
            "DELETE FROM meal_log_item WHERE log_id = %s AND food_id = %s",
            (log_id, food_id),
        )


def update_log_item_amount(log_id, food_id, amount):
    """Uppdaterar mängden för ett livsmedel i en måltidslogg."""
    with get_db() as cur:
        cur.execute(
            "UPDATE meal_log_item SET amount = %s WHERE log_id = %s AND food_id = %s",
            (amount, log_id, food_id),
        )
