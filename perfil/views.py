from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView

from . import models


class Criar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Criar GET')


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar GET')


class Login(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Login GET')


class Logout(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Logout GET')
