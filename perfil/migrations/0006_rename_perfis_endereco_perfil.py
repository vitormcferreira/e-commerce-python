# Generated by Django 3.2.5 on 2021-08-04 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0005_auto_20210802_2125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='endereco',
            old_name='perfis',
            new_name='perfil',
        ),
    ]