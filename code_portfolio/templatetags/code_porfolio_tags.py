# code_portfolio/templatetags/code_portfolio_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets a value from a dictionary using the key.
    Used in templates like: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key)

@register.filter
def skill_category_name(category_code):
    """
    Returns the human-readable name for a skill category code.
    """
    categories = {
        'LANGUAGE': 'Programming Languages',
        'FRAMEWORK': 'Frameworks & Libraries',
        'DATABASE': 'Databases',
        'TOOL': 'Tools & Practices',
        'CONCEPT': 'Concepts',
    }
    return categories.get(category_code, category_code)