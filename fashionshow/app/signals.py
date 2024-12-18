from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TaskClassType

@receiver(post_save, sender=TaskClassType)
def create_seats_for_task_class_type(sender, instance, created, **kwargs):
    if created:
        # Создаем сиденья только при создании нового TaskClassType
        instance.create_seats()
