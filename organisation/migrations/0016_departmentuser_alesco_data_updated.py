# Generated by Django 2.2.14 on 2020-08-27 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0015_adaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='departmentuser',
            name='alesco_data_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
