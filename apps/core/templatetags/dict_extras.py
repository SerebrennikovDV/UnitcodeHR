"""Шаблонные фильтры для работы со словарями и списками."""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return []
    return dictionary.get(key, []) if hasattr(dictionary, 'get') else []
