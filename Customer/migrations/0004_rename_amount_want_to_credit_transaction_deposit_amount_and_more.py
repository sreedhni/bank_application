# Generated by Django 5.0.4 on 2024-04-29 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0003_transaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='amount_want_to_credit',
            new_name='deposit_amount',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='amount_want_to_debit',
            new_name='withdraw_amount',
        ),
    ]
