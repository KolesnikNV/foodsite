# Generated by Django 4.2.3 on 2023-07-11 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='media/images/', verbose_name='Изображение блюда'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
