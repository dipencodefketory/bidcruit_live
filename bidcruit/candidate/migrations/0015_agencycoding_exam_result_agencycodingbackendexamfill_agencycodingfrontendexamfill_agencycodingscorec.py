# Generated by Django 3.1 on 2022-04-07 07:42

import candidate.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agency', '0037_customresult_customscorecardresult'),
        ('candidate', '0014_auto_20220407_0620'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyCodingScoreCardFill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(null=True)),
                ('comment', models.TextField(null=True)),
                ('rating', models.CharField(max_length=10, null=True)),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scorecard_agency_id', to='agency.agency')),
                ('candidate_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_scorecard', to=settings.AUTH_USER_MODEL)),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_scorecard_job_id', to='agency.jobcreation')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_scorecard_template_id', to='agency.template_creation')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_internal_user_scorecard_assessment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgencyCodingFrontEndExamFill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html_code', tinymce.models.HTMLField(null=True)),
                ('css_code', tinymce.models.HTMLField(null=True)),
                ('js_code', tinymce.models.HTMLField(null=True)),
                ('obtain_marks', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='front_end_exam_agency_id', to='agency.agency')),
                ('candidate_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_front_end_exam_candidate_id', to=settings.AUTH_USER_MODEL)),
                ('exam_question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_frontend_exam_que_id', to='agency.codingexamquestions')),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_frontend_exam_job_id', to='agency.jobcreation')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_front_end_exam_template_id', to='agency.template_creation')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_coding_front_end_assessment_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgencyCodingBackEndExamFill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_code', tinymce.models.HTMLField(null=True)),
                ('obtain_marks', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='back_end_exam_agency_id', to='agency.agency')),
                ('candidate_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_back_end_exam_candidate_id', to=settings.AUTH_USER_MODEL)),
                ('exam_question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_backend_exam_que_id', to='agency.codingexamquestions')),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_backend_exam_job_id', to='agency.jobcreation')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_back_end_exam_template_id', to='agency.template_creation')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_coding_backend_assessment_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgencyCoding_Exam_result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_question', models.IntegerField(null=True)),
                ('answered', models.IntegerField(null=True)),
                ('obtain_marks', models.CharField(max_length=10, null=True)),
                ('coding_pdf', models.FileField(max_length=500, null=True, upload_to=candidate.models.agency_coding_document_path_handler)),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_coding_exam_result', to='agency.agency')),
                ('candidate_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_coding_exam_result', to=settings.AUTH_USER_MODEL)),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_coding_exam_result_job_id', to='agency.jobcreation')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_candidate_coding_exam_template_id_result', to='agency.template_creation')),
            ],
        ),
    ]
