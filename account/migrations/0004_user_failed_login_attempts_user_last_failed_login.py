# Generated by Django 5.0.4 on 2024-05-04 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_has_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='failed_login_attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='last_failed_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
