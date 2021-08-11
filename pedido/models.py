from django.db import models
from perfil.models import Perfil


class Pedido(models.Model):
    class Meta:
        db_table = 'pedido'

    usuario = models.ForeignKey(
        verbose_name='Usuário', to=Perfil, on_delete=models.CASCADE)
    total = models.FloatField()
    qtd_total = models.PositiveIntegerField()
    status = models.CharField(
        default='C',
        max_length=1,
        choices=(
            ('A', 'Aprovado'),
            ('C', 'Criado'),
            ('R', 'Reprovado'),
            ('P', 'Pendente'),
            ('E', 'Enviado'),
            ('F', 'Finalizado')
        )
    )

    def __str__(self) -> str:
        return f'Pedido N. {self.pk}'


class ItemPedido(models.Model):
    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'

        db_table = 'itempedido'

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.CharField(max_length=255)
    produto_id = models.PositiveIntegerField()
    variacao = models.CharField('Variação', max_length=255)
    variacao_id = models.PositiveIntegerField('ID da Variação')
    preco = models.FloatField('Preço')
    preco_promocional = models.FloatField('Preço promocional', default=0)
    quantidade = models.PositiveIntegerField()
    imagem = models.CharField(max_length=2048)

    def __str__(self) -> str:
        return f'Item do {self.pedido}'
