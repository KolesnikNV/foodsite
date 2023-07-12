from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    """
    Расширенная модель пользователя.
    """

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLES = (
        (USER, "Пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Администратор"),
    )
    email = models.EmailField(
        verbose_name="Адрес email",
        max_length=254,
        unique=True,
        blank=False,
        error_messages={
            "unique": "Пользователь с таким email уже существует!",
        },
        help_text="Укажите свой email",
    )
    username = models.CharField(
        verbose_name="Логин",
        max_length=150,
        unique=True,
        error_messages={
            "unique": "Пользователь с таким никнеймом уже существует!",
        },
        help_text="Укажите свой никнейм",
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        blank=True,
        help_text="Укажите своё имя",
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        blank=True,
        help_text="Укажите свою фамилию",
    )
    role = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=ROLES,
        default=ADMIN,
    )
    date_joined = models.DateTimeField(
        verbose_name="Дата регистрации",
        auto_now_add=True,
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=150,
        help_text="Введите пароль",
    )

    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.get_full_name()

    @property
    def is_moderator(self):
        """
        Проверяет, является ли пользователь модератором.
        """
        return self.is_staff or self.role == self.MODERATOR

    @property
    def is_admin(self):
        """
        Проверяет, является ли пользователь администратором.
        """
        return self.is_superuser or self.role == self.ADMIN


class Follow(models.Model):
    """
    Модель подписки на авторов рецептов.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор рецепта",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"),
                name="uq_user_follower",
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")),
                name="self_following",
            ),
        )

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
