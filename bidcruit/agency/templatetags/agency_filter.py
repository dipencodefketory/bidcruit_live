
from django import template
from django.utils.timezone import activate
register=template.Library()
# from Registration.models import Subject,lecture_duration,recess_duration,lectures_before_recess,starting_time
from candidate.models import *
from company.models import *
from accounts.models import User
import os
import datetime
import calendar
from agency import models as AgencyModels
import math
from django.db.models import Count
# @register.filter()
# def category_count(stage_id,request):
#     cat_count=TemplateCategory.objects.filter(stage=stage_id,agency_id=User.objects.get(id=request.user.id))
#     print("=============",cat_count)
#     # print(cat_count,"=========",len(cat_count))
#     return len(cat_count)



@register.filter()
def whenpublished(value):
    if value:
        now = timezone.now()
        diff= now - value
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds= diff.seconds
            if seconds == 1:
                return str(seconds) +  "second ago"
            else:
                return str(seconds) + " seconds ago"
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes= math.floor(diff.seconds/60)
            if minutes == 1:
                return str(minutes) + " minute ago"
            else:
                return str(minutes) + " minutes ago"
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours= math.floor(diff.seconds/3600)
            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days= diff.days
            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
        if diff.days >= 30 and diff.days < 365:
            months= math.floor(diff.days/30)
            if months == 1:
                return str(months) + " month ago"
            else:
                return str(months) + " months ago"
        if diff.days >= 365:
            years = math.floor(diff.days/365)
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"
    else:
        return ''



@register.filter()
def experiance_show(value):
    value=str(value)
    exp_value=value.split('.')
    if int(exp_value[0])>1 and int(exp_value[1])>1 :
        return exp_value[0]+' Years '+ exp_value[1] +' Months'
    elif int(exp_value[0])>1:
        return exp_value[0]+' Years '+ exp_value[1] +' Month'
    elif int(exp_value[1])>1:
        return exp_value[0]+' Year '+ exp_value[1] +' Months'
    else:
        return exp_value[0]+' Year '+ exp_value[1] +' Month'

@register.filter()
def get_file_name(value):
    print("valueeee",value)
    # name, extension = os.path.splitext(value.exp_document.name)
    value = value.name.split('/')
    return value[len(value)-1]
    
@register.filter()
def image_path_remove(value):
    value = value.replace("media/home/bidcruit/bidcruit/","")
    return value
@register.filter()
def get_file_name(file_path):
    file_name = file_path.split('/')[-1]
    return file_name

@register.filter()
def total_applied_candidates(jobid):
    result = AgencyModels.AssociateJob.objects.filter(job_id=jobid).count()
    return result
@register.filter()
def total_applied_candidates_internal(jobid):
    result = AgencyModels.AppliedCandidate.objects.filter(job_id=jobid).count()
    return result
 
@register.filter()
def check_appliedcandidate(job_id,candidate_id):
    get_applied=AgencyModels.AssociateJob.objects.filter(internal_candidate_id=InternalCandidateBasicDetail.objects.get(id=candidate_id),job_id=JobCreation.objects.get(id=job_id))
    if get_applied:
        return True
    else:
        return False


@register.filter()
def get_experianceYear_split(exp):
    if exp!='0':
        year = exp.split('.')
        if len(year)!=0:
            return year[0]
    else:
        return 0

@register.filter()
def get_experianceMonth_split(exp):
    if exp !='0':
        month = exp.split('.')
        if len(month)!=0:
            return month[1]
    else:
        return 0


@register.filter()
def get_spaciility_split(spaciility):
    if spaciility:
        spaciilities = spaciility.split(',')
        return spaciilities
    else:
        return ''

@register.filter()
def check_agency_type(agency_id):
    agency_type=AgencyModels.AgencyType.objects.get(agency_id=AgencyModels.Agency.objects.get(user_id=agency_id))
    if agency_type.is_agency:
        return True
    if agency_type.is_freelancer:
        return False


@register.filter()
def check_candidate_is_applied(id,job_id):
    if User.objects.filter(email=id).exists():
        if CompanyModels.AppliedCandidate.objects.filter(candidate_id=User.objects.get(email=id),job_id=JobCreation.objects.get(id=job_id)).exists():
            return True
        else:
            return False
    else:
        return False

@register.filter()
def internal_check_candidate_is_applied(id,job_id):
    if User.objects.filter(email=id).exists():
        if AgencyModels.AppliedCandidate.objects.filter(candidate_id=User.objects.get(email=id),job_id=AgencyModels.JobCreation.objects.get(id=job_id.id)).exists():
            return True
        else:
            return False
    else:
        return False


@register.filter()
def mcqtotal_categories(sub_id):
    count = AgencyModels.mcq_Question.objects.filter(mcq_subject=sub_id).count()
    return count

@register.filter()
def imagetotal_categories(sub_id):
    count = AgencyModels.ImageQuestion.objects.filter(subject=sub_id).count()
    return count

@register.filter()
def coding_total_questions(sub_id):
    categ = AgencyModels.CodingSubjectCategory.objects.get(subject_id=sub_id)
    count = AgencyModels.CodingQuestion.objects.filter(category_id=categ).count()
    return count

@register.filter()
def descriptivetotal_categories(sub_id):
    count = AgencyModels.Descriptive.objects.filter(subject=sub_id).count()
    return count


@register.filter()
def audiototal_categories(sub_id):
    count = AgencyModels.Audio.objects.filter(subject=sub_id).count()
    return count


@register.filter()
def category_count(stage_id,request):
    cat_count=AgencyModels.TemplateCategory.objects.filter(stage=stage_id,agency_id=AgencyModels.Agency.objects.get(user_id=request.user.id))
    print("=============",cat_count)
    # print(cat_count,"=========",len(cat_count))
    return len(cat_count)

@register.filter()
def get_pre_requisite_id(template_creation_obj):
    pre_requisite = AgencyModels.PreRequisites.objects.get(template=template_creation_obj)
    return pre_requisite.id

@register.filter()
def get_agency_image(value):
    agencytype=AgencyModels.AgencyType.objects.get(agency_id=int(value))
    if agencytype.is_freelancer:
        freelancer=AgencyModels.FreelancerProfile.objects.get(agency_id=int(value))
        return freelancer.agency_logo.url
    elif agencytype.is_agency:
        agencyprofile=AgencyModels.AgencyProfile.objects.get(agency_id=int(value))
        return agencyprofile.agency_logo.url
    
@register.filter()
def get_agency_industry(value):
    agencytype=AgencyModels.AgencyType.objects.get(agency_id=int(value))
    if agencytype.is_freelancer:
        freelancer=AgencyModels.FreelancerProfile.objects.get(agency_id=int(value))
        return ''
    elif agencytype.is_agency:
        agencyprofile=AgencyModels.AgencyProfile.objects.get(agency_id=int(value))
        return agencyprofile.industry_type.name
@register.filter()
def convert_to_lacs(value):
    lacs = int(value)/100000
    return lacs



@register.filter()
def closing_in(value):
    date_format = "%Y-%m-%d"
    a = datetime.datetime.strptime(str(datetime.datetime.now().date()), date_format)
    b = datetime.datetime.strptime(str(value), date_format)
    delta = b - a
    print(delta.days)
    return delta.days

@register.filter()
def company_profile(value,datatype):
    if CompanyModels.CompanyProfile.objects.filter(company_id=value).exists():
        companyprofile=CompanyModels.CompanyProfile.objects.get(company_id=value)
        if datatype=='logo':
            return companyprofile.company_logo.url
        if datatype=='contact':
            return companyprofile.contact_no1
    else:
        return None