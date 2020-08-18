# Generated by Django 2.2.14 on 2020-08-04 05:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organisation', '0014_auto_20200804_1132'),
    ]

    operations = [
        migrations.CreateModel(
            name='ADAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action_type', models.CharField(choices=[('Change email', 'Change email'), ('Change account field', 'Change account field'), ('Disable account', 'Disable account'), ('Enable account', 'Enable account')], max_length=128)),
                ('ad_field', models.CharField(blank=True, help_text='Name of the field in Active Directory', max_length=128, null=True)),
                ('ad_field_value', models.TextField(blank=True, help_text='Value of the field in Active Directory', null=True)),
                ('field', models.CharField(blank=True, help_text='Name of the field in IT Assets', max_length=128, null=True)),
                ('field_value', models.TextField(blank=True, help_text='Value of the field in IT Assets', null=True)),
                ('completed', models.DateTimeField(blank=True, editable=False, null=True)),
                ('completed_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('department_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisation.DepartmentUser')),
            ],
            options={
                'verbose_name': 'AD action',
                'verbose_name_plural': 'AD actions',
            },
        ),
    ]