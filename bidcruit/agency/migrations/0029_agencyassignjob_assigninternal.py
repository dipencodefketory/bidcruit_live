# Generated by Django 3.1 on 2022-03-28 10:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agency', '0028_jobcreation'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignInternal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_rejected', models.BooleanField(default=False)),
                ('is_terminated', models.BooleanField(default=False)),
                ('send_email', models.BooleanField(default=False)),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_id_AssignInternal', to='agency.agency')),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_job_assigninternal_id', to='agency.jobcreation')),
                ('recruiter_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_recruiter_job_assigninternal', to=settings.AUTH_USER_MODEL)),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_create_user_id_AssignInternal', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgencyAssignJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recruiter_type_external', models.BooleanField(default=False)),
                ('recruiter_type_internal', models.BooleanField(default=False)),
                ('agency_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_id_CompanyAssignJob', to='agency.agency')),
                ('job_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_job_assign_id', to='agency.jobcreation')),
                ('recruiter_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_create_user_id_recruiter_id', to=settings.AUTH_USER_MODEL)),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_create_user_id_CompanyAssignJob', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]