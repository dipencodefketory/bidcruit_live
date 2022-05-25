from django.db.models.signals import post_save,post_delete,post_init
from django.dispatch import receiver
from candidate.models import CandidateExperience, CandidateProfile, CandidateSkillUserMap,CandidateSocialNetwork,CandidateExpDocuments,CandidatePortfolio,CandidateEducation,CandidateCertificationAttachment, Skill, candidate_job_apply_detail
import os
import shutil
from accounts.models import User
from bidcruit.settings import MEDIA_ROOT
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Q
from company .documents import CandidateDocument
from . import models
from company import models as CompanyModels
# @receiver(post_save, sender=CandidateSocialNetwork)
# def index_post(sender, instance, **kwargs):
#     # print("indexing was called")
#     # id = instance.candidate_id.id
#     # user = User.objects.get(id=id)
#     # user.indexing()
#     registry.update(instance.docs)



@receiver(post_save, sender=User)
def create_user_folder(sender, instance, **kwargs):
    path = '{}{}'.format(MEDIA_ROOT,instance.id)
    print('========',path)
    path1 = path +"/Candidate_Profile"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        path1 = path +"/Candidate_Profile"
        path2 = path +"/Candidate_Education"
        path3 = path +"/Candidate_Experience"
        path4 = path +"/Candidate_Certificate"
        path5 = path +"/Candidate_Portfolio"
        path6 = path +"/Candidate_Awards"
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
        os.mkdir(path3, mode=0o777)
        os.mkdir(path4, mode=0o777)
        os.mkdir(path5, mode=0o777)
        os.mkdir(path6, mode=0o777)

@receiver(post_save, sender=CandidateEducation)
@receiver(post_save, sender=CandidateExperience)
@receiver(post_save, sender=CandidateProfile)
@receiver(post_save, sender=CandidateSkillUserMap)
def update_elastic_docs(sender, instance, **kwargs):
    print("asdasdasdasasdasdasdasxzcxzcxz")

    # print("all_docs",instance.candidate_id.docs)
    q = Q('multi_match',query=instance.candidate_id.email,fields=['email'])
    s= CandidateDocument.search().query(q).extra(size=10000)
    for hit in s:
        print("emaioil",hit.email)
        if User.objects.filter(email= hit.email).exists():
            user = User.objects.get(email=hit.email)
            try:
                hit.delete()
                user.indexing()
            except:
                print("indexing was not called ")


@receiver(post_delete, sender=CandidateExpDocuments)
def delete_exp_folder(sender, instance, **kwargs):
    path = '{}{}/Candidate_Experience/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.candidate_exp_id.company.company_name)
    try:
        os.rmdir(path)
    except:
        print("the folder is not empty")


@receiver(post_delete, sender=CandidatePortfolio)
def delete_portfolio_folder(sender, instance, **kwargs):
    print("wooooooooooooooooooooooooooooooo yeaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaah")
    path = '{}{}/Candidate_Portfolio/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.project_title)
    try:
        shutil.rmtree(path)
    except:
        print("post delete portoflio error")




@receiver(post_delete, sender=CandidateEducation)
def delete_edu_folder(sender, instance, **kwargs):
    path = '{}{}/Candidate_Education/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.degree.name)
    try:
        shutil.rmtree(path)
    except:
        print("educationpost delete delete signal error")


@receiver(post_delete, sender=CandidateCertificationAttachment)
def delete_certificate_folder(sender, instance, **kwargs):
    path = '{}{}/Candidate_Certificate/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.name_of_certificate)
    try:
        shutil.rmtree(path)
    except:
        print("error during the candidate certification poist de;ete signal")

@receiver(post_delete, sender=candidate_job_apply_detail)
def delete_resume_folder(sender, instance, **kwargs):
    path = '{}{}/Candidate_Resume/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.resume)
    try:
        shutil.rmtree(path)
    except:
        print("error during the candidate resume poist de;ete signal")


@receiver(post_save, sender=models.JcrRatio)
def create_user_jcr(sender, instance, **kwargs):
    path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
    print('========',path)
    path1 = path +"/Stages"
    path2 = path + "/Stages/JCR"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path1):
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path2):
        os.mkdir(path2, mode=0o777)

@receiver(post_save, sender=models.PreRequisitesFill)
def create_user_PreRequisitesFill(sender, instance, **kwargs):
    path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
    print('========',path)
    path1 = path + "/Stages"
    path2 = path +"/Stages/PreRequisites"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path1):
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path2):
        os.mkdir(path2, mode=0o777)



@receiver(post_save, sender=models.Mcq_Exam_result)
def create_user_Mcq_Exam_result(sender, instance, **kwargs):
    path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
    print('========',path)
    path1 = path + "/Stages"
    path2 = path +"/Stages/MCQ"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path1):
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path2):
        os.mkdir(path2, mode=0o777)



@receiver(post_save, sender=models.Descriptive_Exam_result)
def create_user_Descriptive_Exam_result(sender, instance, **kwargs):
    path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
    print('========',path)
    path1 = path + "/Stages"
    path2 = path +"/Stages/Descriptive"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path1):
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path2):
        os.mkdir(path2, mode=0o777)



@receiver(post_save, sender=models.Image_Exam_result)
def create_user_Image_Exam_result(sender, instance, **kwargs):
    path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
    print('========',path)
    path1 = path + "/Stages"
    path2 = path +"/Stages/Image"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path1):
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path2):
        os.mkdir(path2, mode=0o777)


@receiver(post_save, sender=models.Coding_Exam_result)
def create_user_Coding_Exam_result(sender, instance, **kwargs):
    path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
    print('========',path)
    path1 = path + "/Stages"
    path2 = path +"/Stages/Coding"
    if not os.path.exists(path):
        os.mkdir(path, mode=0o777)
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path1):
        os.mkdir(path1, mode=0o777)
        os.mkdir(path2, mode=0o777)
    elif not os.path.exists(path2):
        os.mkdir(path2, mode=0o777)
#
# @receiver(post_save, sender=CompanyModels.JobOffer)
# def create_user_JobOffer(sender, instance, **kwargs):
#     path = '{}{}/{}'.format(MEDIA_ROOT,instance.candidate_id.id,instance.job_id)
#     path1 = path + "/Stages"
#     path2 = path +"/Stages/JOBOFFER"
#     if not os.path.exists(path):
#         os.mkdir(path, mode=0o777)
#         os.mkdir(path1, mode=0o777)
#         os.mkdir(path2, mode=0o777)
#     elif not os.path.exists(path1):
#         os.mkdir(path1, mode=0o777)
#         os.mkdir(path2, mode=0o777)
#     elif not os.path.exists(path2):
#         os.mkdir(path2, mode=0o777)
