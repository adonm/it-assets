# Generated by Django 2.2.14 on 2020-07-09 04:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bigpicture', '0002_auto_20200709_1224'),
        ('registers', '0029_auto_20200708_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='itsystem',
            name='dependencies',
            field=models.ManyToManyField(blank=True, help_text='Dependencies used by this IT system', to='bigpicture.Dependency'),
        ),
        migrations.AddField(
            model_name='itsystem',
            name='platform',
            field=models.ForeignKey(blank=True, help_text='The primary platform used to provide this IT system', null=True, on_delete=django.db.models.deletion.SET_NULL, to='bigpicture.Platform'),
        ),
    ]
