from django.contrib import admin

from perfil.models import Perfil, Endereco


class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cpf')
    list_display_links = ('usuario', 'cpf')


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Endereco)
