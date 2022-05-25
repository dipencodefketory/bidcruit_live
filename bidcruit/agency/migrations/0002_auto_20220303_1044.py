# Generated by Django 3.1 on 2022-03-03 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0001_initial'),
        ('candidate', '0001_initial'),
        ('agency', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolepermissions',
            name='permission',
            field=models.ManyToManyField(related_name='RolePermissions_permissionagency', to='candidate.Permissions'),
        ),
        migrations.AddField(
            model_name='rolepermissions',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='RolePermissions_agency', to='agency.role'),
        ),
        migrations.AddField(
            model_name='rolepermissions',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_RolePermissions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='role',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Role_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='role',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_Role', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='internaluserprofile',
            name='InternalUserid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InternalUser_agency', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='internaluserprofile',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InternalUserProfile_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='internaluserprofile',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internaluser_department', to='agency.department'),
        ),
        migrations.AddField(
            model_name='internaluserprofile',
            name='recruiter_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internaluser_RecruiterType', to='candidate.recruitertype'),
        ),
        migrations.AddField(
            model_name='internaluserprofile',
            name='role',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internaluser_role', to='agency.role'),
        ),
        migrations.AddField(
            model_name='internaluserprofile',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_InternalUserProfile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='internalcandidatenotes',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetailNotes_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='internalcandidatenotes',
            name='internal_candidate_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internal_candidate_notes_id', to='agency.internalcandidatebasicdetail'),
        ),
        migrations.AddField(
            model_name='internalcandidatenotes',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetailNotes_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetail_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='candidate_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Candidateid_InternalCandidateBasicDetail_agency', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='current_city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetail_current_city', to='candidate.city'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='notice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetail_applyjob_notice_period', to='candidate.noticeperiod'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='prefered_city',
            field=models.ManyToManyField(null=True, related_name='InternalCandidateBasicDetail_prefered_city', to='candidate.City'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='skills',
            field=models.ManyToManyField(null=True, related_name='InternalCandidateBasicDetail_skill_id', to='candidate.Skill'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetail_source', to='candidate.source'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='tags',
            field=models.ManyToManyField(null=True, related_name='InternalCandidateBasicDetail_tags_id', to='candidate.Tags'),
        ),
        migrations.AddField(
            model_name='internalcandidatebasicdetail',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetail_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FreelancerProfile_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='FreelancerProfile_city', to='candidate.city'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='FreelancerProfile_country', to='candidate.country'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='FreelancerProfile_state', to='candidate.state'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FreelancerProfile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='department',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Department_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='department',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_Department', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comp_agency_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_city', to='candidate.city'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='company_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comp_agency_connect_comp', to='company.company'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_country', to='candidate.country'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='industry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_industry', to='candidate.industrytype'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='payment_terms',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_payment_terms', to='candidate.paymentterms'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='replacement_terms',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_replacement_terms', to='candidate.replacementterms'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_state', to='candidate.state'),
        ),
        migrations.AddField(
            model_name='companyagencyconnection',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_CompanyAgencyConnection', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='candidatesecuredata',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateCandidateSecureData_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='candidatesecuredata',
            name='candidate_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Candidateid_CandidateSecureData_agency', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='candidatesecuredata',
            name='company_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='CandidateSecureData_company', to='company.company'),
        ),
        migrations.AddField(
            model_name='candidatesecuredata',
            name='job_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='CandidateSecureData_job_id', to='company.jobcreation'),
        ),
        migrations.AddField(
            model_name='candidatesecuredata',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateCandidateSecureData_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='associatejob',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetailAssociateJob_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='associatejob',
            name='internal_candidate_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internal_candidate_AssociateJob_id', to='agency.internalcandidatebasicdetail'),
        ),
        migrations.AddField(
            model_name='associatejob',
            name='internal_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internaluserassociatuser', to='agency.internaluserprofile'),
        ),
        migrations.AddField(
            model_name='associatejob',
            name='job_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='AssociateJob_job_id', to='company.jobcreation'),
        ),
        migrations.AddField(
            model_name='associatejob',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='InternalCandidateBasicDetailAssociateJob_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assignjobinternal',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='AssignJobInternal_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='assignjobinternal',
            name='internal_user_id',
            field=models.ManyToManyField(null=True, related_name='agency_AssignJobInternalUser', to='agency.InternalUserProfile'),
        ),
        migrations.AddField(
            model_name='assignjobinternal',
            name='job_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assign_job_id', to='company.jobcreation'),
        ),
        migrations.AddField(
            model_name='assignjobinternal',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_AssignJobInternal', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agencytype',
            name='agency_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_type', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='agencyprofile',
            name='agency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agencyprofile_agency', to='agency.agency'),
        ),
        migrations.AddField(
            model_name='agencyprofile',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_city', to='candidate.city'),
        ),
        migrations.AddField(
            model_name='agencyprofile',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_country', to='candidate.country'),
        ),
        migrations.AddField(
            model_name='agencyprofile',
            name='industry_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_industrytype', to='candidate.industrytype'),
        ),
        migrations.AddField(
            model_name='agencyprofile',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_state', to='candidate.state'),
        ),
        migrations.AddField(
            model_name='agencyprofile',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agency',
            name='agency_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_adminid_Employee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agency',
            name='user_id',
            field=models.ManyToManyField(null=True, related_name='agencyuserid', to=settings.AUTH_USER_MODEL),
        ),
    ]
