# Generated by Django 4.1.2 on 2022-10-10 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0009_records_to_accounts_records_to_contragent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='records',
            name='contragent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='first.contragents', verbose_name=' Контрагент'),
        ),
    ]
