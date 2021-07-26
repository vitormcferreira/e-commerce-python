from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View


class Pagar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Pagar GET')


class FecharPedido(View):
    def get(self, *args, **kwargs):
        return HttpResponse('FecharPedido GET')


class Detalhe(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detalhe GET')
