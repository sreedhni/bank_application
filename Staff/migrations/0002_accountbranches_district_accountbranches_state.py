# Generated by Django 5.0.4 on 2024-04-28 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbranches',
            name='district',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='accountbranches',
            name='state',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
