from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from utils import functions

from .models import Endereco, Perfil


class RegistrarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = '__all__'
        exclude = ['usuario']


class RegistrarUsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean_email(self):
        data = self.cleaned_data["email"]
        errors = []

        if User.objects.filter(email=data):
            errors.append('Email já cadastrado.')

        if errors:
            raise ValidationError(errors)

        return data


class LoginForm(AuthenticationForm):
    pass


class AtualizarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']  # , 'email']


class AtualizarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        exclude = ['usuario']
        # exclude = ['usuario', 'data_nascimento', 'cpf']


# TODO: Formulário de alteração de senha


class RegistrarEnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        exclude = ['perfil']


class AtualizarEnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        exclude = ['perfil']
