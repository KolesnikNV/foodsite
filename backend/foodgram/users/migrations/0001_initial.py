# Generated by Django 4.2.3 on 2023-07-11 12:33

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        error_messages={
                            "unique": "Пользователь с таким email уже существует!"
                        },
                        help_text="Укажите свой email",
                        max_length=254,
                        unique=True,
                        verbose_name="Адрес email",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "Пользователь с таким никнеймом уже существует!"
                        },
                        help_text="Укажите свой никнейм",
                        max_length=150,
                        unique=True,
                        verbose_name="Логин",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True,
                        help_text="Укажите своё имя",
                        max_length=150,
                        verbose_name="Имя",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True,
                        help_text="Укажите свою фамилию",
                        max_length=150,
                        verbose_name="Фамилия",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("user", "user"),
                            ("admin", "admin"),
                            ("moderator", "moderator"),
                        ],
                        default="admin",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата регистрации"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        help_text="Введите пароль",
                        max_length=150,
                        verbose_name="Пароль",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
                "swappable": "AUTH_USER_MODEL",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Follow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="following",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор рецепта",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="follower",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Подписчик",
                    ),
                ),
            ],
            options={
                "verbose_name": "Подписка",
                "verbose_name_plural": "Подписки",
            },
        ),
        migrations.AddConstraint(
            model_name="follow",
            constraint=models.UniqueConstraint(
                fields=("user", "author"), name="uq_user_follower"
            ),
        ),
        migrations.AddConstraint(
            model_name="follow",
            constraint=models.CheckConstraint(
                check=models.Q(("user", models.F("author")), _negated=True),
                name="self_following",
            ),
        ),
    ]
