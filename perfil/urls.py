from django.urls import path

from . import views


app_name = 'perfil'
urlpatterns = [
    path('', views.Registrar.as_view(), name='registrar'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('atualizar/', views.Atualizar.as_view(), name='atualizar'),

    # TODO: Atualizar senha
    path('atualizarsenha/', views.AtualizarSenha.as_view(), name='atualizarsenha'),

    path('listaenderecos/', views.ListaEnderecos.as_view(), name='listaenderecos'),
    path('registrarendereco/', views.RegistrarEndereco.as_view(), name='registrarendereco'),
    path('atualizarendereco/<int:pk>/', views.AtualizarEndereco.as_view(), name='atualizarendereco'),
    path('removerendereco/', views.RemoverEndereco.as_view(), name='removerendereco'),
    
    # TODO: Confirmar senha
    path('confirmasenha/', views.ConfirmaSenha.as_view(), name='confirmasenha'),
    
    # path('teste/', views.Teste.as_view(), name='teste'),
]
