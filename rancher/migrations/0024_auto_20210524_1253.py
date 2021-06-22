# Generated by Django 2.2.21 on 2021-05-24 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rancher', '0023_auto_20210524_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='containerimage',
            name='scan_summary',
            field=models.CharField(editable=False, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='containerimage',
            name='scan_status',
            field=models.SmallIntegerField(choices=[(0, 'Not Scan'), (-1, 'Scan Failed'), (1, 'No Risk'), (2, 'Low Risk'), (4, 'Medium Risk'), (8, 'High Risk')], db_index=True, default=0, editable=False),
        ),
    ]