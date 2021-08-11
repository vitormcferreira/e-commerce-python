from django.template import Library
from utils import functions

register = Library()


@register.filter
def formata_dinheiro(val):
    return functions.formata_dinheiro(val)


@register.filter
def qtd_total_carrinho(carrinho):
    return functions.qtd_total_carrinho(carrinho)


@register.filter
def calcula_total_carrinho(carrinho):
    return functions.calcula_total_carrinho(carrinho)


@register.filter
def get_idade(data):
    return functions.get_idade(data)
