import logging
import pandas as pd

from django.core.management.base import BaseCommand

from food.models import Ingredient, Tag


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Команда управления Django для заполнения
    базы данных из предоставленных файлов.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = {
            "data/ingredients.csv": Ingredient,
            "data/tags.csv": Tag,
        }

    def handle(self, *args, **options):
        """
        Выполняет команду по заполнению базы данных.
        """
        self.populate_database()

    def populate_database(self):
        for path, model in self.db.items():
            try:
                df = pd.read_csv(path, delimiter=",")
                objects = [model(**row) for _, row in df.iterrows()]
                model.objects.bulk_create(objects)
            except Exception as e:
                logger.error(
                    f"Ошибка при добавлении данных из файла {path}: {e}"
                )


if __name__ == "__main__":
    command = Command()
    command.handle()
