# Generated by Django 3.2.5 on 2021-08-06 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0006_rename_perfis_endereco_perfil'),
    ]

    operations = [
        migrations.AddField(
            model_name='endereco',
            name='apelido',
            field=models.CharField(default='', max_length=50, unique=True),
        ),
    ]
