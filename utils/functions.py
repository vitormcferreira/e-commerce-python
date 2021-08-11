from datetime import date
from typing import Mapping

from django.forms import ValidationError


def formata_dinheiro(v):
    """ Formata string, int ou float para dinheiro no formato R$ 1.000,00 """
    try:
        v = float(v)
    except:
        return 'ERRO'
    return f'R$ {v:,.2f}'.replace(',', 'a').replace('.', ',').replace('a', '.')


def valida_cpf(cpf):
    import re
    cpf = str(cpf)
    cpf = re.sub(r'[^0-9]', '', cpf)

    if not cpf or len(cpf) != 11:
        return False

    # Elimina os dois últimos digitos do CPF
    novo_cpf = cpf[:-2]
    reverso = 10                        # Contador reverso
    total = 0

    # Loop do CPF
    for index in range(19):
        if index > 8:                   # Primeiro índice vai de 0 a 9,
            index -= 9                  # São os 9 primeiros digitos do CPF

        total += int(novo_cpf[index]) * reverso  # Valor total da multiplicação

        reverso -= 1                    # Decrementa o contador reverso
        if reverso < 2:
            reverso = 11
            d = 11 - (total % 11)

            if d > 9:                   # Se o digito for > que 9 o valor é 0
                d = 0
            total = 0                   # Zera o total
            novo_cpf += str(d)          # Concatena o digito gerado no novo cpf

    # Evita sequencias. Ex.: 11111111111, 00000000000...
    sequencia = novo_cpf == str(novo_cpf[0]) * len(cpf)

    # Descobri que sequências avaliavam como verdadeiro, então também
    # adicionei essa checagem aqui
    if cpf == novo_cpf and not sequencia:
        return True
    else:
        return False


def qtd_total_carrinho(carrinho):
    """Soma a quantidade de itens no carrinho"""
    return sum([x['quantidade'] for x in carrinho.values()])


def calcula_total_carrinho(carrinho):
    soma = 0
    for prod in carrinho.values():
        if prod['preco_quantitativo_promocional']:
            soma += prod['preco_quantitativo_promocional']
        else:
            soma += prod['preco_quantitativo']
    return soma


def normalize_error_list(error_list: list[Mapping[str, str]]):
    erros = {}
    for errs in error_list:
        for err in errs.items():
            field, msg = err

            if not hasattr(erros, field):
                erros[field] = []
            erros[field].append(ValidationError(msg))
    return erros


def get_idade(dnasc: date):
    try:
        dnasc = date(dnasc)
    except:
        return ''

    hoje = date.today()
    diff = hoje - dnasc

    idade = date.fromordinal(diff.days).year - 1

    return idade
