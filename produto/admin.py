from django.contrib import admin

from .models import Produto, Variacao


class VariacaoInline(admin.TabularInline):
    model = Variacao
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'descricao_curta',
        # 'preco_marketing_formatado',
        # 'preco_marketing_promocional_formatado'
    )
    inlines = [VariacaoInline]


# class VariacaoAdmin(admin.ModelAdmin):
#     list_display = ('produto', 'nome', 'preco', 'preco_promocional', 'estoque')


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Variacao)
