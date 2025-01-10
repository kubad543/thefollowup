from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    return lst[index]