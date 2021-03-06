# Generated by Django 3.1 on 2022-05-02 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0049_auto_20220502_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailysubmission',
            name='categories',
            field=models.ManyToManyField(null=True, related_name='DailySubmission_categories_id', to='agency.CandidateCategories'),
        ),
        migrations.AddField(
            model_name='dailysubmission',
            name='tags',
            field=models.ManyToManyField(null=True, related_name='DailySubmission_tags_id', to='agency.Tags'),
        ),
    ]
