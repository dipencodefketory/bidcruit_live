# Generated by Django 3.1 on 2022-03-03 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0002_auto_20220303_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissionsmodel',
            name='display_name',
            field=models.CharField(default='1', max_length=500),
            preserve_default=False,
        ),
    ]