from utils.mixins import DispatchLoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from perfil.models import Endereco
from furl import furl
from django.utils.safestring import mark_safe
from django.db.models import Q

from . import models
from .exceptions import SemEstoqueError

# TODO
# [x] ListaProdutos
# [x] DetalheProduto
# [x] Carrinho
# [x] AdicionarAoCarrinho
# [x] RemoverDoCarrinho
# [x] ResumoDaCompra


class CarrinhoMixin:
    def get_carrinho(self):
        """Retorna o carrinho."""
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}

        return self.request.session['carrinho']

    def atualiza_precos_carrinho(self):
        """Atualiza os preços quantitativos do carrinho"""
        carrinho = self.get_carrinho()

        for linha in carrinho.values():
            # cálculos do preco total de cada produto
            linha['preco_quantitativo'] = \
                linha['preco_unitario'] * \
                linha['quantidade']
            linha['preco_quantitativo_promocional'] = \
                linha['preco_unitario_promocional'] * \
                linha['quantidade']

    def remover_produto_carrinho(self, variacao_id: str, quant: int = 1):
        carrinho = self.get_carrinho()

        if not carrinho:
            return
        if not carrinho.get(variacao_id):
            return

        quant = int(quant) if quant >= 0 else 0
        carrinho[variacao_id]['quantidade'] -= quant

        if carrinho[variacao_id]['quantidade'] <= 0:
            del carrinho[variacao_id]
        else:
            self.atualiza_precos_carrinho()

    def adicionar_produto_carrinho(self, variacao: models.Variacao, quant: int = 1):
        """Adiciona um novo produto ao carrinho e/ou seta a quantidade.

        Args:
            variacao (Variacao): objeto Variacao.
            quant (int): quantidade a ser adicionada (inteiro positivo).
        """
        variacao_id = str(variacao.id)
        carrinho = self.get_carrinho()

        quant = int(quant) if quant >= 0 else 0

        if variacao_id in carrinho:
            carrinho[variacao_id]['quantidade'] += quant
        else:
            produto = variacao.produto
            carrinho[variacao_id] = {
                'produto_id': produto.id,
                'produto_nome': produto.nome,
                'variacao_nome': variacao.nome,
                'variacao_id': variacao.id,
                'preco_unitario': variacao.preco,
                'preco_unitario_promocional': variacao.preco_promocional,
                'preco_quantitativo': 0,
                'preco_quantitativo_promocional': 0,
                'quantidade': quant,
                'slug': produto.slug,
                'imagem': produto.imagem.url if produto.imagem else None,
            }

        car_var = carrinho[variacao_id]

        # quantidade maior que estoque
        sem_estoque = False
        if variacao.estoque < car_var['quantidade']:
            car_var['quantidade'] = variacao.estoque
            if variacao.estoque == 0:
                del carrinho[variacao_id]
            sem_estoque = True

        self.atualiza_precos_carrinho()

        if sem_estoque:
            produto = variacao.produto
            raise SemEstoqueError(
                f'Estoque insuficiente para '
                f'{car_var["quantidade"]}x no produto '
                f'"{produto.nome} ({variacao.nome})". Adicionamos '
                f'{variacao.estoque}x ao seu carrinho.'
            )

    def salva_carrinho(self):
        self.request.session.save()


class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/listaprodutos.html'
    context_object_name = 'produtos'
    paginate_by = 1
    ordering = ['-id']

    def get_queryset(self):
        sql = '''
            SELECT *, MIN(variacao.preco) as preco FROM produto
                INNER JOIN variacao ON produto.id=variacao.produto_id
                GROUP BY variacao.produto_id ORDER BY variacao.produto_id DESC;
        '''
        produtos = models.Produto.objects.raw(sql)

        return produtos


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalheproduto.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        # TODO: Exibir "Sem estoque" na página do produto
        # qs = qs.annotate(
        #     existe_estoque=Count(
        #         Case(
        #             When(variacao__produto_id=F('pk'),
        #                  variacao__estoque__gt=0, then=F('variacao__estoque'))
        #         )
        #     )
        # )
        # print(qs.query)
        return qs


class Carrinho(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'produto/carrinho.html')


class AdicionarAoCarrinho(CarrinhoMixin, View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER', reverse('produto:listaprodutos'))
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(self.request, 'Produto não existe.')
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, pk=variacao_id)

        try:
            self.adicionar_produto_carrinho(variacao)
        except SemEstoqueError as err:
            messages.error(self.request, *err.args)
        else:
            car_var = self.get_carrinho()[variacao_id]
            messages.success(
                self.request,
                f'Produto {car_var["produto_nome"]} adicionado ao seu '
                f'carrinho. Possui {car_var["quantidade"]}x.'
            )

        self.salva_carrinho()

        return redirect(http_referer)


class RemoverDoCarrinho(CarrinhoMixin, View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER', reverse('produto:listaprodutos'))
        variacao_id = self.request.GET.get('vid')

        variacao = get_object_or_404(models.Variacao, pk=variacao_id)

        self.remover_produto_carrinho(variacao.pk)
        self.salva_carrinho()

        messages.success(
            self.request,
            f'Produto {variacao.produto.nome} removido do seu carrinho'
        )

        return redirect(http_referer)


class ResumoDaCompra(DispatchLoginRequiredMixin, CarrinhoMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        http_referer = request.META.get(
            'HTTP_REFERER', reverse('produto:resumodacompra'))

        if not self.get_carrinho():
            return redirect(reverse('produto:listaprodutos'))

        enderecos = Endereco.objects.filter(
            perfil_id=self.request.user.perfil.pk)
        usuario = self.request.user

        if not enderecos:
            messages.error(
                request,
                mark_safe(
                    'Sem endereços disponíveis. Cadastre um novo '
                    f'<a href="{reverse("perfil:registrarendereco")}">aqui</a>'
                    ' para finalizar a compra.'
                )
            )
            return redirect(http_referer)

        return render(self.request, 'produto/resumodacompra.html', {
            'enderecos': enderecos,
            'usuario': usuario,
        })


class Busca(ListaProdutos):
    model = models.Produto
    template_name = 'produto/busca.html'

    def get_queryset(self):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        
        self.request.session['termo'] = termo

        # Na nota diz:
        # "Dictionary params are not supported with the SQLite backend; with
        # this backend, you must pass parameters as a list."
        # https://docs.djangoproject.com/en/3.2/topics/db/sql/#passing-parameters-into-raw
        sql = '''
            SELECT *, MIN(variacao.preco) as preco FROM produto
                INNER JOIN variacao ON produto.id=variacao.produto_id
                WHERE 
                    (produto.nome LIKE %(t)s OR 
                    produto.descricao_curta LIKE %(t)s OR 
                    produto.descricao_longa LIKE %(t)s)
                GROUP BY variacao.produto_id 
                ORDER BY variacao.produto_id DESC;
        '''
        produtos = models.Produto.objects.raw(sql, params={'t': f'%{termo}%'})

        return produtos
