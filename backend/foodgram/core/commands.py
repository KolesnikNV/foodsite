import sqlite3

import pandas
import webcolors
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Команда управления Django для заполнения базы данных из предоставленных файлов.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = {
            "data/ingredients.csv": "food_ingredient",
            "data/tags.csv": "food_tags",
        }
        self.db_connection = sqlite3.connect(
            "/Users/nikitakolesnik/foodgram-project-react/backend/foodgram/db.sqlite3"
        )

    def handle(self, *args, **options):
        """
        Выполняет команду по заполнению базы данных.
        """
        self.clear_tags_with_color()
        self.populate_database()

    def clear_tags_with_color(self):
        """
        Очищает таблицу 'food_tags' от строк с цветами в формате HEX.
        """
        cursor = self.db_connection.cursor()
        sql_delete = "DELETE FROM food_tags WHERE color LIKE '%#%'"
        cursor.execute(sql_delete)
        self.db_connection.commit()

    def get_color_name(self, hex_code):
        """
        Возвращает название цвета, соответствующего заданному HEX коду.
        """
        rgb = webcolors.hex_to_rgb(hex_code)
        color = webcolors.rgb_to_name(rgb)
        return color

    def populate_database(self):
        """
        Заполняет таблицы базы данных данными из предоставленных файлов.
        """
        for path, name in self.db.items():
            try:
                df = pandas.read_csv(path, delimiter=",")
                if name == "food_tags":
                    df["color"] = df["color"].apply(self.get_color_name)

                df.to_sql(
                    name,
                    self.db_connection,
                    if_exists="append",
                    index=False,
                )
                print(f"Данные успешно добавлены в таблицу {name}")
            except Exception as e:
                print(f"Ошибка при добавлении данных в таблицу {name}: {e}")

    def remove_duplicates(self):
        """
        Удаляет дублирующиеся строки из таблицы 'food_ingredient' на основе столбца 'name'.
        Сохраняет строку с минимальным значением 'id' для каждого дублирующегося имени.
        """
        cursor = self.db_connection.cursor()
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

        self.db_connection.commit()

    def __del__(self):
        self.db_connection.close()


if __name__ == "__main__":
    command = Command()
    command.handle()
    command.remove_duplicates()
