# Generated by Django 5.0.4 on 2024-05-03 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0012_alter_openaccount_account_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='account_number',
            new_name='your_account_number',
        ),
        migrations.AddField(
            model_name='transaction',
            name='withdraw_account_number',
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
    ]
