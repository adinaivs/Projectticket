from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Token, ClassType, Task, TaskClassType, Comment

# Регистрируем модель пользователя
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')  # Поля для отображения в списке
    search_fields = ('email', 'first_name', 'last_name')  # Поля для поиска
    list_filter = ('is_staff', 'is_active')  # Фильтрация по полям
    readonly_fields = ('email', 'date_joined')  # Поля только для чтения
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'is_staff', 'is_active')}),
        (_('Important Dates'), {'fields': ('date_joined',)}),
    )  # Разделение полей по секциям

admin.site.register(CustomUser, CustomUserAdmin)


# Регистрируем модель типов классов
class ClassTypeAdmin(admin.ModelAdmin):
    model = ClassType
    list_display = ('name', 'created_at', 'updated_at')  # Поля для отображения в списке
    search_fields = ('name',)  # Поиск по названию
    readonly_fields = ('created_at', 'updated_at')  # Поля только для чтения
    list_filter = ('created_at',)  # Фильтрация по времени создания

admin.site.register(ClassType, ClassTypeAdmin)


# Регистрируем модель Task
class TaskClassTypeInline(admin.TabularInline):
    model = TaskClassType
    extra = 1  # Количество пустых строк для добавления

class TaskAdmin(admin.ModelAdmin):
    model = Task
    list_display = ('title', 'event_date', 'location', 'created_at', 'updated_at')  # Поля для отображения в списке
    search_fields = ('title', 'location')  # Поиск по названию и месту
    list_filter = ('event_date', 'location')  # Фильтрация по дате события и месту
    readonly_fields = ('created_at', 'updated_at')  # Поля только для чтения
    inlines = [TaskClassTypeInline]  # Встраиваем промежуточную модель для отображения в форме

admin.site.register(Task, TaskAdmin)


# Регистрируем модель TaskClassType
class TaskClassTypeAdmin(admin.ModelAdmin):
    model = TaskClassType
    list_display = ('task', 'class_type', 'price', 'available_seats')  # Поля для отображения в списке
    search_fields = ('task__title', 'class_type__name')  # Поиск по названию задачи и типа класса
    list_filter = ('price', 'available_seats')  # Фильтрация по цене и количеству мест
    readonly_fields = ('task', 'class_type')  # Поля только для чтения

admin.site.register(TaskClassType, TaskClassTypeAdmin)


# Регистрируем модель Comment
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('task', 'user', 'subject', 'is_published', 'created_at')  # Поля для отображения в списке
    search_fields = ('task__title', 'user__email', 'subject')  # Поиск по названию задачи, email пользователя и теме комментария
    list_filter = ('is_published', 'created_at')  # Фильтрация по статусу публикации и времени создания
    readonly_fields = ('created_at',)  # Поле только для чтения

admin.site.register(Comment, CommentAdmin)
