# Generated by Django 3.2.5 on 2021-07-23 00:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0002_auto_20210722_1914'),
        ('pedido', '0003_auto_20210722_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='perfil.perfil', verbose_name='Usuário'),
        ),
    ]
