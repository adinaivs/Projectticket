from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.contrib.auth import get_user_model


class Seat(models.Model):
    row = models.CharField(max_length=1, choices=[(chr(i), chr(i)) for i in range(65, 91)])  # A-Z
    number = models.PositiveIntegerField()
    is_reserved = models.BooleanField(default=False)

    # Связь с TaskClassType
    task_class_type = models.ForeignKey('TaskClassType', related_name='seats', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.row}{self.number} ({self.task_class_type.class_type.name})"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Пользователь
class CustomUser(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(_("email address"), unique=True, )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"

class Token(models.Model):
    token = models.CharField(max_length=255, unique=True)  # Токен, который будет использоваться для подтверждения
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Ссылка на пользователя
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания токена
    expires_at = models.DateTimeField()  # Время, до которого токен действителен

    def __str__(self):
        return self.token


# Класс для типов мест (VIP, Стандарт и т.д.)
class ClassType(models.Model):
    name = models.CharField("Название класса", max_length=50)
    color = models.CharField("Цвет", max_length=7, default="#FFFFFF")  # HEX-код для цвета
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TaskClassType(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name="task_class_types")
    class_type = models.ForeignKey('ClassType', on_delete=models.CASCADE, related_name="class_type_tasks")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField("Доступные места")

    def __str__(self):
        return f"{self.task.title} - {self.class_type.name} ({self.price} руб., {self.available_seats} мест)"

    def create_seats(self):
        """Создание мест для данного типа класса и задачи"""
        for i in range(1, self.available_seats + 1):
            Seat.objects.create(
                task_class_type=self,
                row=self.class_type.name[0],  # Первая буква названия класса как ряд
                number=i,
            )


class Task(models.Model):
    title = models.CharField(verbose_name=_("Название мероприятия"), max_length=255, null=True, blank=True)
    task = models.TextField('Описание')
    event_date = models.DateTimeField('Дата и время проведения')
    location = models.CharField('Место проведения', max_length=100)
    image = models.ImageField('Изображение', upload_to='events/images/', null=True, blank=True)

    # Связь через промежуточную модель
    class_types = models.ManyToManyField(ClassType, through=TaskClassType)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    task = models.ForeignKey('Task', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, verbose_name="Тема комментария")
    message = models.TextField(verbose_name="Сообщение")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self):
        return f"Комментарий от {self.user.email} на {self.task.title}"
