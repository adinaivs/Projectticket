from django import template
from django.utils.html import format_html
from django.urls import reverse

register = template.Library()

@register.simple_tag
def render_button(row, number, color, status, task_pk, class_type_pk):
    """
    Генерирует кнопку для конкретного места.
    """
    btn_classes = "seat-btn available" if status != "sold" else "seat-btn sold"
    btn_disabled = "disabled" if status == "sold" else ""

    form_action = reverse('book_seat', args=[task_pk, class_type_pk])
    return format_html(
        f"""
        <form method="POST" action="{form_action}">
            {{% csrf_token %}}
            <button
                type="submit"
                name="seat"
                value="{number}"
                class="{btn_classes}"
                style="background-color: {color};"
                {btn_disabled}>
                {row}-{number}
            </button>
        </form>
        """
    )
