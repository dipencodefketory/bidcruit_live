# Generated by Django 3.1 on 2022-05-03 05:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0050_auto_20220502_1159'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailysubmission',
            old_name='varify',
            new_name='verify',
        ),
    ]
