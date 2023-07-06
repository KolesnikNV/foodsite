import sqlite3
import pandas
import webcolors
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Наполняет базу данных из предоставленных файлов."

    def handle(self, *args, **kwargs):
        db = {
            "data/ingredients.csv": "food_ingredient",
            "data/tags.csv": "food_tags",
        }
        conn = sqlite3.connect(
            "/Users/nikitakolesnik/foodgram-project-react/backend/foodgram/db.sqlite3"
        )
        cursor = conn.cursor()

        sql_delete = "DELETE FROM food_tags WHERE color LIKE '%#%'"
        cursor.execute(sql_delete)
        conn.commit()

        def get_color_name(hex_code):
            rgb = webcolors.hex_to_rgb(hex_code)
            color = webcolors.rgb_to_name(rgb)
            return color

        for path, name in db.items():
            try:
                df = pandas.read_csv(path, delimiter=",")
                conn = sqlite3.connect(
                    "/Users/nikitakolesnik/foodgram-project-react/backend/foodgram/db.sqlite3"
                )

                if name == "food_tags":
                    df["color"] = df["color"].apply(get_color_name)

                df.to_sql(
                    name,
                    conn,
                    if_exists="append",
                    index=False,
                )
                conn.commit()
                print(f"Данные успешно добавлены в таблицу {name}")
            except Exception as e:
                print(f"Ошибка при добавлении данных в таблицу {name}: {e}")

    def remove_duplicates(self):
        conn = sqlite3.connect(
            "/Users/nikitakolesnik/foodgram-project-react/backend/foodgram/db.sqlite3"
        )
        cursor = conn.cursor()

        select_query = """
        SELECT MIN(id) AS min_id, name, COUNT(*) AS count
        FROM food_ingredient
        GROUP BY name
        HAVING COUNT(*) > 1
        """
        cursor.execute(select_query)
        duplicate_rows = cursor.fetchall()

        for row in duplicate_rows:
            min_id, name, count = row
            delete_query = """
            DELETE FROM food_ingredient
            WHERE name = ? AND id != ?
            """
            cursor.execute(delete_query, (name, min_id))

        conn.commit()
        conn.close()

        conn.close()


if __name__ == "__main__":
    command = Command()
    command.handle()
    command.remove_duplicates()
