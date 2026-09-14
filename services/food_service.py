"""Tjänster för livsmedelsdata.

Den här filen ansvarar för databasoperationer kopplade till livsmedel,
som att hämta listor, slå upp livsmedel och skapa nya poster.
"""

from db import get_db


def get_all_foods():
    """Hämtar alla livsmedel från databasen, sorterade i bokstavsordning."""
    with get_db() as cur:
        cur.execute("SELECT * FROM food ORDER BY name")
        return cur.fetchall()


def get_food_id_by_name(name):
    """Hämtar food_id för ett livsmedel baserat på namn. Returnerar None om det inte finns."""
    with get_db() as cur:
        cur.execute("SELECT food_id FROM food WHERE name = %s", (name,))
        return cur.fetchone()


def add_food(name, calories, protein, fat, carbs):
    """Lägger till ett nytt livsmedel i databasen. Returnerar inget värde."""
    with get_db() as cur:
        cur.execute(
            "INSERT INTO food (name, calories, protein, fat, carbs) VALUES (%s, %s, %s, %s, %s)",
            (name, calories, protein, fat, carbs),
        )
