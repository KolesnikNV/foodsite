import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
from sqlalchemy import create_engine


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
        with connection.cursor() as cursor:
            sql_delete = "DELETE FROM food_tags WHERE color LIKE '%#%'"
            cursor.execute(sql_delete)

    def populate_database(self):
        db_url = "postgresql://postgres:postgres@localhost:5432/postgres"
        engine = create_engine(db_url)

        for path, name in self.db.items():
            try:
                df = pd.read_csv(path, delimiter=",")
                if name == "food_tags":
                    df["color"] = df["color"]

                df.to_sql(
                    name,
                    engine,
                    schema="public",
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
        with connection.cursor() as cursor:
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
                WHERE name = %s AND id != %s
                """
                cursor.execute(delete_query, (name, min_id))

    def __del__(self):
        connection.close()


if __name__ == "__main__":
    command = Command()
    command.handle()
    command.remove_duplicates()
