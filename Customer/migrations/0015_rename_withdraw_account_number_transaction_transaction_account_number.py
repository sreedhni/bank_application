# Generated by Django 5.0.4 on 2024-05-03 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0014_alter_transaction_deposit_amount_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='withdraw_account_number',
            new_name='transaction_account_number',
        ),
    ]