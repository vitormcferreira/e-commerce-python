from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from utils import functions
from utils.functions import valida_cpf

# para adicionar os erros


class Perfil(models.Model):
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

        db_table = 'perfil'

    usuario = models.OneToOneField(
        verbose_name='Usuário', to=User, on_delete=models.CASCADE)
    data_nascimento = models.DateField('Data de nascimento')
    cpf = models.CharField('CPF', max_length=11)

    def __str__(self) -> str:
        return self.usuario.get_full_name() or str(self.usuario)

    # validação a nivel de model
    # https://docs.djangoproject.com/en/3.2/ref/models/instances/#django.db.models.Model.clean
    def clean(self):
        error_list = []

        if not valida_cpf(self.cpf):
            error_list.append({'cpf': 'Digite um CPF válido'})

        if error_list:
            error_list = functions.normalize_error_list(error_list)
            raise ValidationError(error_list)


class Endereco(models.Model):
    class Meta:
        db_table = 'endereco'

    apelido = models.CharField(
        max_length=50, blank=False,
        help_text='Digite aqui um apelido para o endereço. '
        'Ele será usado para você identificar o endereço durante a compra'
    )
    endereco = models.CharField('Endereço', max_length=50)
    numero = models.CharField('Número', max_length=5)
    complemento = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField('CEP', max_length=8)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(
        max_length=2,
        default='SP',
        choices=(
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        )
    )
    perfil = models.ForeignKey(to=Perfil, on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        error_list = []

        apelido_repetido = Endereco.objects.all().filter(apelido=self.apelido).exists()
        if apelido_repetido:
            error_list.append({
                'apelido': 'Você já possui um endereço com este apelido. Escolha outro.'
            })

        if error_list:
            error_list = functions.normalize_error_list(error_list)
            raise ValidationError(error_list)

    def __str__(self):
        return f'{self.apelido}'
