from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.list import ListView
from furl import furl
from pedido.views import DispatchLoginRequiredMixin

from . import forms, models

# TODO
# [x] Registrar
# [x] Login
# [x] Logout
# [ ] Atualizar (adicionar o campo email)
# [ ] AtualizarSenha
# [ ] ConfirmaSenha
# [x] ListaEnderecos
# [x] RegistrarEndereco
# [x] AtualizarEndereco
# [x] RemoverEndereco


class BaseRegistrar(View):
    template_name = 'perfil/registrar.html'

    def get_context_data(self, registrarusuarioform=None, registrarperfilform=None, loginform=None, *args, **kwargs):
        """Retorna o contexto com os forms. Se o form foi enviado, retorna o próprio."""
        contexto = {
            'registrarusuarioform': registrarusuarioform or forms.RegistrarUsuarioForm(),
            'registrarperfilform': registrarperfilform or forms.RegistrarPerfilForm(),
            'loginform': loginform or forms.LoginForm(),
        }
        return contexto


class Registrar(BaseRegistrar):
    def get(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            # TODO: Trocar por redirecionar para o perfil
            return redirect(reverse('produto:carrinho'))

        contexto = self.get_context_data(*args, **kwargs)
        return render(request, self.template_name, contexto)

    def post(self, request: HttpRequest, *args, **kwargs):
        registrarusuarioform = forms.RegistrarUsuarioForm(data=request.POST)
        registrarperfilform = forms.RegistrarPerfilForm(data=request.POST)

        # Formulário válido: Registra o usuário e perfil
        if registrarusuarioform.is_valid() and registrarperfilform.is_valid():
            usuario = registrarusuarioform.save()
            perfil = registrarperfilform.save(commit=False)

            perfil.usuario = usuario
            perfil.save()

            messages.success(
                request,
                'Conta criada com sucesso, agora faça login.'
            )
            return redirect(reverse('perfil:registrar'))

        messages.error(request, 'Existem erros no formulário.')

        # Formulário inválido: Exibe o formulário com os erros
        contexto = self.get_context_data(
            registrarusuarioform=registrarusuarioform,
            registrarperfilform=registrarperfilform,
            *args, **kwargs
        )
        return render(request, self.template_name, contexto)


class Login(BaseRegistrar):
    def post(self, request: HttpRequest, *args, **kwargs):
        http_referer = request.META.get('HTTP_REFERER')

        carrinho = request.session.get('carrinho', {})

        loginform = forms.LoginForm(data=request.POST)

        if loginform.is_valid():
            user = loginform.get_user()
            auth.login(request, user)

            # copia o carrinho da sessão anterior
            request.session['carrinho'] = carrinho

            return redirect(
                request.GET.get(
                    'redirect_url', reverse('produto:listaprodutos')
                )
            )

        messages.error(request, 'Existem erros no formulário.')

        contexto = self.get_context_data(loginform=loginform, *args, **kwargs)
        return render(request, self.template_name, contexto)


@method_decorator(login_required, name='dispatch')
class Logout(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        carrinho = request.session.get('carrinho', {})

        auth.logout(request)

        # copia o carrinho da sessão anterior
        request.session['carrinho'] = carrinho

        return redirect(reverse('produto:listaprodutos'))


# decorando classes com login_required
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#decorating-class-based-views
@method_decorator(login_required, name='dispatch')
class Atualizar(View):
    template_name = 'perfil/atualizar.html'

    def get_context_data(self, *args, **kwargs):
        """Retorna o contexto com os forms."""

        usuario = self.request.user

        perfil = None
        if hasattr(usuario, 'perfil'):
            perfil = usuario.perfil

        contexto = {
            'atualizarusuarioform': forms.AtualizarUsuarioForm(
                data=self.request.POST or None,
                instance=usuario,
            ),
            'atualizarperfilform': forms.AtualizarPerfilForm(
                data=self.request.POST or None,
                instance=perfil,
            ),
        }

        return contexto

    def get(self, request: HttpRequest, *args, **kwargs):
        contexto = self.get_context_data(*args, **kwargs)
        return render(request, self.template_name, contexto)

    def post(self, request: HttpRequest, *args, **kwargs):
        contexto = self.get_context_data(*args, **kwargs)

        atualizarusuarioform = contexto['atualizarusuarioform']
        atualizarperfilform = contexto['atualizarperfilform']

        if atualizarusuarioform.is_valid() and atualizarperfilform.is_valid():
            # TODO: Para atualizar deve-se antes confirmar a senha
            usuario = atualizarusuarioform.save()
            perfil = atualizarperfilform.save(commit=False)

            perfil.usuario = usuario

            perfil.save()

            messages.success(request, 'Dados alterados com sucesso.')

            if 'username' in atualizarusuarioform.changed_data:
                auth.logout(request)
                messages.success(
                    request,
                    'Nome de usuário alterado com sucesso. '
                    'Faça login novamente.'
                )
                return redirect(reverse('perfil:registrar'))

            # BUG: Quando adiciona o campo email ao formulário em contexto
            # é levantada exceção.
            # O campo email está desativado e para ativar basta adicionar
            # email aos fields do form do usuario
            return redirect(reverse('perfil:atualizar'))

        messages.error(request, 'Existem erros no formulário.')
        return render(request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class AtualizarSenha(View):
    template_name = 'perfil/atualizarsenha.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class ConfirmaSenha(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, 'perfil/confirmasenha.html')


class ListaEnderecos(DispatchLoginRequiredMixin, ListView):
    model = models.Endereco
    template_name = 'perfil/listaenderecos.html'
    context_object_name = 'enderecos'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().filter(
            perfil_id=self.request.user.perfil.pk
        ).order_by(
            'estado'
        )
        return qs


class RegistrarEndereco(DispatchLoginRequiredMixin, View):
    template_name = 'perfil/registrarendereco.html'

    def get_context_data(self, *args, **kwargs):
        contexto = {
            'registrarenderecoform': forms.RegistrarEnderecoForm(
                data=self.request.POST or None,
            )
        }
        return contexto

    def get(self, request: HttpRequest, *args, **kwargs):
        contexto = self.get_context_data(*args, **kwargs)
        return render(request, self.template_name, contexto)

    def post(self, request: HttpRequest, *args, **kwargs):
        contexto = self.get_context_data(*args, **kwargs)
        registrarenderecoform = contexto['registrarenderecoform']

        if registrarenderecoform.is_valid():
            endereco = registrarenderecoform.save(commit=False)
            perfil = request.user.perfil
            endereco.perfil = perfil
            endereco.save()
            messages.success(request, 'Endereço registrado com sucesso')
            return redirect(reverse('perfil:listaenderecos'))

        messages.error(request, 'Existem erros no formulário.')

        return render(request, self.template_name, contexto)


class AtualizarEndereco(DispatchLoginRequiredMixin, View):
    template_name = 'perfil/atualizarendereco.html'

    def get_context_data(self, *args, **kwargs):
        endereco_id = kwargs.get('pk')
        endereco = models.Endereco.objects.filter(pk=endereco_id).first()
        contexto = {
            'atualizarenderecoform': forms.AtualizarEnderecoForm(
                data=self.request.POST or None,
                instance=endereco
            )
        }
        return contexto

    def get(self, request: HttpRequest, *args, **kwargs):
        contexto = self.get_context_data(*args, **kwargs)
        return render(request, self.template_name, contexto)

    def post(self, request: HttpRequest, *args, **kwargs):
        contexto = self.get_context_data(*args, **kwargs)

        atualizarenderecoform = contexto['atualizarenderecoform']

        if atualizarenderecoform.is_valid():
            atualizarenderecoform.save()
            messages.success(request, 'Endereço editado com sucesso.')

            return redirect(reverse('perfil:listaenderecos'))

        messages.error(request, 'Existem erros no formulário.')

        return render(request, self.template_name, contexto)


class RemoverEndereco(DispatchLoginRequiredMixin, View):
    http_method_names = ['get']
    template_name = 'perfil/removerendereco.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        endereco_id = request.GET.get('eid')

        if endereco_id:
            models.Endereco.objects.filter(pk=endereco_id).delete()
            messages.success(request, 'Endereco apagado com sucesso.')

        return redirect(reverse('perfil:listaenderecos'))


class Teste(View):
    def get(self, request, *args, **kwargs):
        raise Http404()
        form = forms.RegistrarUsuarioForm({
            'first_name': '',
            'last_name': 'teste',
            'username': 'teste',
            'email': 'teste@teste.com',
            'password1': 'teste',
            'password2': 'teste',
            'data_nascimento': 'teste',
            'cpf': 'teste',
        })
        res = f"""
            <p>{form.is_valid()}</p>
            <p>{form.errors}</p>
            <p></p>
        """

        return HttpResponse(res)
