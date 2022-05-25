# Generated by Django 3.1 on 2022-03-31 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agency', '0037_customresult_customscorecardresult'),
        ('candidate', '0007_agency_mcq_exam_agency_mcq_exam_result'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agency_ExamTimeStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(null=True)),
                ('candidate_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_exam_time_status_candidate_id', to=settings.AUTH_USER_MODEL)),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_exam_time_status_job_id', to='agency.jobcreation')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_exam_time_status_template_id', to='agency.template_creation')),
            ],
        ),
    ]
