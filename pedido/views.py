from django.contrib import messages
from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from produto.models import Variacao
from produto.views import CarrinhoMixin
from utils import functions
from utils.mixins import DispatchLoginRequiredMixin

from . import models


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagar.html'
    model = models.Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(usuario_id=self.request.user.perfil.pk)
        return qs


class ListaPedidos(DispatchLoginRequiredMixin, ListView):
    model = models.Pedido
    context_object_name = 'pedidos'
    paginate_by = 15
    template_name = 'pedido/listapedidos.html'
    ordering = '-id'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(usuario_id=self.request.user.perfil.pk)
        return qs


class SalvarPedido(DispatchLoginRequiredMixin, CarrinhoMixin, View):
    template_name = 'pedido/salvarpedido.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        if not self.get_carrinho():
            messages.error(request, 'Carrinho vazio.')
            return redirect('produto:listaprodutos')

        carrinho: dict = self.get_carrinho()
        carrinho_variacao_ids = list(carrinho.keys())

        bd_variacoes = list(
            Variacao.objects.filter(id__in=carrinho_variacao_ids)
        )

        for variacao in bd_variacoes:
            vid = str(variacao.id)
            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                messages.error(
                    request,
                    'Estoque insuficiente para alguns '
                    'produtos do seu carrinho. Reduzimos a '
                    'quantidade desses produtos. Por favor, '
                    'verifique quais produtos foram afetados'
                    ' a seguir.'
                )

        self.atualiza_precos_carrinho()
        self.salva_carrinho()

        qtd_total_carrinho = functions.qtd_total_carrinho(carrinho)
        valor_total_carrinho = functions.calcula_total_carrinho(carrinho)

        pedido = models.Pedido(
            usuario=request.user.perfil,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C',
        )
        pedido.save()

        models.ItemPedido.objects.bulk_create(
            [
                models.ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
            ]
        )

        del request.session['carrinho']
        # return render(request, self.template_name)
        return redirect(
            reverse('pedido:pagar', kwargs={'pk': pedido.pk})
        )


class Detalhe(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/detalhe.html'
    model = models.Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'
