# Generated by Django 4.1.2 on 2022-11-30 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0018_alter_records_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounts_permission',
            name='model_type',
            field=models.CharField(default='first_accounts', max_length=255, verbose_name='Таблица'),
        ),
    ]
