# Generated by Django 3.1 on 2022-03-26 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0005_stage_list_display_name'),
        ('agency', '0023_interviewscorecard_interviewtemplate'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomTemplateScorecard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CustomTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField()),
                ('enable_file_input', models.BooleanField(default=False)),
                ('file_input', models.FileField(null=True, upload_to='')),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_agency_id', to='agency.agency')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agencycustom_creation_category', to='agency.templatecategory')),
                ('scorecards', models.ManyToManyField(null=True, related_name='agencycustomTemplate_scorecards', to='agency.CustomTemplateScorecard')),
                ('stage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agencycustom_creation_stage', to='candidate.stage_list')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agencycustom_creation_temnplate', to='agency.template_creation')),
            ],
        ),
    ]
