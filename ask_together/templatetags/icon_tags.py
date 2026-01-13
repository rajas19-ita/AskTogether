from django import template
from django.templatetags.static import static

register = template.Library()

@register.inclusion_tag('ask_together/includes/_icon.html')
def icon(name, class_name=""):
    return {
        'name': name,
        'class_name': class_name,
        'sprite_url': static('ask_together/icons/sprite.svg')
    }