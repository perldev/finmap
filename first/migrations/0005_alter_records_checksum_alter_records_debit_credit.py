# Generated by Django 4.1.2 on 2022-10-07 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0004_alter_accounts_creator_alter_contragents_creator_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='records',
            name='checksum',
            field=models.CharField(default='', max_length=255, unique=True, verbose_name='checksum'),
        ),
        migrations.AlterField(
            model_name='records',
            name='debit_credit',
            field=models.CharField(choices=[('debit', 'Доход'), ('credit', 'Расход'), ('transfer', 'Перевод')], max_length=20, verbose_name='тип операции'),
        ),
    ]
