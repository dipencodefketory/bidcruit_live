# Generated by Django 3.1 on 2022-05-21 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0024_auto_20220513_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliedcandidate',
            name='dailysubmission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='DailySubmission_id_AppliedCandidate', to='company.dailysubmission'),
        ),
    ]
