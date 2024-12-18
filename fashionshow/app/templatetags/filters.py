from django import template

register = template.Library()

@register.filter
def filter(seats, class_type_pk):
    """
    Возвращает список мест, относящихся к определенному типу класса.
    """
    return [seat for seat in seats if seat.task_class_type.pk == class_type_pk]
