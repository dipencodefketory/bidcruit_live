# Generated by Django 3.1 on 2022-04-23 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0041_auto_20220423_0804'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailysubmission',
            name='job_type',
            field=models.CharField(default='company', max_length=10),
            preserve_default=False,
        ),
    ]
