from django.contrib import admin
from .models import CustomUser, Task, ClassType, TaskClassType


admin.site.site_header = 'Fashion Show Admin Panel'
# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('username', 'email')
    list_per_page = 10


# admin.site.register(ClassType)
@admin.register(TaskClassType)
class TaskClassTypeAdmin(admin.ModelAdmin):
    list_display = ('task', 'class_type', 'price')

# admin.site.register(ClassType)
admin.site.register(ClassType)


class TaskClassTypeInline(admin.TabularInline):
    model = TaskClassType
    extra = 1  # Количество пустых строк для добавления новых записей
    fields = ('class_type', 'price', 'available_seats')  # Поля, которые будут отображаться
    min_num = 1  # Минимальное количество записей (опционально)

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
