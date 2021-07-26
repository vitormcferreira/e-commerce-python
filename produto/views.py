from django.db.models import Max, Min
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, F, When
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/listaprodutos.html'
    context_object_name = 'produtos'
    paginate_by = 10

    def get_queryset(self):
        # SELECT produto.id, produto.nome, produto.descricao_curta, produto.descricao_longa,
        #     produto.imagem, produto.slug, MIN(variacao.preco) as preco, variacao.preco_promocional as preco_promocional
        #     FROM produto INNER JOIN variacao ON produto.id=variacao.produto_id GROUP BY variacao.produto_id;
        sql = '''
        SELECT *, MIN(variacao.preco) as preco
            FROM produto INNER JOIN variacao ON produto.id=variacao.produto_id GROUP BY variacao.produto_id;
        '''
        produtos = models.Produto.objects.raw(sql)
        # produtos = models.Produto.objects.filter(
        #     variacao__produto_id=F('pk')
        # ).annotate(
        #     preco=Min('variacao__preco')
        # ).order_by('nome')
        # print(produtos.query)
        return produtos


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalheproduto.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('AdicionarAoCarrinho GET')


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('RemoverDoCarrinho GET')


class Carrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Carrinho GET')


class Finalizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finalizar GET')
