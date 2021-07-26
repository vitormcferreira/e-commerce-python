from django.template import Library
from utils import functions


register = Library()


@register.filter
def formata_dinheiro(val):
    return functions.formata_dinheiro(val)
