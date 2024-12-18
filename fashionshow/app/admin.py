from django.contrib import admin
from .models import CustomUser, Task, ClassType, TaskClassType, Comment

admin.site.site_header = 'Fashion Show Admin Panel'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'task', 'is_published', 'created_at')  # Поля, отображаемые в списке
    list_filter = ('is_published', 'created_at')  # Фильтры в правой части страницы
    search_fields = ('subject', 'user_email', 'task_title')  # Поля для поиска
    list_per_page = 10  # Количество записей на странице

# Регистрируем модель CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('username', 'email')
    list_per_page = 10

# Регистрируем модель TaskClassType
@admin.register(TaskClassType)
class TaskClassTypeAdmin(admin.ModelAdmin):
    list_display = ('task', 'class_type', 'price')

# Регистрируем модель ClassType
admin.site.register(ClassType)

# Встраиваем модель TaskClassType в админку Task
class TaskClassTypeInline(admin.TabularInline):
    model = TaskClassType
    extra = 1  # Количество пустых строк для добавления новых записей
    fields = ('class_type', 'price', 'available_seats')  # Поля, которые будут отображаться
    min_num = 1  # Минимальное количество записей (опционально)

# Регистрируем модель Task
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'event_date', 'location', 'get_class_type')
    inlines = [TaskClassTypeInline]  # Добавляем Inline
    list_per_page = 10

    def get_class_type(self, obj):
        """
        Возвращает информацию о классах, ценах и количестве мест для мероприятия.
        """
        return ", ".join(
            [
                f"{ct.class_type.name} (Цена: {ct.price}, Места: {ct.available_seats})"
                for ct in obj.task_class_types.all()
            ]
        )

    get_class_type.short_description = "Классы"
