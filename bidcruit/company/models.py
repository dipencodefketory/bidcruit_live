from django.db import models
from datetime import date
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from tinymce.models import HTMLField
from candidate import models as CandidateModels
import random
from tinymce.models import HTMLField
import os
from django.utils import timezone
from django.db.models.fields.related import ForeignKey, ManyToManyField
from bidcruit import settings
from colorfield.fields import ColorField
def generate_pk():
    number = random.randint(1000, 99999)
    return 'company-{}-{}'.format(timezone.now().strftime('%y%m%d'), number)

# ##################################### Common Models ########################################################


class Company(models.Model):
    company_id=models.ForeignKey(User, related_name="company_adminid_Employee", on_delete=models.CASCADE,
                                     null=True)
    user_id=models.ManyToManyField(User, related_name="company_userid",
                                     null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Role(models.Model):
    name = models.CharField(max_length=20)
    system_generated = models.BooleanField(default=False)
    status=models.BooleanField(default=False)
    description=models.CharField(max_length=500,null=True)
    company_id=models.ForeignKey(Company,related_name="Role_company",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='company_Role',on_delete=models.CASCADE)

class RolePermissions(models.Model):
    system_generated = models.BooleanField(default=False)
    role=models.ForeignKey(Role,related_name="RolePermissions_company",on_delete=models.CASCADE)
    permission=models.ManyToManyField(CandidateModels.Permissions,related_name="RolePermissions_permission")
    company_id=models.ForeignKey(Company,related_name="RolePermissions_company",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='company_RolePermissions',on_delete=models.CASCADE)



# ##################################### Common Models Ends ########################################################


class CandidateHire(models.Model):
    # id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    company_id = models.ForeignKey(User, related_name="Company_id", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name="candidate_hire_id", on_delete=models.CASCADE)
    message = models.CharField(max_length=50)
    profile_id = models.ForeignKey(CandidateModels.Profile,related_name='profile_id',null=True,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    request_status = models.IntegerField(default=0,null=True)

    def __str__(self):
        return str(self.id)


class CandidateSelectedPreference(models.Model):
    # id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    company_id = models.ForeignKey(User, related_name="preference_check_company_id", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name="preference_check_candidate_id", on_delete=models.CASCADE)
    preference_name = models.CharField(max_length=100)
    # preference_id = models.ForeignKey(CandidateModels.CandidateJobPreference, related_name="candidate_preference_id", on_delete=models.CASCADE)
    is_selected = models.BooleanField(null=True)

    def __str__(self):
        return str(self.id)


class CompanyProfile(models.Model):
    employee_count_choices = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001-5000', '1001-5000 employees'),
        ('5001-10,000', '5001-10,000 employees'),
        ('10,001+', '10,001+ employees'),
    ]
    company_type_choices = [
        ('Public Company','Public Company'),
        ('Educational','Educational'),
        ('Self Employed','Self Employed'),
        ('Government Agency','Government Agency'),
        ('Non Profit','Non Profit'),
        ('Self Owned','Self Owned'),
        ('Privately Held','Privately Held'),
        ('Partnership','Partnership')
        ]
    universal_Name = models.CharField(max_length=500)
    contact_email = models.EmailField()
    compnay_type = models.CharField(max_length=50,choices=company_type_choices)
    industry_type = models.ForeignKey(CandidateModels.IndustryType, related_name="company_industrytype", on_delete=models.CASCADE, null=True)
    company_logo = models.ImageField(verbose_name="company_logo_image")
    company_bg = models.ImageField(verbose_name="company_bg_image")
    speciality = models.TextField()
    aboutus = models.TextField()
    address = models.CharField(max_length=255)
    country = models.ForeignKey(CandidateModels.Country, related_name="company_country", on_delete=models.CASCADE, null=True)
    state = models.ForeignKey(CandidateModels.State, related_name="company_state", on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(CandidateModels.City, related_name="company_city", on_delete=models.CASCADE, null=True)
    zip_code = models.CharField(max_length=10, null=True)
    contact_no1 = models.CharField(max_length=10)
    founded_year = models.CharField(max_length=5)
    employee_count = models.CharField(max_length=50,choices=employee_count_choices)
    company_id = models.ForeignKey(Company,related_name='company_id_profile',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_profile',on_delete=models.CASCADE,null=True)


class ShortlistedCandidates(models.Model):
    candidate_id = models.ForeignKey(User, related_name="shortlisted_candidate_id", on_delete=models.CASCADE,null=True)
    company_id = models.ForeignKey(User, related_name="shortlisted_company_id", on_delete=models.CASCADE, null=True)

# ############################################    ATS    #################################################


#  ################## -------ADD Candidate------- ##################


class InternalCandidate(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    gender = models.ForeignKey(CandidateModels.Gender, related_name="internal_candidate_gender",
                               on_delete=models.CASCADE, null=True)
    dob = models.CharField(max_length=20, null=True)
    phone_no = models.CharField(max_length=20)
    current_country = models.ForeignKey(CandidateModels.Country, related_name="internal_candidate_current_country",
                                        on_delete=models.CASCADE, null=True)
    current_state = models.ForeignKey(CandidateModels.State, related_name="internal_candidate_current_state",
                                      on_delete=models.CASCADE, null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="internal_candidate_current_city",
                                     on_delete=models.CASCADE, null=True)
    current_zip_code = models.CharField(max_length=10, null=True)
    current_street = models.CharField(max_length=50, null=True)
    permanent_country = models.ForeignKey(CandidateModels.Country, related_name="internal_candidate_permanent_country",
                                          on_delete=models.CASCADE, null=True)
    permanent_state = models.ForeignKey(CandidateModels.State, related_name="internal_candidate_permanent_state",
                                        on_delete=models.CASCADE, null=True)
    permanent_city = models.ForeignKey(CandidateModels.City, related_name="internal_candidate_permanent_city",
                                       on_delete=models.CASCADE, null=True)
    permanent_zip_code = models.CharField(max_length=10, null=True)
    permanent_street = models.CharField(max_length=50, null=True)


class InternalCandidateProfessionalDetail(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_professional_detail",
                                              on_delete=models.CASCADE, null=True)
    experience = models.CharField(max_length=20, null=True)
    current_job_title = models.CharField(max_length=30, null=True)
    highest_qualification = models.CharField(max_length=30, null=True)
    expected_salary = models.CharField(max_length=20, null=True)
    current_salary = models.CharField(max_length=20, null=True)
    current_employer = models.CharField(max_length=30, null=True)
    skills = models.CharField(max_length=100, null=True)
    notice_period = models.ForeignKey(CandidateModels.NoticePeriod, related_name="internal_candidate_notice_period",
                                      on_delete=models.CASCADE, null=True)


class InternalCandidateEducation(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_id",
                                              on_delete=models.CASCADE, null=True)
    university_board = models.ForeignKey(CandidateModels.UniversityBoard, related_name="internal_candidate_university",
                                         on_delete=models.CASCADE,
                                         null=True)
    department = models.CharField(max_length=50, null=True)
    degree = models.ForeignKey(CandidateModels.Degree, related_name="internal_candidate_degree",
                               on_delete=models.CASCADE, null=True)
    duration = models.CharField(max_length=50, null=True)
    start_date = models.CharField(max_length=50, null=True)
    end_date = models.CharField(max_length=50, null=True)
    is_pursuing = models.BooleanField(default=False, null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)


class InternalCandidateExperience(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_experience_id",
                                              on_delete=models.CASCADE,
                                              null=True)
    job_title = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=100, null=True)
    company = models.ForeignKey(CandidateModels.Company, related_name="internal_candidate_company_id",
                                on_delete=models.CASCADE,
                                null=True)
    start_date = models.CharField(max_length=100, null=True)
    end_date = models.CharField(max_length=100, null=True)
    summary = models.CharField(max_length=100, null=True)
    skills = models.ForeignKey(CandidateModels.Skill, related_name="internal_candidate_skill_id",
                               on_delete=models.CASCADE,
                               null=True)
    currently_working = models.BooleanField(default=False, null=True)
    # notice_period = models.ForeignKey(CandidateModels.NoticePeriod, related_name="internal_candidate_exp_notice_period",on_delete=models.CASCADE,
    #                            null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)


class InternalCandidatePreference(models.Model):
    working_day_choices = [
        ('5day', '5 Days Working'),
        ('6day', '6 Days Working')
    ]
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_preference",
                                              on_delete=models.CASCADE,
                                              null=True)
    country = models.ForeignKey(CandidateModels.Country, related_name="internal_candidate_preference_country",
                                on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(CandidateModels.City, related_name="internal_candidate_preference_city",
                             on_delete=models.CASCADE, null=True)
    company_type = models.ForeignKey(CandidateModels.CompanyType, related_name="internal_candidate_preference_company_type",
                                     on_delete=models.CASCADE, null=True)
    working_days = models.CharField(max_length=20, choices=working_day_choices)


class InternalCandidatePortfolio(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_portfolio",
                                              on_delete=models.CASCADE,
                                              null=True)
    project_name = models.CharField(max_length=100)
    project_link = models.CharField(max_length=100)
    attachment = models.FileField(null=True)
    description = HTMLField()


class InternalCandidateSource(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_source",
                                              on_delete=models.CASCADE,
                                              null=True)
    source_id = models.ForeignKey(CandidateModels.Source, related_name="internal_candidate_source_id", on_delete=models.CASCADE)
    custom_source_name = models.CharField(max_length=200,null=True)


class InternalCandidateAttachment(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_attachment",
                                              on_delete=models.CASCADE,
                                              null=True)
    file_name = models.CharField(max_length=50)
    file = models.FileField()


class InternalCandidateProfessionalSkill(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidate, related_name="internal_candidate_skill_user_id", on_delete=models.CASCADE,
                                     null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="internal_candidate_skill_user_map", null=True)
    custom_added_skills = models.ManyToManyField(CandidateModels.InternalCandidateAddedSkill, related_name="internal_candidate_skill_user_map", null=True)



    # user_id and department pending

#  ################## -------Job Creation------- ##################



class Department(models.Model):
    name = models.CharField(max_length=20)
    system_generated = models.BooleanField(default=False)
    status=models.BooleanField(default=False)
    company_id = models.ForeignKey(Company,related_name='company_id_Department',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Department',on_delete=models.CASCADE,null=True)
    def __str__(self):
        return str(self.name)

class JobCreation(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_JobCreation',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_JobCreation',on_delete=models.CASCADE,null=True)
    job_title = models.CharField(max_length=100,null=True)
    job_type = models.ForeignKey(CandidateModels.JobTypes,related_name="job_type_id",on_delete=models.CASCADE)
    contact_name = models.ForeignKey(User,related_name='contact_person_id',on_delete=models.CASCADE,null=True)
    target_date = models.DateField()
    status = models.ForeignKey(CandidateModels.JobStatus,null=True,related_name="job_status_id",on_delete=models.CASCADE)
    industry_type = models.ForeignKey(CandidateModels.IndustryType,related_name="industry_type_id",on_delete=models.CASCADE, null=True)
    remote_job = models.BooleanField()
    salary_as_per_market=models.BooleanField(default=False)
    min_salary = models.CharField(max_length=10)
    max_salary = models.CharField(max_length=10)
    experience_year_min = models.CharField(max_length=10)
    experience_year_max = models.CharField(max_length=10)
    job_description = HTMLField()
    benefits = HTMLField(max_length=100)
    requirements = HTMLField(max_length=100)
    required_skill=models.ManyToManyField(CandidateModels.Skill,related_name="required_skill_job",null=True)
    job_shift_id=models.ManyToManyField(CandidateModels.JobShift,related_name="JobShift_job",null=True)
    country = models.ForeignKey(CandidateModels.Country,related_name="job_country",on_delete=models.CASCADE)
    city = models.ForeignKey(CandidateModels.City,related_name="job_city",on_delete=models.CASCADE)
    department = models.ForeignKey(Department,related_name="job_department_id",on_delete=models.CASCADE, null=True)
    zip_code = models.CharField(max_length=10)
    job_owner = models.ForeignKey(User,related_name='job_owner',on_delete=models.CASCADE,null=True)
    job_link = models.TextField(null=True)
    is_publish = models.BooleanField(default=False)
    publish_at = models.DateTimeField(null=True)
    close_job_targetdate = models.BooleanField(default=False)
    close_job=models.BooleanField(default=False)
    close_job_at = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.id)


class CompanyAssignJob(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CompanyAssignJob',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CompanyAssignJob',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_assign_id", on_delete=models.CASCADE)
    recruiter_type_external=models.BooleanField(default=False)
    recruiter_type_internal=models.BooleanField(default=False)
    recruiter_id=models.ForeignKey(User,related_name='create_user_id_recruiter_id',on_delete=models.CASCADE,null=True)

from agency.models import Agency
class AssignExternal(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_AssignExternal',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AssignExternal',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_assignexternal_id", on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    recruiter_id = models.ForeignKey(Agency, related_name="recruiter_job_assignexternal", on_delete=models.CASCADE, null=True)

class AssignInternal(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_AssignInternal',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AssignInternal',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_assigninternal_id", on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    recruiter_id = models.ForeignKey(User, related_name="recruiter_job_assigninternal", on_delete=models.CASCADE, null=True)

class CompanyJobShift(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CompanyJobShift',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CompanyJobShift',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_id", on_delete=models.CASCADE)
    job_shift_id = models.ForeignKey(CandidateModels.JobShift, related_name="job_shift_id", on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

#  ################## -------Template Creation------- ##################




class TemplateCategory(models.Model):
    name = models.CharField(max_length=100)
    stage = models.ForeignKey(CandidateModels.Stage_list,on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company,related_name='company_id_Template',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Template',on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True)


class Template_creation(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="Template_creation_stage",on_delete=models.CASCADE)
    category = models.ForeignKey(TemplateCategory,related_name="Template_creation_category",on_delete=models.CASCADE,null=True)
    company_id = models.ForeignKey(Company,related_name='company_id_Template_creation',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Template_creation',on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True)
    status = models.BooleanField(default=False,null=True)
    created_by = models.CharField(max_length=10,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JCR(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_jcr',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_jcr',on_delete=models.CASCADE,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="jcr_creation_stage",on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(TemplateCategory, related_name="jcr_creation_category",on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="jcr_creation_temnplate",on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    ratio = models.IntegerField()
    flag = models.CharField(max_length=10, null=True)
    pid = models.ForeignKey('JCR', related_name='jcr_id',on_delete=models.CASCADE,null=True)


class PreRequisites(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_PreRequisites',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_PreRequisites',on_delete=models.CASCADE,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="prerequisites_creation_stage",on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(TemplateCategory,related_name="prerequisites_creation_category",on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation,related_name="prerequisites_creation_temnplate",on_delete=models.CASCADE,null=True)
    data = HTMLField()
    html_data = HTMLField()


# ############################################### Workflow Creation ###############################################


class Workflows(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Workflows',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Workflows',on_delete=models.CASCADE,null=True)
    name = models.TextField()
    is_configured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User, related_name='update_user_id_Workflows', on_delete=models.CASCADE,
                                  null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User, related_name='delete_user_id_Workflows', on_delete=models.CASCADE,
                                  null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class WorkflowStages(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_WorkflowStages',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_WorkflowStages',on_delete=models.CASCADE,null=True)
    stage_name = models.CharField(max_length=100)
    workflow = models.ForeignKey(Workflows, related_name="workflow_id", on_delete=models.CASCADE,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="workflow_stage", on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(TemplateCategory, related_name="workflow_category", on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="workflow_template",on_delete=models.CASCADE, null=True)
    sequence_number = models.IntegerField()
    display = models.BooleanField(default=True)


class WorkflowConfiguration(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_WorkflowConfiguration',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_WorkflowConfiguration',on_delete=models.CASCADE,null=True)
    workflow_stage = models.ForeignKey(WorkflowStages, related_name="workflow_stage_id", on_delete=models.CASCADE)
    interviewer = models.ManyToManyField(User,related_name="interview_name", null=True)
    is_automation = models.BooleanField(null=True)
    shortlist = models.FloatField(null=True)
    onhold = models.FloatField(null=True)
    reject = models.FloatField(null=True)


class JobCreationTemplate(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_JobTemplate', on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='create_user_id_JobTemplate', on_delete=models.CASCADE, null=True)
    job_title = models.CharField(max_length=100, null=True)
    job_type = models.ForeignKey(CandidateModels.JobTypes, related_name="job_template_type_id", on_delete=models.CASCADE)
    target_date = models.DateField()
    industry_type = models.ForeignKey(CandidateModels.IndustryType, related_name="job_template_industry_type_id",
                                      on_delete=models.CASCADE, null=True)
    remote_job = models.BooleanField()
    salary_as_per_market = models.BooleanField(default=False)
    min_salary = models.CharField(max_length=10)
    max_salary = models.CharField(max_length=10)
    experience_year_min = models.CharField(max_length=10)
    experience_year_max = models.CharField(max_length=10)
    job_description = HTMLField()
    benefits = HTMLField(max_length=100)
    requirements = HTMLField(max_length=100)
    jobshift = models.ManyToManyField(CandidateModels.JobShift, related_name="job_template_shift")
    required_skill = models.ManyToManyField(CandidateModels.Skill, related_name="job_template_required_skill",
                                            null=True)
    country = models.ForeignKey(CandidateModels.Country, related_name="job_template_country", on_delete=models.CASCADE)
    city = models.ForeignKey(CandidateModels.City, related_name="job_template_city", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name="job_template_department", on_delete=models.CASCADE,
                                   null=True)
    zip_code = models.CharField(max_length=10)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="job_creation_stage", on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(TemplateCategory, related_name="job_creation_category", on_delete=models.CASCADE,
                                 null=True)
    template = models.ForeignKey(Template_creation, related_name="job_creation_temnplate", on_delete=models.CASCADE,
                                 null=True)
    created_by = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User, related_name='update_user_id_JobCreationTemplates', on_delete=models.CASCADE,
                                  null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User, related_name='delete_user_id_JobCreationTemplate', on_delete=models.CASCADE,
                                  null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)


class JobWorkflow(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_JobWorkflow',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_JobWorkflow',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_workflow_id", on_delete=models.CASCADE)
    onthego=models.BooleanField(default=False)
    withworkflow=models.BooleanField(default=False)
    is_application_review = models.BooleanField(default=False)
    workflow_id = models.ForeignKey(Workflows, null=True, related_name="job_workflow_id", on_delete=models.CASCADE)
   

class Paragraph_subject(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Paragraph_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Paragraph_subject',on_delete=models.CASCADE,null=True)
    subject_name=models.CharField(max_length=50)


class Paragraph(models.Model):
    subject = models.ForeignKey(Paragraph_subject, related_name='paragraph_subject', null=True, on_delete=models.CASCADE)
    paragraph_type=models.CharField(max_length=50, null=True)
    company_id = models.ForeignKey(Company,related_name='company_id_Paragraph',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Paragraph',on_delete=models.CASCADE,null=True)
    paragraph_description=HTMLField()


class Paragraph_option(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Paragraph_option',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Paragraph_option',on_delete=models.CASCADE,null=True)
    paragraph=models.ForeignKey(Paragraph, related_name='option_paragraph', null=True, on_delete=models.CASCADE)
    subject = models.ForeignKey(Paragraph_subject, related_name='option_subject', null=True, on_delete=models.CASCADE)
    question=models.CharField(max_length=50)
    option1=models.CharField(max_length=50)
    option2=models.CharField(max_length=50)
    option3=models.CharField(max_length=50)
    option4=models.CharField(max_length=50)
    answer=models.CharField(max_length=50)


# Descriptive
class Descriptive_subject(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Descriptive_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Descriptive_subject',on_delete=models.CASCADE,null=True)
    subject_name = models.CharField(max_length=50)


class Descriptive(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Descriptive',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Descriptive',on_delete=models.CASCADE,null=True)
    subject = models.ForeignKey(Descriptive_subject, related_name='descriptive_subject', null=True,
                                on_delete=models.CASCADE)
    paragraph_description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)

# MCQ


class MCQ_subject(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_MCQ_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_MCQ_subject',on_delete=models.CASCADE,null=True)
    subject_name=models.CharField(max_length=50)


class mcq_Question(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_mcq_Question',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_mcq_Question',on_delete=models.CASCADE,null=True)
    mcq_subject=models.ForeignKey(MCQ_subject, related_name="mcq_subject_id",on_delete=models.CASCADE)
    question_description = models.TextField()
    question_level = models.ForeignKey(CandidateModels.QuestionDifficultyLevel,related_name="company_mcq_question_level",on_delete=models.CASCADE)
    correct_option = models.CharField(max_length=1)
    option_a = models.CharField(max_length=200,null=True)
    option_b = models.CharField(max_length=200,null=True)
    option_c = models.CharField(max_length=200,null=True)
    option_d = models.CharField(max_length=200,null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ExamTemplate(models.Model):
    # common fields
    company_id = models.ForeignKey(Company,related_name='company_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="mcq_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="mcq_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="mcq_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(MCQ_subject,related_name="mcq_subject_temnplate",null=True,on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=6) #two choices,random and custom
    total_question=models.IntegerField()
    basic_questions_count= models.IntegerField()
    intermediate_questions_count = models.IntegerField()
    advanced_questions_count = models.IntegerField()
    allow_negative_marking = models.BooleanField(default=True)
    #OPTIONAL  fields
    # total_question_count = models.IntegerField() can be calculated so not storing the total again
    marking_system = models.CharField(max_length=15,null=True)  # two  choices category-wise or question-wise
    basic_question_marks = models.IntegerField(null=True)
    intermediate_question_marks = models.IntegerField(null=True)
    advanced_question_marks = models.IntegerField(null=True)
    question_wise_time = models.BooleanField(null=True)
    duration = models.CharField(max_length=10,null=True)
    negative_mark_percent = models.IntegerField(default=0)
    basic_questions = ManyToManyField(mcq_Question,related_name="exam_template_basic_questions")
    intermediate_questions = ManyToManyField(mcq_Question,related_name="exam_template_intermediate_questions")
    advanced_questions = ManyToManyField(mcq_Question,related_name="exam_template_advanced_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class ExamQuestionUnit(models.Model):
    question = models.ForeignKey(mcq_Question,related_name="exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="mcq_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class QuestionPaper(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_QuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_QuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(ExamTemplate, related_name="question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(ExamQuestionUnit,related_name="question_paper_exam_question_units")




# Image based


class ImageSubject(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_ImageSubject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_ImageSubject',on_delete=models.CASCADE,null=True)
    subject_name=models.CharField(max_length=50)


class ImageQuestion(models.Model):
    subject = models.ForeignKey(ImageSubject, related_name='Image_subject', null=True, on_delete=models.CASCADE)
    question_level = models.ForeignKey(CandidateModels.QuestionDifficultyLevel,related_name="company_image_question_level",on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company,related_name='company_id_ImageQuestion',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_ImageQuestion',on_delete=models.CASCADE,null=True)
    image_que_description=models.TextField()
    question_file = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ImageOption(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_ImageOption',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_ImageOption',on_delete=models.CASCADE,null=True)
    question_id = models.ForeignKey(ImageQuestion, related_name='ImageQuestion_id', null=True, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(ImageSubject, related_name='ImageSubject_id', null=True, on_delete=models.CASCADE)
    option1=models.CharField(max_length=50)
    option2=models.CharField(max_length=50)
    option3=models.CharField(max_length=50)
    option4=models.CharField(max_length=50)
    answer=models.CharField(max_length=50)
    file1 = models.FileField(null=True)
    file2 = models.FileField(null=True)
    file3 = models.FileField(null=True)
    file4 = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class CodingSubject(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CodingSubject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CodingSubject',on_delete=models.CASCADE,null=True)
    api_subject_id = models.ForeignKey(CandidateModels.CodingApiSubjects, related_name='coding_api_subject_id', null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, null=True)   # two types - frontend, backend


class CodingSubjectCategory(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CodingSubjectCategory',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CodingSubjectCategory',on_delete=models.CASCADE,null=True)
    subject_id = models.ForeignKey(CodingSubject, related_name='coding_subject_id', null=True, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)


class CodingQuestion(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CodingQuestion',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CodingQuestion',on_delete=models.CASCADE,null=True)
    category_id = models.ForeignKey(CodingSubjectCategory, related_name='coding_category_id', null=True, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=50, null=True)
    coding_que_title = models.TextField()
    coding_que_description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)


class CodingExamConfiguration(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    template_id = models.ForeignKey(Template_creation,related_name="coding_config_template",on_delete=models.CASCADE)
    coding_subject_id = models.ForeignKey(CodingSubject, related_name='exam_config_coding_subject_id', on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    total_time = models.CharField(max_length=50)
    total_question = models.CharField(max_length=50)
    assignment_type = models.CharField(max_length=50)
    exam_type = models.CharField(max_length=50)
    technology = models.CharField(max_length=50)
    coding_category_id =  models.ForeignKey(CodingSubjectCategory, related_name='code_exam_config_category_id', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class CodingExamQuestions(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CodingExamQuestions',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_CodingExamQuestions',on_delete=models.CASCADE,null=True)
    coding_exam_config_id = models.ForeignKey(CodingExamConfiguration, related_name="coding_configuration_id",on_delete=models.CASCADE)
    question_id = models.ForeignKey(CodingQuestion, related_name="coding_question_id", on_delete=models.CASCADE)
    marks = models.CharField(null=True, max_length=10)


#  if exam assignment type is rating this model will get used
class CodingScoreCard(models.Model):
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True,max_length=10)
    coding_exam_config_id = models.ForeignKey(CodingExamConfiguration, related_name="coding_configuration_rating",
                                              on_delete=models.CASCADE)


class DescriptiveExamTemplate(models.Model):
    # common fields
    company_id = models.ForeignKey(Company,related_name='company_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="Descriptive_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="Descriptive_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="Descriptive_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(Descriptive_subject,related_name="Descriptive_subject_temnplate",null=True,on_delete=models.CASCADE)
    assignment_type = models.CharField(max_length=10,null=True) #two choices,random and custom
    #OPTIONAL  fields
    total_question = models.IntegerField()
    question_wise_time = models.BooleanField(default=True)
    descriptivequestions = ManyToManyField(Descriptive,related_name="Descriptive_exam_template_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)



class DescriptiveExamQuestionUnit(models.Model):
    question = models.ForeignKey(Descriptive,related_name="Descriptive_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="Descriptive_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class DescriptiveQuestionPaper(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_DescriptiveQuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_DescriptiveQuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(DescriptiveExamTemplate, related_name="Descriptive_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(DescriptiveExamQuestionUnit,related_name="Descriptive_question_paper_exam_question_units")


# image
class ImageExamTemplate(models.Model):
    # common fields
    company_id = models.ForeignKey(Company,related_name='company_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="Image_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="Image_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="Image_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(ImageSubject,related_name="mcq_subject_temnplate",null=True,on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=6) #two choices,random and custom
    total_question=models.IntegerField()
    basic_questions_count= models.IntegerField()
    intermediate_questions_count = models.IntegerField()
    advanced_questions_count = models.IntegerField()
    allow_negative_marking = models.BooleanField(default=True)
    #OPTIONAL  fields
    # total_question_count = models.IntegerField() can be calculated so not storing the total again
    marking_system = models.CharField(max_length=15,null=True)#two  choices category-wise or question-wise
    basic_question_marks = models.IntegerField(null=True)
    intermediate_question_marks = models.IntegerField(null=True)
    advanced_question_marks = models.IntegerField(null=True)
    question_wise_time = models.BooleanField(null=True)
    duration = models.CharField(max_length=10,null=True)
    negative_mark_percent = models.IntegerField(default=0)
    basic_questions = ManyToManyField(ImageQuestion,related_name="Image_exam_template_basic_questions")
    intermediate_questions = ManyToManyField(ImageQuestion,related_name="Image_exam_template_intermediate_questions")
    advanced_questions = ManyToManyField(ImageQuestion,related_name="Image_exam_template_advanced_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class ImageExamQuestionUnit(models.Model):
    question = models.ForeignKey(ImageQuestion,related_name="Image_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="Image_mcq_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class ImageQuestionPaper(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_ImageQuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_ImageQuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(ImageExamTemplate, related_name="Image_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(ImageExamQuestionUnit,related_name="Image_question_paper_exam_question_units")



# Audio/Video
class Audio_subject(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Audio_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Audio_subject',on_delete=models.CASCADE,null=True)
    subject_name = models.CharField(max_length=50)


class Audio(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Audio',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Audio',on_delete=models.CASCADE,null=True)
    subject = models.ForeignKey(Audio_subject, related_name='audio_subject', null=True,
                                on_delete=models.CASCADE)
    paragraph_description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)




class AudioExamTemplate(models.Model):
    # common fields
    company_id = models.ForeignKey(Company,related_name='company_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="Audio_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="Audio_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="Audio_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(Audio_subject,related_name="Audio_subject_temnplate",null=True,on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=6) #two choices,random and custom #update will be removed
    #OPTIONAL  fields
    total_question = models.IntegerField()
    question_wise_time = models.BooleanField(default=True)#will be removed
    total_exam_time = models.CharField(max_length= 9)
    is_video = models.BooleanField(default=False)
    audioquestions = ManyToManyField(Audio,related_name="Audio_exam_template_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class AudioExamQuestionUnit(models.Model):
    question = models.ForeignKey(Audio,related_name="Audio_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="Audio_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class AudioQuestionPaper(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_AudioQuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AudioQuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(AudioExamTemplate, related_name="Audio_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(AudioExamQuestionUnit,related_name="Audio_question_paper_exam_question_units")
    

class CandidateJobStagesStatus(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_CandidateJobStagesStatus',on_delete=models.CASCADE,null=True)
    candidate_id = models.ForeignKey(User, related_name='candidate_workflow_stages_status', on_delete=models.CASCADE,
                                   null=True)
    job_id = models.ForeignKey(JobCreation, related_name="StagesStatus_job_workflow_id", on_delete=models.CASCADE)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="StagesStatus_workflow_stage", on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="workflow_template_stage_status", on_delete=models.CASCADE,
                                 null=True)
    sequence_number = models.IntegerField()
    assessment_done = models.BooleanField(null=True,default=False)
    action_performed = models.BooleanField(null=True,default=False)
    status = models.IntegerField(default=0)
    reject_by_candidate = models.BooleanField(default=False, null=True)
    custom_stage_name = models.CharField(max_length=100,null=True)


class Collaboration(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_Collaboration',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Collaboration',on_delete=models.CASCADE,null=True)
    candidate_id = models.ForeignKey(User, related_name='candidate_colloboration_id', on_delete=models.CASCADE,
                                     null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_colloboration_id", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='user_colloboration_id', on_delete=models.CASCADE,
                                   null=True)
    comment = models.TextField()
    attachment = models.FileField(null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


class Employee(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    department = models.ForeignKey(Department,related_name="employee_department",on_delete=models.CASCADE)
    role = models.ForeignKey(Role,related_name='id_role',on_delete=models.CASCADE,null=True)
    contact_num = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    employee_id=models.ForeignKey(User,related_name='id_employee',on_delete=models.CASCADE,null=True)
    company_id = models.ForeignKey(Company,related_name='company_id_employee',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_employee',on_delete=models.CASCADE,null=True)
    profile_pic = models.ImageField(verbose_name="internal_user_pic", null=True)
    unique_id = models.CharField(unique=True,max_length=100,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


from agency.models import InternalCandidateBasicDetail,InternalUserProfile

# agency associate candidate


class AssociateCandidateAgency(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_AssociateCandidateAgency',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AssociateCandidateAgency',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_AssociateCandidateAgency_id", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='candidate_AssociateCandidateAgency_status', on_delete=models.CASCADE,
                                   null=True)
    agency_id = models.ForeignKey(Agency, related_name='candidate_Agency_id', on_delete=models.CASCADE,
                                   null=True)
    agency_internal_id = models.ForeignKey(InternalCandidateBasicDetail, related_name='candidateinternal_Agency_id', on_delete=models.CASCADE,
                                   null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


def resume_path_handler(instance, filename):
    #    file_extension = filename.split('.')
    path = '{}company{}/Candidate_Resume'.format(settings.MEDIA_ROOT, instance.company_id.id)
    if not os.path.exists(path):
        os.makedirs(path, mode=0o777)
    return '{}company{}/Candidate_Resume/{}'.format(settings.MEDIA_ROOT, instance.company_id.id,
                                                filename)


class CandidateTempDatabase(models.Model):
    candidate_id = models.ForeignKey(User, related_name="Candidateid_Candidatetempdatabase_company",
                                        on_delete=models.CASCADE, null=True)
    company_id = models.ForeignKey(Company,related_name='company_id_Candidatetempdatabases',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_Candidatetempdatabases',on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    resume = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    contact = models.CharField(max_length=20)
    designation = models.CharField(max_length=100)
    prefered_city = models.ManyToManyField(CandidateModels.City, related_name="Candidatetempdatabase_prefered_city",null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="Candidatetempdatabase_current_city",
                                        on_delete=models.CASCADE,null=True)
    notice = models.ForeignKey(CandidateModels.NoticePeriod, related_name="Candidatetempdatabase_notice_period",
                                on_delete=models.CASCADE,null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="Candidatetempdatabase_skill_id",null=True)
    ctc = models.CharField(max_length=100, null=True)
    expectedctc = models.CharField(max_length=100, null=True)
    total_exper = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(verbose_name="candidate_pf_pic_temp_db", null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)

class CandidateCategories(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_CandidateCategories',
                                   on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='create_user_id_CandidateCategories',
                                on_delete=models.CASCADE, null=True)
    category_name = models.TextField()
    def __str__(self):
        return str(self.category_name)
class Tags(models.Model):
    name=models.CharField(max_length=100)
    company=models.ForeignKey(Company,related_name="Tags_company",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='company_Tags_user',on_delete=models.CASCADE)


class InternalCandidateBasicDetails(models.Model):
    candidate_id = models.ForeignKey(User, related_name="Candidateid_InternalCandidateBasicDetail_company",
                                     on_delete=models.CASCADE, null=True)
    company_id = models.ForeignKey(Company,related_name='company_id_InternalCandidateBasicDetails',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_InternalCandidateBasicDetails',on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    resume = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    contact = models.CharField(max_length=20)
    designation = models.CharField(max_length=100)
    prefered_city = models.ManyToManyField(CandidateModels.City, related_name="add_internalcandidate_prefered_city",null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="add_internalcandidate_current_city",on_delete=models.CASCADE,null=True)
    notice = models.ForeignKey(CandidateModels.NoticePeriod, related_name="add_internalcandidate_applyjob_notice_period", on_delete=models.CASCADE,
                               null=True)
    source = models.ForeignKey(CandidateModels.Source, related_name="add_internalcandidate_source", on_delete=models.CASCADE,
                               null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="add_internalcandidate_skill_id",null=True)
    categories = models.ManyToManyField(CandidateCategories, related_name="add_internalcandidate_categories_id",null=True)
    tags = models.ManyToManyField(Tags, related_name="add_internalcandidate_tags_id",null=True)
    ctc = models.CharField(max_length=100, null=True)
    expectedctc = models.CharField(max_length=100, null=True)
    total_exper = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(verbose_name="candidate_pf_pic", null=True)
    withdraw_by_Candidate = models.BooleanField(default=False,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_InternalCandidateBasicDetails',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_InternalCandidateBasicDetails',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class InternalCandidateNotes(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidateBasicDetails, related_name="internal_candidate_notes_id", on_delete=models.CASCADE,
                                     null=True)
    note = models.TextField()
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    company_id = models.ForeignKey(Company, related_name='company_id_InternalCandidateNotes',
                                   on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='create_user_id_InternalCandidateNotes',
                                on_delete=models.CASCADE, null=True)


class AssociateCandidateInternal(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_AssociateCandidateInternal',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AssociateCandidateInternal',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="job_AssociateCandidateInternal_id", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='candidate_AssociateCandidateInternal_status', on_delete=models.CASCADE,
                                   null=True)
    internal_candidate_id = models.ForeignKey(InternalCandidateBasicDetails, related_name="companyinternal_candidate_AssociateJob_id", on_delete=models.CASCADE,
                                     null=True)


# INTERVIEW


class InterviewTemplate(models.Model):
    company_id = models.ForeignKey(Company, related_name='interview_company_id', null=True, on_delete=models.CASCADE)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="interview_creation_stage", null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TemplateCategory, related_name="interview_creation_category", null=True,
                                 on_delete=models.CASCADE)
    template = models.ForeignKey(Template_creation, related_name="interview_creation_temnplate", null=True,
                                 on_delete=models.CASCADE)
    interview_name = models.CharField(max_length=100)
    interview_type = models.CharField(max_length=100)
    user_id = models.ForeignKey(User,related_name='create_user_id_InterviewTemplate',on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='update_user_id_InterviewTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='delete_user_id_InterviewTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class InterviewScorecard(models.Model):
    interview_template = models.ForeignKey(InterviewTemplate, related_name='interview_template_id', null=True,
                                           on_delete=models.CASCADE)
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)


class InterviewSchedule(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_InterviewSchedule',on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='candidate_InterviewSchedule', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='InterviewSchedule_by_user', on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(JobCreation, related_name="InterviewSchedule_job_id", on_delete=models.CASCADE)
    template = models.ForeignKey(Template_creation, related_name="InterviewSchedule_template_id",on_delete=models.CASCADE)
    interview_template = models.ForeignKey(InterviewTemplate,related_name="interview_template_obj",on_delete=models.CASCADE,null=True)
    job_stages_id = models.ForeignKey(CandidateJobStagesStatus, related_name="InterviewSchedule_job_stages_id",on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="InterviewSchedule_participants_ids")
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    meridiem = models.CharField(max_length=10,null=True)
    interview_duration = models.CharField(max_length=100, null=True)
    is_accepted = models.BooleanField(null=True)
    interview_start_button_status = models.BooleanField(null=True,default=False)

    # scheduled=1 and not-scheduled=0
    status = models.IntegerField(null=True,default=0)

    reschedule_message = models.TextField(null=True)
    interview_link = models.TextField(null=True,unique=True)
    is_completed = models.BooleanField(default=False)


class OfferNegotiation(models.Model):
    designation = models.CharField(max_length=100,null=True)
    annual_ctc = models.TextField(null=True)
    notice_period = models.CharField(max_length=100,null=True)
    joining_date = models.DateField(null=True)
    other_details = models.TextField(null=True)
    from_company = models.BooleanField(null=True)
    action_performed = models.BooleanField(default=False)
    action_name = models.CharField(max_length=100,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


def job_offer_path_handler(instance, filename):
    path = '{}{}/{}/Stages/JOBOFFER'.format(settings.MEDIA_ROOT, instance.candidate_id.id, instance.job_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return '{}{}/{}/Stages/JOBOFFER/{}'.format(settings.MEDIA_ROOT, instance.candidate_id.id, instance.job_id, filename)


class JobOffer(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_JobOffer', on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='candidate_JobOffer', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='JobOffer_by_user', on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(JobCreation, related_name="JobOffer_job_id", on_delete=models.CASCADE)
    job_stages_id = models.ForeignKey(CandidateJobStagesStatus, related_name="JobOffer_job_stages_id",
                                      on_delete=models.CASCADE)
    candidate_name = models.TextField(null=True)
    bond = models.TextField(null=True)
    NDA = models.TextField(null=True)
    offer_letter = models.FileField(null=True, upload_to=job_offer_path_handler)
    is_accepted = models.BooleanField(default=False)
    rejected_by_candidate = models.BooleanField(default=False)
    negotiations = models.ManyToManyField(OfferNegotiation, related_name="JobOffer_participants_ids")
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


class CandidateJobStatus(models.Model):
    candidate_id = models.ForeignKey(User, related_name="candidate_JobStatus", on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="job_id_JobStatus",on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, related_name='company_id_JobStatus', on_delete=models.CASCADE)
    withdraw_by = models.ForeignKey(User, related_name='user_withdraw_JobStatus', on_delete=models.CASCADE,null=True)
    hire_by = models.ForeignKey(User, related_name='user_hired_JobStatus', on_delete=models.CASCADE,null=True)
    is_withdraw = models.BooleanField(default=False)
    is_hired = models.BooleanField(default=False)


class InterviewScorecardResult(models.Model):
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)


class InterviewResult(models.Model):
    candidate_id = models.ForeignKey(User, related_name="candidate_InterviewResult", on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="job_id_InterviewResult", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='InterviewResult_by_user', on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, related_name='company_id_InterviewResult', on_delete=models.CASCADE)
    interview_template = models.ForeignKey(InterviewTemplate,related_name='company_id_InterviewResult', on_delete=models.CASCADE)
    scorecard_results = models.ManyToManyField(InterviewScorecardResult, related_name="InterviewResult_scorecards",null=True)


# onthego change
class OnTheGoStages(models.Model):
    job_id = models.ForeignKey(JobCreation, related_name="job_id_OnTheGoStages", on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, related_name='company_id_OnTheGoStages', on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User, related_name='create_user_id_OnTheGoStages', on_delete=models.CASCADE,null=True)
    stage_name = models.CharField(max_length=100,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="on_the_go_stagelist_id", on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="on_the_go_template_id", on_delete=models.CASCADE, null=True)
    sequence_number = models.IntegerField()


class CustomTemplateScorecard(models.Model):
    title = models.TextField()


class CustomTemplate(models.Model):
    company_id = models.ForeignKey(Company, related_name='custom_company_id', null=True, on_delete=models.CASCADE)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="custom_creation_stage", null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TemplateCategory, related_name="custom_creation_category", null=True,
                                 on_delete=models.CASCADE)
    template = models.ForeignKey(Template_creation, related_name="custom_creation_temnplate", null=True,
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.TextField()
    enable_file_input = models.BooleanField(default=False)
    file_input = models.FileField(null=True)
    scorecards = models.ManyToManyField(CustomTemplateScorecard, related_name="customTemplate_scorecards",null=True)


class CustomScorecardResult(models.Model):
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)


class CustomResult(models.Model):
    candidate_id = models.ForeignKey(User, related_name="candidate_CustomResult", on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="job_id_CustomResult", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='CustomResult_by_user', on_delete=models.CASCADE,null=True)
    company_id = models.ForeignKey(Company, related_name='company_id_CustomResult', on_delete=models.CASCADE)
    custom_template = models.ForeignKey(CustomTemplate,related_name='CustomResult_template', on_delete=models.CASCADE)
    title = models.CharField(max_length=500,null=True)
    description = models.TextField(null=True)
    enable_file_input = models.BooleanField(default=False)
    enable_response = models.BooleanField(default=False)
    file_input = models.FileField(null=True)
    submitted_file_by_candidate = models.FileField(null=True)
    description_by_candidate = models.TextField(null=True)
    scorecard_results = models.ManyToManyField(CustomScorecardResult, related_name="CustomResult_scorecards",null=True)


class Tracker(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_Tracker', on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="job_id_Tracker", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='candidate_id_Tracker', on_delete=models.CASCADE)
    current_stage = models.ForeignKey(CandidateModels.Stage_list, related_name="current_stage_Tracker", on_delete=models.CASCADE,null=True)
    currentcompleted=models.BooleanField(default=False)
    next_stage=models.ForeignKey(CandidateModels.Stage_list, related_name="next_stage_Tracker", on_delete=models.CASCADE,null=True)
    action_required=models.CharField(max_length=100,null=True)
    reject=models.BooleanField(default=False)
    withdraw=models.BooleanField(default=False)
    hire=models.BooleanField(default=False)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)


class DailySubmission(models.Model):
    candidate_id=models.ForeignKey(User,related_name='daily_submission_candidate_id_company',on_delete=models.CASCADE,null=True)
    company_id=models.ForeignKey(Company,related_name="daily_submission_AssociateJob_company",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="daily_submissionAssociateJob_user_company", on_delete=models.CASCADE,
                                     null=True)
    internal_candidate_id_company = models.ForeignKey(InternalCandidateBasicDetails, related_name="daily_submissionJob_id_company", on_delete=models.CASCADE,
                                     null=True)
    internal_user_company=models.ForeignKey(Employee,related_name="daily_submissionuser_company",on_delete=models.CASCADE,null=True)
    company_job_id=models.ForeignKey(JobCreation,null=True,related_name="company_daily_submission_job_id_company",on_delete=models.CASCADE)
    job_type=models.CharField(max_length=10,null=True)
    agency_id=models.ForeignKey(Agency,null=True,related_name="daily_submission_AssociateJob_agency_company",on_delete=models.CASCADE)
    internal_candidate_id_agency = models.ForeignKey(InternalCandidateBasicDetail, related_name="daily_submissionJob_id_company", on_delete=models.CASCADE,
                                     null=True)
    internal_user_agency=models.ForeignKey(InternalUserProfile,related_name="daily_submissionuser_company",on_delete=models.CASCADE,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    applied=models.BooleanField(default=False)
    withdraw=models.BooleanField(default=False)
    candidate_custom_id=models.CharField(max_length=10,null=True)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    email=models.EmailField(null=True)
    gender = models.CharField(max_length=100,null=True)
    resume = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    secure_resume = models.BooleanField(default=False,null=True)
    secure_resume_file = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    contact = models.CharField(max_length=20,null=True)
    designation=models.CharField(max_length=100,null=True)
    prefered_city = models.ManyToManyField(CandidateModels.City,related_name="DailySubmission_prefered_city_company",null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="DailySubmission_current_city_company",on_delete=models.CASCADE,null=True)
    notice = models.ForeignKey(CandidateModels.NoticePeriod, related_name="DailySubmission_applyjob_notice_period_company", on_delete=models.CASCADE,
                               null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="DailySubmission_skill_id_company",null=True)
    source = models.ForeignKey(CandidateModels.Source, related_name="DailySubmission_source_company", on_delete=models.CASCADE,
                               null=True)
    categories = models.ManyToManyField(CandidateCategories, related_name="DailySubmission_categories_id_company",null=True)
    tags = models.ManyToManyField(Tags, related_name="DailySubmission_tags_id_company",null=True)
    ctc = models.CharField(max_length=100, null=True)
    expectedctc = models.CharField(max_length=100, null=True)
    total_exper = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(verbose_name="DailySubmission_pf_pic_company", null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    verify=models.BooleanField(default=False)
    verified=models.BooleanField(default=False)


class AppliedCandidate(models.Model):
    company_id = models.ForeignKey(Company,related_name='company_id_AppliedCandidate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_user_id_AppliedCandidate',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="applied_job_id", on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, related_name="applied_candidate_id", on_delete=models.CASCADE)
    dailysubmission=models.ForeignKey(DailySubmission,related_name='DailySubmission_id_AppliedCandidate',on_delete=models.CASCADE,null=True)
    submit_type=models.CharField(max_length=100,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)

class TaskCategories(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_TaskCategories',
                                   on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='create_user_id_TaskCategories',
                                on_delete=models.CASCADE, null=True)
    category_name = models.TextField()
    color = ColorField(default='#FF0000')
    def __str__(self):
        return str(self.category_name)


class TaskManagment(models.Model):
    company_id = models.ForeignKey(Company, related_name='company_id_TaskManagment',
                                   on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='create_user_id_TaskManagment',
                                on_delete=models.CASCADE, null=True)
    title=models.CharField(max_length=255)
    priority_id=models.ForeignKey(CandidateModels.Priority,related_name='Priority_TaskManagment',on_delete=models.CASCADE)
    description=models.TextField()
    category_id=models.ForeignKey(TaskCategories,related_name='category_TaskManagment',on_delete=models.CASCADE)
    job_id=models.ForeignKey(JobCreation,related_name='job_TaskManagment',on_delete=models.CASCADE,null=True)
    applied_candidate_id=models.ForeignKey(User,related_name='applied_candidate_TaskManagment',on_delete=models.CASCADE,null=True)
    internal_candidate_id=models.ForeignKey(InternalCandidateBasicDetails,related_name='internal_candidate_TaskManagment',on_delete=models.CASCADE,null=True)
    owner=models.ForeignKey(Employee,related_name="owner_TaskManagment",on_delete=models.CASCADE)
    assignee=models.ManyToManyField(Employee, related_name="Assignee_TaskManagment")
    due_date=models.DateField()
    status=models.ForeignKey(CandidateModels.TastStatus,related_name="owner_TaskManagment",on_delete=models.CASCADE)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    