# Generated by Django 3.1 on 2022-04-09 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0011_auto_20220401_1308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobcreationtemplate',
            name='status',
        ),
    ]
