from typing import Union
from django.db import models
from PIL import Image
from django.utils.text import slugify
from utils.functions import formata_dinheiro


class Produto(models.Model):
    class Meta:
        db_table = 'produto'

    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField('Descrição curta', max_length=255)
    descricao_longa = models.TextField('Descrição longa')
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m/', blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    # preco_marketing = models.FloatField('Preço')
    # preco_marketing_promocional = models.FloatField(
    #     'Preço promocional', default=0)
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variação'),
            ('S', 'Simples')
        )
    )

    def __str__(self) -> str:
        return self.nome

    # def preco_marketing_formatado(self):
    #     return formata_dinheiro(self.preco_marketing)
    # preco_marketing_formatado.short_description = 'Preço'

    # def preco_marketing_promocional_formatado(self):
    #     return formata_dinheiro(self.preco_marketing_promocional)
    # preco_marketing_promocional_formatado.short_description = 'Preço promocional'

    def save(self, *args, **kwargs) -> None:
        if self.slug is None or not self.slug:
            self.slug = f'{slugify(self.nome)}'

        super().save(*args, **kwargs)

        self.resize_image(self.imagem)

    @staticmethod
    def resize_image(img: models.ImageField, new_width: int = 800) -> None:
        if not img:
            return

        # TODO: pesquisar sobre img.file, mais especificamente se há problema
        # em usar .close() nele
        with Image.open(img.path) as pil_img:
            old_width, old_height = pil_img.size

            if old_width > new_width:
                new_height = round(new_width * old_height / old_width)

                pil_img.resize(
                    (new_width, new_height), Image.LANCZOS
                ).save(
                    img.path, optimize=True, quality=50
                )


class Variacao(models.Model):
    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'

        db_table = 'variacao'

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    preco = models.FloatField('Preço')
    preco_promocional = models.FloatField('Preço promocional', default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return self.nome or self.produto.nome
