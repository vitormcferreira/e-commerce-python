from django.contrib import messages
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from furl import furl


class DispatchLoginRequiredMixin:
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        http_referer = request.META.get(
            'HTTP_REFERER', reverse('produto:resumodacompra'))

        if not request.user.is_authenticated:
            messages.error(request, 'Logue ou crie uma conta para continuar.')

            obj_furl = furl(reverse('perfil:registrar'),
                            args={'redirect_url': http_referer})
            return redirect(obj_furl.url)

        if not hasattr(request.user, 'perfil'):
            messages.error(
                request,
                'Seu usuário não possui um perfil. Preencha as informações '
                'faltantes para continuar.'
            )
            obj_furl = furl(reverse('perfil:atualizar'),
                            args={'redirect_url': http_referer})
            return redirect(obj_furl.url)

        return super().dispatch(request, *args, **kwargs)
