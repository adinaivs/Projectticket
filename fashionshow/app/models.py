from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.contrib.auth import get_user_model



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


# Тип класса
class ClassType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name


# Промежуточная модель для хранения цены и количества мест
class TaskClassType(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name="task_class_types")
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, related_name="class_type_tasks")
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, null=True, blank=True)
    available_seats = models.PositiveIntegerField(verbose_name=_("Доступные места"), null=True, blank=True)

    def __str__(self):
        return f"{self.task.title} - {self.class_type.name} ({self.price} руб., {self.available_seats} мест)"


# Модель мероприятия
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
