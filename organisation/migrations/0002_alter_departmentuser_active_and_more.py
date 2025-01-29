# Generated by Django 4.2.18 on 2025-01-24 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentuser',
            name='active',
            field=models.BooleanField(default=True, editable=False, help_text='Account is enabled within Active Directory / Entra ID'),
        ),
        migrations.AlterField(
            model_name='departmentuser',
            name='azure_guid',
            field=models.CharField(blank=True, help_text='Azure Active Directory (Entra ID) unique object ID', max_length=48, null=True, unique=True, verbose_name='Azure GUID'),
        ),
    ]
