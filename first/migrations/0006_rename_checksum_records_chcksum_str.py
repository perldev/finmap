# Generated by Django 4.1.2 on 2022-10-07 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0005_alter_records_checksum_alter_records_debit_credit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='records',
            old_name='checksum',
            new_name='chcksum_str',
        ),
    ]
