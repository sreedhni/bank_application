# Generated by Django 5.0.4 on 2024-05-02 11:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0006_alter_openaccount_total_amount'),
        ('Staff', '0007_loantype_loandetail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanApply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loanAmount', models.IntegerField()),
                ('Proof_of_identity', models.CharField(choices=[('passport', 'Passport'), ('VotersId', 'Voters ID'), ('DrivingLicence', 'Driving Licence'), ('PanCard', 'Pan Card')], max_length=100)),
                ('Address_proof', models.CharField(choices=[('RationCard', 'Ration Card'), ('TelElectricityBill', 'Tel/Electricity Bill'), ('LeaseAgreement', 'Lease Agreement'), ('Passport', 'Passport')], max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='loan_application_photos')),
                ('salary_certificate', models.FileField(blank=True, null=True, upload_to='salary_certificates')),
                ('income_tax_returns', models.FileField(blank=True, null=True, upload_to='income_tax_returns')),
                ('salary_account_statement', models.FileField(blank=True, null=True, upload_to='salary_account_statements')),
                ('loan_application_form', models.FileField(blank=True, null=True, upload_to='loan_application_forms')),
                ('applicant_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('loanname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Staff.loandetail')),
            ],
        ),
    ]
