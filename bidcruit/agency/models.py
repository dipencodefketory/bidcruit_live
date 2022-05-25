from django.db import models
from accounts.models import User
from candidate import models as CandidateModels
from company import models as CompanyModels
from tinymce.models import HTMLField
from bidcruit import settings
from django.db.models.fields.related import ForeignKey, ManyToManyField
import os
# Create your models here.

class Agency(models.Model):
    agency_id=models.ForeignKey(User, related_name="agency_adminid_Employee", on_delete=models.CASCADE,
                                     null=True)
    user_id=models.ManyToManyField(User, related_name="agencyuserid",
                                     null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Role(models.Model):
    name = models.CharField(max_length=20)
    system_generated = models.BooleanField(default=False)
    status=models.BooleanField(default=False)
    description=models.CharField(max_length=500,null=True)
    agency_id=models.ForeignKey(Agency,related_name="Role_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_Role',on_delete=models.CASCADE)
    def __str__(self):
        return (self.agency_id.agency_id.company_name)
class RolePermissions(models.Model):
    role=models.ForeignKey(Role,related_name="RolePermissions_agency",on_delete=models.CASCADE)
    system_generated = models.BooleanField(default=False)
    permission=models.ManyToManyField(CandidateModels.Permissions,related_name="RolePermissions_permissionagency")
    agency_id=models.ForeignKey(Agency,related_name="RolePermissions_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_RolePermissions',on_delete=models.CASCADE)
    def __str__(self):
        return (self.agency_id.agency_id.company_name+'  '+self.role.name)

class AgencyType(models.Model):
    agency_id = models.ForeignKey(Agency, related_name="agency_type", on_delete=models.CASCADE,
                                     null=True)
    is_freelancer = models.BooleanField(default=False)
    is_agency = models.BooleanField(default=False)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)



class Department(models.Model):
    name = models.CharField(max_length=20)
    system_generated = models.BooleanField(default=False)
    status=models.BooleanField(default=False)
    agency_id=models.ForeignKey(Agency,related_name="Department_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_Department',on_delete=models.CASCADE)

class CompanyAgencyConnection(models.Model):
    # connection_status_list = (("accept","Accept"),("accept","Accept"),("accept","Accept"))
    website=models.CharField(max_length=500,null=True)
    workemail=models.EmailField()
    client_name=models.CharField(max_length=500,null=True)
    company_name=models.CharField(max_length=500,null=True)
    contact_number=models.CharField(max_length=20,null=True)
    industry=models.ForeignKey(CandidateModels.IndustryType,related_name='client_industry',on_delete=models.CASCADE,null=True)
    address = models.CharField(max_length=2000,null=True)
    country = models.ForeignKey(CandidateModels.Country, related_name="client_country", on_delete=models.CASCADE, null=True)
    state = models.ForeignKey(CandidateModels.State, related_name="client_state", on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(CandidateModels.City, related_name="client_city", on_delete=models.CASCADE, null=True)
    company_id = models.ForeignKey(CompanyModels.Company,related_name="comp_agency_connect_comp",on_delete=models.CASCADE,null=True)
    commission_rate =  models.DecimalField(max_digits = 6,decimal_places = 2)
    contract_details = models.FileField(verbose_name="contract_details")
    payment_terms = models.ForeignKey(CandidateModels.PaymentTerms, related_name="client_payment_terms", on_delete=models.CASCADE, null=True)
    replacement_terms = models.ForeignKey(CandidateModels.ReplacementTerms, related_name="client_replacement_terms", on_delete=models.CASCADE, null=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)
    agency_id=models.ForeignKey(Agency,related_name="comp_agency_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_CompanyAgencyConnection',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class DomainExpertise(models.Model):
    name=models.CharField(max_length=500)

class AgencyProfile(models.Model):
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
    agency_type_choices=[
        ('Public Company','Public Company'),
        ('Educational','Educational'),
        ('Self Employed','Self Employed'),
        ('Government Agency','Government Agency'),
        ('Non Profit','Non Profit'),
        ('Self Owned','Self Owned'),
        ('Privately Held','Privately Held'),
        ('Partnership','Partnership')
        ]
    user_id = models.ForeignKey(User,related_name='agency_profile',on_delete=models.CASCADE)
    agency_profile_type = models.CharField(max_length=100,choices=agency_type_choices,null=True)
    agency_logo = models.ImageField(verbose_name="agency_logo_image")
    agency_bg = models.ImageField(verbose_name="agency_bg_image")
    industry_type = models.ForeignKey(CandidateModels.IndustryType, related_name="agency_industrytype", on_delete=models.CASCADE, null=True)
    domain_expertise=models.TextField()
    speciality = models.TextField()
    aboutus = models.TextField()
    address = models.CharField(max_length=1500)
    country = models.ForeignKey(CandidateModels.Country, related_name="agency_country", on_delete=models.CASCADE, null=True)
    state = models.ForeignKey(CandidateModels.State, related_name="agency_state", on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(CandidateModels.City, related_name="agency_city", on_delete=models.CASCADE, null=True)
    contact_email = models.CharField(max_length=500)
    contact_no = models.CharField(max_length=10)
    founded_year = models.CharField(max_length=5,null=True)
    employee_count = models.CharField(max_length=50,choices=employee_count_choices,null=True)
    agency_id=models.ForeignKey(Agency,related_name="agencyprofile_agency",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class FreelancerProfile(models.Model):
    user_id = models.ForeignKey(User,related_name='FreelancerProfile',on_delete=models.CASCADE)
    agency_logo = models.ImageField(verbose_name="FreelancerProfile_logo_image")
    agency_bg = models.ImageField(verbose_name="FreelancerProfile_bg_image")
    speciality = models.TextField()
    aboutus = models.TextField()
    gender = models.CharField(max_length=10)
    contact_no = models.CharField(max_length=10)
    country = models.ForeignKey(CandidateModels.Country, related_name="FreelancerProfile_country", on_delete=models.CASCADE,
                                null=True)
    state = models.ForeignKey(CandidateModels.State, related_name="FreelancerProfile_state", on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(CandidateModels.City, related_name="FreelancerProfile_city", on_delete=models.CASCADE, null=True)
    agency_id=models.ForeignKey(Agency,related_name="FreelancerProfile_agency",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class InternalUserProfile(models.Model):
    department=models.ForeignKey(Department,on_delete=models.CASCADE,related_name="internaluser_department",null=True)
    recruiter_type=models.ForeignKey(CandidateModels.RecruiterType,on_delete=models.CASCADE,related_name="internaluser_RecruiterType",null=True)
    role=models.ForeignKey(Role,on_delete=models.CASCADE,related_name="internaluser_role",null=True)
    contact_number=models.CharField(max_length=11,null=True)
    gender=models.CharField(max_length=100,null=True)
    branch=models.CharField(max_length=100,null=True)
    total_experiance=models.CharField(default=0.0,max_length=100,null=True)
    spaciility=models.TextField()
    aboutus=models.TextField()
    unique_id = models.CharField(unique=True,max_length=100,null=True)
    InternalUserid= models.ForeignKey(User,related_name="InternalUser_agency",on_delete=models.CASCADE)
    agency_id=models.ForeignKey(Agency,related_name="InternalUserProfile_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_InternalUserProfile',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class AssignJobInternal(models.Model):
    internal_user_id=models.ManyToManyField(InternalUserProfile, related_name="agency_AssignJobInternalUser",null=True)
    agency_id=models.ForeignKey(Agency,related_name="AssignJobInternal_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_AssignJobInternal',on_delete=models.CASCADE)
    job_id=models.ForeignKey(CompanyModels.JobCreation,related_name="assign_job_id",on_delete=models.CASCADE)                               
    created_at = models.DateTimeField(auto_now_add=True)


def resume_path_handler(instance, filename):
    #    file_extension = filename.split('.')
    path = '{}{}/Candidate_Resume'.format(settings.MEDIA_ROOT, instance.agency_id.id)
    if not os.path.exists(path):
        os.makedirs(path, mode=0o777)
    return '{}{}/Candidate_Resume/{}'.format(settings.MEDIA_ROOT, instance.agency_id.id,
                                                filename)
class CandidateCategories(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='agency_id_CandidateCategories',
                                   on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='agency_create_user_id_CandidateCategories',
                                on_delete=models.CASCADE, null=True)
    category_name = models.TextField()

class Tags(models.Model):
    name=models.CharField(max_length=100)
    agency_id=models.ForeignKey(Agency,related_name="Tags_agency",on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,related_name='agency_Tags_user',on_delete=models.CASCADE)

# add candidate
class InternalCandidateBasicDetail(models.Model):
    candidate_id=models.ForeignKey(User,related_name="Candidateid_InternalCandidateBasicDetail_agency",on_delete=models.CASCADE,null=True)
    agency_id=models.ForeignKey(Agency,related_name="InternalCandidateBasicDetail_agency",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="InternalCandidateBasicDetail_user", on_delete=models.CASCADE,
                                     null=True)
    candidate_custom_id=models.CharField(max_length=10)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email=models.EmailField()
    gender = models.CharField(max_length=100)
    resume = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    secure_resume = models.BooleanField(default=False)
    secure_resume_file = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    contact = models.CharField(max_length=20)
    designation=models.CharField(max_length=100)
    prefered_city = models.ManyToManyField(CandidateModels.City, related_name="InternalCandidateBasicDetail_prefered_city",null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="InternalCandidateBasicDetail_current_city",on_delete=models.CASCADE,null=True)
    notice = models.ForeignKey(CandidateModels.NoticePeriod, related_name="InternalCandidateBasicDetail_applyjob_notice_period", on_delete=models.CASCADE,
                               null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="InternalCandidateBasicDetail_skill_id",null=True)
    source = models.ForeignKey(CandidateModels.Source, related_name="InternalCandidateBasicDetail_source", on_delete=models.CASCADE,
                               null=True)
    categories = models.ManyToManyField(CandidateCategories, related_name="agency_add_internalcandidate_categories_id",null=True)
    tags = models.ManyToManyField(Tags, related_name="InternalCandidateBasicDetail_tags_id",null=True)
    ctc = models.CharField(max_length=100, null=True)
    expectedctc = models.CharField(max_length=100, null=True)
    total_exper = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(verbose_name="candidate_pf_pic", null=True)
    withdraw_by_Candidate = models.BooleanField(default=False,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    def filename(self):
        return os.path.basename(self.resume.name)
class CandidateTempDatabase(models.Model):
    ccandidate_id=models.ForeignKey(User,related_name="Candidateid_CandidateTempDatabase_agency",on_delete=models.CASCADE,null=True)
    agency_id=models.ForeignKey(Agency,related_name="CandidateTempDatabase_agency",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="CandidateTempDatabase_user", on_delete=models.CASCADE,
                                     null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    resume = models.FileField(max_length=500, null=True, upload_to=resume_path_handler)
    contact = models.CharField(max_length=20)
    designation = models.CharField(max_length=100)
    prefered_city = models.ManyToManyField(CandidateModels.City, related_name="Candidatetempdatabase_prefered_city_agency",null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="Candidatetempdatabase_current_city_agency",
                                        on_delete=models.CASCADE,null=True)
    notice = models.ForeignKey(CandidateModels.NoticePeriod, related_name="Candidatetempdatabase_notice_period_agency",
                                on_delete=models.CASCADE,null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="Candidatetempdatabase_skill_id_agency",null=True)
    ctc = models.CharField(max_length=100, null=True)
    expectedctc = models.CharField(max_length=100, null=True)
    total_exper = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(verbose_name="candidate_pf_pic_temp_db_agency", null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)

class InternalCandidateNotes(models.Model):
    internal_candidate_id = models.ForeignKey(InternalCandidateBasicDetail, related_name="internal_candidate_notes_id", on_delete=models.CASCADE,
                                     null=True)
    note = models.TextField()
    agency_id=models.ForeignKey(Agency,related_name="InternalCandidateBasicDetailNotes_agency",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="InternalCandidateBasicDetailNotes_user", on_delete=models.CASCADE,
                                     null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


# associate_job
class AssociateJob(models.Model):
    agency_id=models.ForeignKey(Agency,related_name="InternalCandidateBasicDetailAssociateJob_agency",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="InternalCandidateBasicDetailAssociateJob_user", on_delete=models.CASCADE,
                                     null=True)
    internal_candidate_id = models.ForeignKey(InternalCandidateBasicDetail, related_name="internal_candidate_AssociateJob_id", on_delete=models.CASCADE,
                                     null=True)
    internal_user=models.ForeignKey(InternalUserProfile,related_name="internaluserassociatuser",on_delete=models.CASCADE,null=True)
    job_id=models.ForeignKey(CompanyModels.JobCreation,related_name="AssociateJob_job_id",on_delete=models.CASCADE)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    applied=models.BooleanField(default=False)
# Job / workflow / question bank / template


class CandidateSecureData(models.Model):
    agency_id=models.ForeignKey(Agency,related_name="InternalCandidateCandidateSecureData_agency",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="InternalCandidateCandidateSecureData_user", on_delete=models.CASCADE,
                                     null=True)
    job_id = models.ForeignKey(CompanyModels.JobCreation, related_name="CandidateSecureData_job_id", on_delete=models.CASCADE)
    company_id = models.ForeignKey(CompanyModels.Company, related_name="CandidateSecureData_company",
                                   on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(User, related_name="Candidateid_CandidateSecureData_agency",
                                     on_delete=models.CASCADE, null=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_request = models.BooleanField(default=False)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200,null=True)






# MCQ


class MCQ_subject(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_MCQ_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_MCQ_subject',on_delete=models.CASCADE,null=True)
    subject_name=models.CharField(max_length=50)


class mcq_Question(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_mcq_Question',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_mcq_Question',on_delete=models.CASCADE,null=True)
    mcq_subject=models.ForeignKey(MCQ_subject, related_name="mcq_subject_id",on_delete=models.CASCADE)
    question_description = models.TextField()
    question_level = models.ForeignKey(CandidateModels.QuestionDifficultyLevel,related_name="agency_mcq_question_level",on_delete=models.CASCADE)
    correct_option = models.CharField(max_length=1)
    option_a = models.CharField(max_length=200,null=True)
    option_b = models.CharField(max_length=200,null=True)
    option_c = models.CharField(max_length=200,null=True)
    option_d = models.CharField(max_length=200,null=True)
    created_at = models.DateTimeField(auto_now_add=True)



# Image based


class ImageSubject(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_ImageSubject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_ImageSubject',on_delete=models.CASCADE,null=True)
    subject_name=models.CharField(max_length=50)


class ImageQuestion(models.Model):
    subject = models.ForeignKey(ImageSubject, related_name='agency_Image_subject', null=True, on_delete=models.CASCADE)
    question_level = models.ForeignKey(CandidateModels.QuestionDifficultyLevel,related_name="agency_image_question_level",on_delete=models.CASCADE)
    agency_id = models.ForeignKey(Agency,related_name='agency_id_ImageQuestion',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_ImageQuestion',on_delete=models.CASCADE,null=True)
    image_que_description=models.TextField()
    question_file = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ImageOption(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_ImageOption',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_ImageOption',on_delete=models.CASCADE,null=True)
    question_id = models.ForeignKey(ImageQuestion, related_name='agency_ImageQuestion_id', null=True, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(ImageSubject, related_name='agency_ImageSubject_id', null=True, on_delete=models.CASCADE)
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





#   coding

class CodingSubject(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CodingSubject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_CodingSubject',on_delete=models.CASCADE,null=True)
    api_subject_id = models.ForeignKey(CandidateModels.CodingApiSubjects, related_name='agency_coding_api_subject_id', null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, null=True)   # two types - frontend, backend


class CodingSubjectCategory(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CodingSubjectCategory',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_CodingSubjectCategory',on_delete=models.CASCADE,null=True)
    subject_id = models.ForeignKey(CodingSubject, related_name='coding_subject_id', null=True, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)


class CodingQuestion(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CodingQuestion',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_CodingQuestion',on_delete=models.CASCADE,null=True)
    category_id = models.ForeignKey(CodingSubjectCategory, related_name='agency_coding_category_id', null=True, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=50, null=True)
    coding_que_title = models.TextField()
    coding_que_description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)


# Descriptive
class Descriptive_subject(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Descriptive_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_Descriptive_subject',on_delete=models.CASCADE,null=True)
    subject_name = models.CharField(max_length=50)


class Descriptive(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Descriptive',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_Descriptive',on_delete=models.CASCADE,null=True)
    subject = models.ForeignKey(Descriptive_subject, related_name='agency_descriptive_subject', null=True,
                                on_delete=models.CASCADE)
    paragraph_description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)


# audio/video

# Audio/Video
class Audio_subject(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Audio_subject',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_Audio_subject',on_delete=models.CASCADE,null=True)
    subject_name = models.CharField(max_length=50)


class Audio(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Audio',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_Audio',on_delete=models.CASCADE,null=True)
    subject = models.ForeignKey(Audio_subject, related_name='agency_audio_subject', null=True,
                                on_delete=models.CASCADE)
    paragraph_description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)



# template

class TemplateCategory(models.Model):
    name = models.CharField(max_length=100)
    stage = models.ForeignKey(CandidateModels.Stage_list,related_name='agency_id_Template_stage',on_delete=models.CASCADE)
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Template',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_Template',on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True)


class Template_creation(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="Template_creation_agency_stage",on_delete=models.CASCADE)
    category = models.ForeignKey(TemplateCategory,related_name="Template_creation_category_agency",on_delete=models.CASCADE,null=True)
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Template_creation',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_id_Template_creation',on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True)
    status = models.BooleanField(default=False,null=True)
    created_by = models.CharField(max_length=10,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PreRequisites(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_PreRequisites',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='create_agency_user_id_PreRequisites',on_delete=models.CASCADE,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_prerequisites_creation_stage",on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(TemplateCategory,related_name="agency_prerequisites_creation_category",on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation,related_name="agency_prerequisites_creation_temnplate",on_delete=models.CASCADE,null=True)
    data = HTMLField()
    html_data = HTMLField()

# mcq template

class ExamTemplate(models.Model):
    # common fields
    agency_id = models.ForeignKey(Agency,related_name='agency_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_id_create_user_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="agency_id_mcq_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="agency_id_mcq_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="agency_id_mcq_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(MCQ_subject,related_name="agency_id_mcq_subject_temnplate",null=True,on_delete=models.CASCADE)
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
    basic_questions = ManyToManyField(mcq_Question,related_name="agency_id_exam_template_basic_questions")
    intermediate_questions = ManyToManyField(mcq_Question,related_name="agency_id_exam_template_intermediate_questions")
    advanced_questions = ManyToManyField(mcq_Question,related_name="agency_id_exam_template_advanced_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='agency_id_update_user_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='agency_id_delete_user_id_ExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class ExamQuestionUnit(models.Model):
    question = models.ForeignKey(mcq_Question,related_name="agency_id_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_id_mcq_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class QuestionPaper(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_QuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_id_create_user_id_QuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(ExamTemplate, related_name="agency_id_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(ExamQuestionUnit,related_name="agency_id_question_paper_exam_question_units")

# image template

# image
class ImageExamTemplate(models.Model):
    # common fields
    agency_id = models.ForeignKey(Agency,related_name='agency_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="agency_Image_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="agency_Image_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="agency_Image_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(ImageSubject,related_name="agency_mcq_subject_temnplate",null=True,on_delete=models.CASCADE)
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
    basic_questions = ManyToManyField(ImageQuestion,related_name="agency_Image_exam_template_basic_questions")
    intermediate_questions = ManyToManyField(ImageQuestion,related_name="agency_Image_exam_template_intermediate_questions")
    advanced_questions = ManyToManyField(ImageQuestion,related_name="agency_Image_exam_template_advanced_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='agency_update_user_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='agency_delete_user_id_ImageExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class ImageExamQuestionUnit(models.Model):
    question = models.ForeignKey(ImageQuestion,related_name="agency_Image_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_Image_mcq_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class ImageQuestionPaper(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_ImageQuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_ImageQuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(ImageExamTemplate, related_name="agency_Image_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(ImageExamQuestionUnit,related_name="agency_Image_question_paper_exam_question_units")


# descriptive Template


class DescriptiveExamTemplate(models.Model):
    # common fields
    agency_id = models.ForeignKey(Agency,related_name='agency_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="agency_Descriptive_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="agency_Descriptive_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="agency_Descriptive_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(Descriptive_subject,related_name="agency_Descriptive_subject_temnplate",null=True,on_delete=models.CASCADE)
    assignment_type = models.CharField(max_length=10,null=True) #two choices,random and custom
    #OPTIONAL  fields
    total_question = models.IntegerField()
    question_wise_time = models.BooleanField(default=True)
    descriptivequestions = ManyToManyField(Descriptive,related_name="agency_Descriptive_exam_template_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='agency_update_user_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='agency_delete_user_id_DescriptiveExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)



class DescriptiveExamQuestionUnit(models.Model):
    question = models.ForeignKey(Descriptive,related_name="agency_Descriptive_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_Descriptive_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class DescriptiveQuestionPaper(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_DescriptiveQuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_DescriptiveQuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(DescriptiveExamTemplate, related_name="agency_Descriptive_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(DescriptiveExamQuestionUnit,related_name="agency_Descriptive_question_paper_exam_question_units")

# audio/video template


class AudioExamTemplate(models.Model):
    # common fields
    agency_id = models.ForeignKey(Agency,related_name='agency_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    stage=models.ForeignKey(CandidateModels.Stage_list, related_name="agency_Audio_creation_stage",null=True,on_delete=models.CASCADE)
    category=models.ForeignKey(TemplateCategory,related_name="agency_Audio_creation_category",null=True,on_delete=models.CASCADE)
    template=models.ForeignKey(Template_creation,related_name="agency_Audio_creation_temnplate",null=True,on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(Audio_subject,related_name="agency_Audio_subject_temnplate",null=True,on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=6) #two choices,random and custom #update will be removed
    #OPTIONAL  fields
    total_question = models.IntegerField()
    question_wise_time = models.BooleanField(default=True)#will be removed
    total_exam_time = models.CharField(max_length= 9)
    is_video = models.BooleanField(default=False)
    audioquestions = ManyToManyField(Audio,related_name="agency_Audio_exam_template_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='agency_update_user_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='agency_delete_user_id_AudioExamTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class AudioExamQuestionUnit(models.Model):
    question = models.ForeignKey(Audio,related_name="agency_Audio_exam_question_unit_question",on_delete=models.CASCADE)
    question_mark = models.IntegerField(null=True)
    question_time = models.CharField(max_length=5,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_Audio_que_unit_temnplate", null=True,
                                 on_delete=models.CASCADE)


class AudioQuestionPaper(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_AudioQuestionPaper',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_AudioQuestionPaper',on_delete=models.CASCADE,null=True)
    exam_template = models.ForeignKey(AudioExamTemplate, related_name="agency_Audio_question_paper_exam_template",on_delete=models.CASCADE)
    exam_question_units = ManyToManyField(AudioExamQuestionUnit,related_name="agency_Audio_question_paper_exam_question_units")
    
# coding template

class CodingExamConfiguration(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    template_id = models.ForeignKey(Template_creation,related_name="agency_coding_config_template",on_delete=models.CASCADE)
    coding_subject_id = models.ForeignKey(CodingSubject, related_name='agency_exam_config_coding_subject_id', on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    total_time = models.CharField(max_length=50)
    total_question = models.CharField(max_length=50)
    assignment_type = models.CharField(max_length=50)
    exam_type = models.CharField(max_length=50)
    technology = models.CharField(max_length=50)
    coding_category_id =  models.ForeignKey(CodingSubjectCategory, related_name='agency_code_exam_config_category_id', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='agency_update_user_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='agency_delete_user_id_CodingExamConfiguration',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class CodingExamQuestions(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CodingExamQuestions',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_CodingExamQuestions',on_delete=models.CASCADE,null=True)
    coding_exam_config_id = models.ForeignKey(CodingExamConfiguration, related_name="cagency_oding_configuration_id",on_delete=models.CASCADE)
    question_id = models.ForeignKey(CodingQuestion, related_name="agency_coding_question_id", on_delete=models.CASCADE)
    marks = models.CharField(null=True, max_length=10)


#  if exam assignment type is rating this model will get used
class CodingScoreCard(models.Model):
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True,max_length=10)
    coding_exam_config_id = models.ForeignKey(CodingExamConfiguration, related_name="agency_coding_configuration_rating",
                                              on_delete=models.CASCADE)


# interview template

class InterviewTemplate(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='interview_agency_id', null=True, on_delete=models.CASCADE)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_interview_creation_stage", null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TemplateCategory, related_name="agency_interview_creation_category", null=True,
                                 on_delete=models.CASCADE)
    template = models.ForeignKey(Template_creation, related_name="agency_interview_creation_temnplate", null=True,
                                 on_delete=models.CASCADE)
    interview_name = models.CharField(max_length=100)
    interview_type = models.CharField(max_length=100)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_InterviewTemplate',on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User,related_name='agency_update_user_id_InterviewTemplate',on_delete=models.CASCADE,null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User,related_name='agency_delete_user_id_InterviewTemplate',on_delete=models.CASCADE,null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class InterviewScorecard(models.Model):
    interview_template = models.ForeignKey(InterviewTemplate, related_name='agency_interview_template_id', null=True,
                                           on_delete=models.CASCADE)
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)


# custom template

class CustomTemplateScorecard(models.Model):
    title = models.TextField()


class CustomTemplate(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='custom_agency_id', null=True, on_delete=models.CASCADE)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agencycustom_creation_stage", null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TemplateCategory, related_name="agencycustom_creation_category", null=True,
                                 on_delete=models.CASCADE)
    template = models.ForeignKey(Template_creation, related_name="agencycustom_creation_temnplate", null=True,
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.TextField()
    enable_file_input = models.BooleanField(default=False)
    file_input = models.FileField(null=True)
    scorecards = models.ManyToManyField(CustomTemplateScorecard, related_name="agencycustomTemplate_scorecards",null=True)

# job creation template

class JobCreationTemplate(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='agency_id_JobTemplate', on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name='agencycreate_user_id_JobTemplate', on_delete=models.CASCADE, null=True)
    job_title = models.CharField(max_length=100, null=True)
    job_type = models.ForeignKey(CandidateModels.JobTypes, related_name="agencyjob_template_type_id", on_delete=models.CASCADE)
    target_date = models.DateField()
    status = models.ForeignKey(CandidateModels.JobStatus, related_name="agencyjob_template_status_id",null=True, on_delete=models.CASCADE)
    industry_type = models.ForeignKey(CandidateModels.IndustryType, related_name="agencyjob_template_industry_type_id",
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
    jobshift = models.ManyToManyField(CandidateModels.JobShift, related_name="agencyjob_template_shift")
    required_skill = models.ManyToManyField(CandidateModels.Skill, related_name="agencyjob_template_required_skill",
                                            null=True)
    country = models.ForeignKey(CandidateModels.Country, related_name="agencyjob_template_country", on_delete=models.CASCADE)
    city = models.ForeignKey(CandidateModels.City, related_name="agencyjob_template_city", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name="agencyjob_template_department", on_delete=models.CASCADE,
                                   null=True)
    zip_code = models.CharField(max_length=10)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agencyjob_creation_stage", on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(TemplateCategory, related_name="agencyjob_creation_category", on_delete=models.CASCADE,
                                 null=True)
    template = models.ForeignKey(Template_creation, related_name="agencyjob_creation_temnplate", on_delete=models.CASCADE,
                                 null=True)
    created_by = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User, related_name='agencyupdate_user_id_JobCreationTemplates', on_delete=models.CASCADE,
                                  null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User, related_name='agencydelete_user_id_JobCreationTemplate', on_delete=models.CASCADE,
                                  null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)



# workflow

class Workflows(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Workflows',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_Workflows',on_delete=models.CASCADE,null=True)
    name = models.TextField()
    is_configured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_by = models.ForeignKey(User, related_name='agency_update_user_id_Workflows', on_delete=models.CASCADE,
                                  null=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    delete_by = models.ForeignKey(User, related_name='agency_delete_user_id_Workflows', on_delete=models.CASCADE,
                                  null=True)
    delete_at = models.DateTimeField(max_length=200, null=True)


class WorkflowStages(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_WorkflowStages',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_WorkflowStages',on_delete=models.CASCADE,null=True)
    stage_name = models.CharField(max_length=100)
    workflow = models.ForeignKey(Workflows, related_name="agency_workflow_id", on_delete=models.CASCADE,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_workflow_stage", on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(TemplateCategory, related_name="agency_workflow_category", on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_workflow_template",on_delete=models.CASCADE, null=True)
    sequence_number = models.IntegerField()
    display = models.BooleanField(default=True)


class WorkflowConfiguration(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_WorkflowConfiguration',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_WorkflowConfiguration',on_delete=models.CASCADE,null=True)
    workflow_stage = models.ForeignKey(WorkflowStages, related_name="agency_workflow_stage_id", on_delete=models.CASCADE)
    interviewer = models.ManyToManyField(User,related_name="agency_interview_name", null=True)
    is_automation = models.BooleanField(null=True)
    shortlist = models.FloatField(null=True)
    onhold = models.FloatField(null=True)
    reject = models.FloatField(null=True)


# job creation

class JobCreation(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_company_id_JobCreation',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_JobCreation',on_delete=models.CASCADE,null=True)
    job_title = models.CharField(max_length=100,null=True)
    job_type = models.ForeignKey(CandidateModels.JobTypes,related_name="agency_job_type_id",on_delete=models.CASCADE)
    contact_name = models.ForeignKey(User,related_name='agency_contact_person_id',on_delete=models.CASCADE,null=True)
    target_date = models.DateField()
    status = models.ForeignKey(CandidateModels.JobStatus,null=True,related_name="agency_job_status_id",on_delete=models.CASCADE)
    industry_type = models.ForeignKey(CandidateModels.IndustryType,related_name="agency_industry_type_id",on_delete=models.CASCADE, null=True)
    remote_job = models.BooleanField()
    salary_as_per_market=models.BooleanField(default=False)
    min_salary = models.CharField(max_length=10)
    max_salary = models.CharField(max_length=10)
    experience_year_min = models.CharField(max_length=10)
    experience_year_max = models.CharField(max_length=10)
    job_description = HTMLField()
    benefits = HTMLField(max_length=100)
    requirements = HTMLField(max_length=100)
    required_skill=models.ManyToManyField(CandidateModels.Skill,related_name="agency_required_skill_job",null=True)
    job_shift_id=models.ManyToManyField(CandidateModels.JobShift,related_name="agency_JobShift_job",null=True)
    country = models.ForeignKey(CandidateModels.Country,related_name="agency_job_country",on_delete=models.CASCADE)
    city = models.ForeignKey(CandidateModels.City,related_name="agency_job_city",on_delete=models.CASCADE)
    department = models.ForeignKey(Department,related_name="agency_job_department_id",on_delete=models.CASCADE, null=True)
    zip_code = models.CharField(max_length=10)
    job_owner = models.ForeignKey(User,related_name='agency_job_owner',on_delete=models.CASCADE,null=True)
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

class AgencyAssignJob(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CompanyAssignJob',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_CompanyAssignJob',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_assign_id", on_delete=models.CASCADE)
    recruiter_type_external=models.BooleanField(default=False)
    recruiter_type_internal=models.BooleanField(default=False)
    recruiter_id=models.ForeignKey(User,related_name='agency_create_user_id_recruiter_id',on_delete=models.CASCADE,null=True)



class AssignInternal(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_AssignInternal',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_AssignInternal',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_assigninternal_id", on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    recruiter_id = models.ForeignKey(User, related_name="agency_recruiter_job_assigninternal", on_delete=models.CASCADE, null=True)




class JobWorkflow(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_company_id_JobWorkflow',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_JobWorkflow',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_workflow_id", on_delete=models.CASCADE)
    onthego=models.BooleanField(default=False)
    withworkflow=models.BooleanField(default=False)
    is_application_review = models.BooleanField(default=False)
    workflow_id = models.ForeignKey(Workflows, null=True, related_name="agency_job_workflow_id", on_delete=models.CASCADE)



# onthego change
class OnTheGoStages(models.Model):
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_id_OnTheGoStages", on_delete=models.CASCADE)
    agency_id = models.ForeignKey(Agency, related_name='agency_id_OnTheGoStages', on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User, related_name='agency_create_user_id_OnTheGoStages', on_delete=models.CASCADE,null=True)
    stage_name = models.CharField(max_length=100,null=True)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_on_the_go_stagelist_id", on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_on_the_go_template_id", on_delete=models.CASCADE, null=True)
    sequence_number = models.IntegerField()




class AppliedCandidate(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_AppliedCandidate',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_AppliedCandidate',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_applied_job_id", on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, related_name="agency_applied_candidate_id", on_delete=models.CASCADE)
    submit_type=models.CharField(max_length=100,null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


class AssociateCandidateInternal(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_AssociateCandidateInternal',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_AssociateCandidateInternal',on_delete=models.CASCADE,null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_AssociateCandidateInternal_id", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='agency_candidate_AssociateCandidateInternal_status', on_delete=models.CASCADE,
                                   null=True)
    internal_candidate_id = models.ForeignKey(InternalCandidateBasicDetail, related_name="agency_companyinternal_candidate_AssociateJob_id", on_delete=models.CASCADE,
                                     null=True)



class CandidateJobStagesStatus(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_CandidateJobStagesStatus',on_delete=models.CASCADE,null=True)
    candidate_id = models.ForeignKey(User, related_name='agency_candidate_workflow_stages_status', on_delete=models.CASCADE,
                                   null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_StagesStatus_job_workflow_id", on_delete=models.CASCADE)
    stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_StagesStatus_workflow_stage", on_delete=models.CASCADE,null=True)
    template = models.ForeignKey(Template_creation, related_name="agency_workflow_template_stage_status", on_delete=models.CASCADE,
                                 null=True)
    sequence_number = models.IntegerField()
    assessment_done = models.BooleanField(null=True,default=False)
    action_performed = models.BooleanField(null=True,default=False)
    status = models.IntegerField(default=0)
    reject_by_candidate = models.BooleanField(default=False, null=True)
    custom_stage_name = models.CharField(max_length=100,null=True)

class Tracker(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='agency_id_Tracker', on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_id_Tracker", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='agency_candidate_id_Tracker', on_delete=models.CASCADE)
    current_stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_current_stage_Tracker", on_delete=models.CASCADE,null=True)
    currentcompleted=models.BooleanField(default=False)
    next_stage=models.ForeignKey(CandidateModels.Stage_list, related_name="agency_next_stage_Tracker", on_delete=models.CASCADE,null=True)
    action_required=models.CharField(max_length=100,null=True)
    reject=models.BooleanField(default=False)
    withdraw=models.BooleanField(default=False)
    hire=models.BooleanField(default=False)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)





class InterviewScorecard(models.Model):
    interview_template = models.ForeignKey(InterviewTemplate, related_name='interview_template_id', null=True,
                                           on_delete=models.CASCADE)
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)


class InterviewSchedule(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='agency_id_InterviewSchedule',on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='agencycandidate_InterviewSchedule', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='agencyInterviewSchedule_by_user', on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agencyInterviewSchedule_job_id", on_delete=models.CASCADE)
    template = models.ForeignKey(Template_creation, related_name="agencyInterviewSchedule_template_id",on_delete=models.CASCADE)
    interview_template = models.ForeignKey(InterviewTemplate,related_name="agencyinterview_template_obj",on_delete=models.CASCADE,null=True)
    job_stages_id = models.ForeignKey(CandidateJobStagesStatus, related_name="agencyInterviewSchedule_job_stages_id",on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="agencyInterviewSchedule_participants_ids")
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
    agency_id = models.ForeignKey(Agency, related_name='agency_id_JobOffer', on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='agencycandidate_JobOffer', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='agencyJobOffer_by_user', on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agencyJobOffer_job_id", on_delete=models.CASCADE)
    job_stages_id = models.ForeignKey(CandidateJobStagesStatus, related_name="agencyJobOffer_job_stages_id",
                                      on_delete=models.CASCADE)
    candidate_name = models.TextField(null=True)
    bond = models.TextField(null=True)
    NDA = models.TextField(null=True)
    offer_letter = models.FileField(null=True, upload_to=job_offer_path_handler)
    is_accepted = models.BooleanField(default=False)
    rejected_by_candidate = models.BooleanField(default=False)
    negotiations = models.ManyToManyField(OfferNegotiation, related_name="agencyJobOffer_participants_ids")
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


class CandidateJobStatus(models.Model):
    candidate_id = models.ForeignKey(User, related_name="agencycandidate_JobStatus", on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="agencyjob_id_JobStatus",on_delete=models.CASCADE)
    agency_id = models.ForeignKey(Agency, related_name='agency_id_JobStatus', on_delete=models.CASCADE)
    withdraw_by = models.ForeignKey(User, related_name='agencyuser_withdraw_JobStatus', on_delete=models.CASCADE,null=True)
    hire_by = models.ForeignKey(User, related_name='agencyuser_hired_JobStatus', on_delete=models.CASCADE,null=True)
    is_withdraw = models.BooleanField(default=False)
    is_hired = models.BooleanField(default=False)


class InterviewScorecardResult(models.Model):
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)


class InterviewResult(models.Model):
    candidate_id = models.ForeignKey(User, related_name="agencycandidate_InterviewResult", on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="agencyjob_id_InterviewResult", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='agencyInterviewResult_by_user', on_delete=models.CASCADE)
    agency_id = models.ForeignKey(Agency, related_name='agency_id_InterviewResult', on_delete=models.CASCADE)
    interview_template = models.ForeignKey(InterviewTemplate,related_name='agency_id_InterviewResult', on_delete=models.CASCADE)
    scorecard_results = models.ManyToManyField(InterviewScorecardResult, related_name="agencyInterviewResult_scorecards",null=True)



class Collaboration(models.Model):
    agency_id = models.ForeignKey(Agency,related_name='agency_id_Collaboration',on_delete=models.CASCADE,null=True)
    user_id = models.ForeignKey(User,related_name='agency_create_user_id_Collaboration',on_delete=models.CASCADE,null=True)
    candidate_id = models.ForeignKey(User, related_name='agency_candidate_colloboration_id', on_delete=models.CASCADE,
                                     null=True)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_colloboration_id", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='agency_user_colloboration_id', on_delete=models.CASCADE,
                                   null=True)
    comment = models.TextField()
    attachment = models.FileField(null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)


class CustomScorecardResult(models.Model):
    title = models.TextField()
    comment = models.TextField(null=True)
    rating = models.CharField(null=True, max_length=10)



class CustomResult(models.Model):
    candidate_id = models.ForeignKey(User, related_name="agency_candidate_CustomResult", on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_id_CustomResult", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='agency_CustomResult_by_user', on_delete=models.CASCADE,null=True)
    agency_id = models.ForeignKey(Agency, related_name='agency_id_CustomResult', on_delete=models.CASCADE)
    custom_template = models.ForeignKey(CustomTemplate,related_name='agency_CustomResult_template', on_delete=models.CASCADE)
    scorecard_results = models.ManyToManyField(CustomScorecardResult, related_name="agency_CustomResult_scorecards",null=True)
    submitted_file_by_candidate = models.FileField(null=True)
    description_by_candidate = models.TextField(null=True)
    description = models.TextField(null=True)

class Tracker(models.Model):
    agency_id = models.ForeignKey(Agency, related_name='agency_id_Tracker', on_delete=models.CASCADE)
    job_id = models.ForeignKey(JobCreation, related_name="agency_job_id_Tracker", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(User, related_name='agency_candidate_id_Tracker', on_delete=models.CASCADE)
    current_stage = models.ForeignKey(CandidateModels.Stage_list, related_name="agency_current_stage_Tracker", on_delete=models.CASCADE,null=True)
    currentcompleted=models.BooleanField(default=False)
    next_stage=models.ForeignKey(CandidateModels.Stage_list, related_name="agency_next_stage_Tracker", on_delete=models.CASCADE,null=True)
    action_required=models.CharField(max_length=100,null=True)
    reject=models.BooleanField(default=False)
    withdraw=models.BooleanField(default=False)
    hire=models.BooleanField(default=False)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)


class DailySubmission(models.Model):
    candidate_id=models.ForeignKey(User,related_name='daily_submission_candidate_id_agency',on_delete=models.CASCADE,null=True)
    agency_id=models.ForeignKey(Agency,related_name="daily_submission_AssociateJob_agency",on_delete=models.CASCADE)
    user_id=models.ForeignKey(User, related_name="daily_submissionAssociateJob_user", on_delete=models.CASCADE,
                                     null=True)
    internal_candidate_id = models.ForeignKey(InternalCandidateBasicDetail, related_name="daily_submissionJob_id", on_delete=models.CASCADE,
                                     null=True)
    internal_user=models.ForeignKey(InternalUserProfile,related_name="daily_submissionuser",on_delete=models.CASCADE,null=True)
    company_job_id=models.ForeignKey(CompanyModels.JobCreation,null=True,related_name="company_daily_submission_job_id",on_delete=models.CASCADE)
    agency_job_id=models.ForeignKey(JobCreation,null=True,related_name="agency_daily_submission_job_id",on_delete=models.CASCADE)
    job_type=models.CharField(max_length=10,null=True)
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
    prefered_city = models.ManyToManyField(CandidateModels.City,related_name="DailySubmission_prefered_city",null=True)
    current_city = models.ForeignKey(CandidateModels.City, related_name="DailySubmission_current_city",on_delete=models.CASCADE,null=True)
    notice = models.ForeignKey(CandidateModels.NoticePeriod, related_name="DailySubmission_applyjob_notice_period", on_delete=models.CASCADE,
                               null=True)
    skills = models.ManyToManyField(CandidateModels.Skill, related_name="DailySubmission_skill_id",null=True)
    source = models.ForeignKey(CandidateModels.Source, related_name="DailySubmission_source", on_delete=models.CASCADE,
                               null=True)
    categories = models.ManyToManyField(CandidateCategories, related_name="DailySubmission_categories_id",null=True)
    tags = models.ManyToManyField(Tags, related_name="DailySubmission_tags_id",null=True)
    ctc = models.CharField(max_length=100, null=True)
    expectedctc = models.CharField(max_length=100, null=True)
    total_exper = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(verbose_name="DailySubmission_pf_pic", null=True)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)
    update_at = models.DateTimeField(max_length=200, null=True)
    verify=models.BooleanField(default=False)
    verified=models.BooleanField(default=False)