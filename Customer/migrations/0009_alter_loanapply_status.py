# Generated by Django 5.0.4 on 2024-05-02 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0008_loanapply_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanapply',
            name='status',
            field=models.CharField(choices=[('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Pending', 'Pending')], default='Pending', max_length=20),
        ),
    ]
