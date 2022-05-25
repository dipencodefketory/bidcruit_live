
from django import template
from django.http import request
from django.utils.timezone import activate

register=template.Library()
# from Registration.models import Subject,lecture_duration,recess_duration,lectures_before_recess,starting_time
from candidate.models import *
from company.models import *
from accounts.models import User
import os
import datetime

import time
import calendar
from company.models import Company,Employee,TemplateCategory,AppliedCandidate,AssociateCandidateInternal,Audio,ImageQuestion,Descriptive,mcq_Question,InternalCandidateBasicDetails,JobCreation,CodingSubjectCategory,CodingQuestion,AssociateCandidateAgency
import math
from django.db.models import Count
from agency.models import AssociateJob,AgencyProfile,AgencyType,FreelancerProfile
@register.filter()
def get_education_title(value):
    # return "hello"
    month = {'January':1,
        'February':2,
        'March':3,
        'April':4,
        'May':5,
        'June':6,
        'July':7,
        'August':8,
        'September':9,
        'October':10,
        'November':11,
        'December':12
        }
    user = User.objects.get(id=value)
    profile=get_active_profile(user)
    if profile:
        education = CandidateEducation.objects.filter(candidate_id=user.id,profile_id=profile.profile_id)
        # return education
        print('================================================',education)
        if education:
            latest_education = education[0]
            start_month = month[latest_education.start_date.split(',')[0]]
            start_year = int(latest_education.start_date.split(',')[1])
            start_date = datetime.date(year=start_year,month=start_month,day = 1)
            
            end_month = month[latest_education.end_date.split(',')[0]]
            end_year = int(latest_education.end_date.split(',')[1])
            latest_end_date = datetime.date(year=end_year,month=end_month,day = 1)
            print("we are in the if zooooooooooooooone")
        else:
            latest_education=''
            print("=======> we are in the else zone")
            return ""
        count=1
        
        for i in education:
            if education:
                print("start dasasdaste",i.start_date)
                start_month = month[i.start_date.split(',')[0]]
                start_year = int(i.start_date.split(',')[1])
                start_date = datetime.date(year=start_year,month=start_month,day = 1)
                
                end_month = month[i.end_date.split(',')[0]]
                end_year = int(i.end_date.split(',')[1])
                end_date = datetime.date(year=end_year,month=end_month,day = 1)
                print("start date ",start_date)
                print("in for loop education",i)
                print("in for loop latest education",latest_education)
                if end_date > latest_end_date:
                    latest_education = i

                    # count+=1
                    # latest_education= i
                    # if i.end_date.split(',')[1] >latest_education.end_date.split(',')[1]:
                    #     latest_education = i
                    # elif i.end_date.split(',')[1] == latest_education.end_date.split(',')[1]:
                    #     if month[i.end_date.split(',')[0]] > month[latest_education.end_date.split(',')[0]]:
                    #         latest_education = i
                    # count+=1
                    # latest_education= i
       
            
        return latest_education.degree.name
    else:
        return None
        
@register.filter()
def get_latest_experience(value):
    month = {'January':1,
        'February':2,
        'March':3,
        'April':4,
        'May':5,
        'June':6,
        'July':7,
        'August':8,
        'September':9,
        'October':10,
        'November':11,
        'December':12
        }
    user = User.objects.get(id=value)
    experience = CandidateExperience.objects.filter(candidate_id=user.id)
    if experience:
        latest_experience = experience[0]
        latest_experiance_year=0
        latest_experiance_month=''
        if latest_experience.end_date=='present':
            latest_experiance_year=int(datetime.datetime.now().year)
            latest_experiance_month=datetime.datetime.now().strftime("%B")
        else:
            latest_experiance_year=int(latest_experience.end_date.split(',')[1])
            latest_experiance_month=latest_experience.end_date.split(',')[0]
        end_date_year=0
        end_date_month=''
        for i in experience:
            for x in range(len(i.end_date)):
                print(x,i.end_date[x])
            print("is present ?",i.end_date == 'present')
            print("length of date",len(i.end_date))
            if i.end_date=='present':
                end_date_year=int(datetime.datetime.now().year)
                end_date_month=datetime.datetime.now().strftime("%B")
            else:
                end_date_year=int(i.end_date.split(',')[1])
                end_date_month=i.end_date.split(',')[0]
            if  end_date_year >latest_experiance_year:
                latest_experience = i
            elif end_date_year == latest_experiance_year:
                print("end date mon",end_date_month)
                print("latest date mon",latest_experiance_month)
                if month[end_date_month] > month[latest_experiance_month]:
                    latest_experience = i
        return latest_experience.company.company_name
    else:
        return None
@register.filter()
def get_profile_url(value):
    user = User.objects.get(id=value)
    profile = CandidateProfile.objects.get(candidate_id=user.id)
    return profile.url_name

@register.filter()
def get_profile_picture(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    # print("IMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGE",active_profile.user_image)
    if active_profile:
        return active_profile.user_image
    else:
        print("error in get progfile pic")
        return None
@register.filter()
def get_contact_no(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.contact_no
    else:
        print('error in get contact no')
        return None
@register.filter()
def get_dob(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.dob
    else:
        print("error in get dob")
        return None
@register.filter()
def get_gender(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.gender.name
    else:
        print("error in get gender")
        return None
@register.filter()
def get_about_me(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.about_me
    else:
        print("error in get about me")
        return None
@register.filter()
def get_job_title(value):
    print("i ammm inside get job tiiiiiitle ",value)
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.designation
    else:
        return None
    # candidate_experience = CandidateExperience.objects.filter(candidate_id=user.id)
    # job_titles=''
    # for i in candidate_experience:
    #     job_titles += i.job_profile_name +','
    # return job_titles
    # return "placeholder job title"
@register.filter()
def get_preferred_job_locations(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        if active_profile.preferred_cities:
            preferred_cities_ids = active_profile.preferred_cities
            preferred_cities_ids = preferred_cities_ids.split(',')
            cities = []
            for i in preferred_cities_ids:
                city = City.objects.get(id=int(i))
                print("city",city)
                cities.append(city.city_name)
            print("final cities list",cities)
            if cities:
                return ','.join(cities)
            else:
                return ''
    else:
        return None
@register.filter()
def get_current_city(value):
    print("inside filter value ",value)
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.city.city_name
    else:
        return None

@register.filter()
def get_total_experience(value):
    user = User.objects.get(id=value)
    candidate_profile = get_active_profile(user)
    if candidate_profile:
        return candidate_profile.total_experience
    else:
        return None



@register.filter()
def get_current_salary(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.current_salary
    else:
        print("get_current salary error")
        return None
@register.filter()
def get_expected_salary_min(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.expected_salary_min
    else:
        print("error in excpected slary min")
        return None
@register.filter()
def get_notice_period(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    
    if active_profile:
        notice_period = NoticePeriod.objects.get(id=active_profile.notice_period.id)
        return notice_period.notice_period
    else:
        return None
@register.filter()
def get_view_counter(value):
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    view_count=CandidateCounter.objects.filter(candidate_id=value,profile_id=active_profile.profile_id).count()
    return view_count
def get_active_profile(current_user):
    print("inside get active profile",current_user.id)
    profiles = Profile.objects.filter(candidate_id=current_user)
    
    if profiles:
        for i in profiles:
            if i.active == True:
                print("teh active profile is ",i)
                if CandidateProfile.objects.filter(candidate_id=current_user,profile_id=i).exists():
                    candidate_profile = CandidateProfile.objects.get(profile_id=i)
                    return candidate_profile
                else:
                    return None
    else:
        return None
@register.filter()
def get_skills(value):
    user = User.objects.get(id=value)
    profile=Profile.objects.get(candidate_id=user,active=True)
    skills = CandidateSkillUserMap.objects.filter(candidate_id = user,profile_id = profile)
    skill_list = []
    for i in skills:
        if i.skill.name not in skill_list:
            skill_list.append(i.skill.name)
    return ','.join(skill_list)
@register.filter()
def get_fname_lname(value):
    user = User.objects.get(id=value)
    fname_lname = str(user.first_name)+ ' ' +str(user.last_name)
    return fname_lname

@register.filter()
def get_fname(value):
    user = User.objects.get(id=value)
    return user.first_name

@register.filter()
def get_lname(value):
    user = User.objects.get(id=value)
    return user.last_name


@register.filter()
def get_candidate_url(value):
    print("urllll fucntion was caleeeed",value)
    user = User.objects.get(id=value)
    active_profile = get_active_profile(user)
    if active_profile:
        return active_profile.url_name
    else:
        print("error in get candidate url")
        return None

@register.filter()
def get_dictonary_value(d,k):
    return d[k]
@register.filter()
def get_required_title(value):
    # print("type of value",type(value))
    if isinstance(value,CandidateExperience):
        return value.job_profile_name
    elif isinstance(value,CandidateEducation):
        return value.degree.name
    elif isinstance(value,CandidateCertificationAttachment):
        return value.name_of_certificate
    elif isinstance(value,CandidateAward):
        return value.title
    elif isinstance(value,CandidatePortfolio):
        return value.link
    elif isinstance(value,Gap):
        print("gap ofooooooooooooooooooooooound")
        return value.reason
@register.filter()
def get_required_title_giver(value):
    # print("type of value",type(value))
    if isinstance(value,CandidateExperience):
        print('=========================================00000000000000')
        return value.company.company_name
    elif isinstance(value,CandidateEducation):
        return value.university_board.name
    elif isinstance(value,CandidateCertificationAttachment):
        return value.institute_organisation
    elif isinstance(value,CandidateAward):
        return value.awarder
    elif isinstance(value,CandidatePortfolio):
        return value.project_title
    elif isinstance(value,Gap):
        print("gap ofooooooooooooooooooooooound")
        return value.type
@register.filter()
def get_circle_color(value):
    # print("type of value",type(value))
    if isinstance(value,CandidateExperience):
        return "yellow-bg"
    elif isinstance(value,CandidateEducation):
        return "pink-bg"
    elif isinstance(value,CandidateCertificationAttachment):
        return "purpal-bg"
    elif isinstance(value,CandidateAward):
        return "green-bg"
    elif isinstance(value,CandidatePortfolio):
        return "gigas-bg"
    elif isinstance(value,Gap):
        print("gap ofooooooooooooooooooooooound")
        return "drop-dot"
@register.filter()
def get_year_img(value):
    # print("type of value",type(value))
    if isinstance(value,CandidateExperience):
        return "/static/assets/img/curve-lable.png"
    elif isinstance(value,CandidateEducation):
        return "/static/assets/img/curve-lable-pink.png"
    elif isinstance(value,CandidateCertificationAttachment):
        return "/static/assets/img/curve-lable-perple.png"
    elif isinstance(value,CandidateAward):
        return "/static/assets/img/curve-lable-green.png"
    elif isinstance(value,CandidatePortfolio):
        return "/static/assets/img/curve-lable-blue.png"
    elif isinstance(value,Gap):
        print("gap ofooooooooooooooooooooooound")
        return "/static/assets/img/curve-lable-red.png"

@register.filter()
def check_blink(value):
    if isinstance(value,Gap):
        return "blinking"
@register.filter()
def get_file_name(value):
    print("valueeee",value)
    # name, extension = os.path.splitext(value.exp_document.name)
    value = value.name.split('/')
    return value[len(value)-1]
@register.filter()
def get_file_size(value):
    byte_size = value.size
    #value = ing(value)
    if byte_size < 512000:
        byte_size = byte_size / 1024.0
        ext = 'kb'
    elif byte_size < 4194304000:
        byte_size = byte_size / 1048576.0
        ext = 'mb'
    else:
        byte_size = byte_size / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(byte_size, 2)), ext)
# @register.filter()
# def get_count():
#     if request.session.get('count') == None:
#         request.session['count'] = 1
#         print("counter is ",request.session['count'])
#         return request.session['count']
#     request.session['count'] +=1
#     print("counter is ",request.session['count'])
#     return request.session['count']
# @register.filter()
# def get_count():
#     try:
#         del request.session['count']
#         return "deleted"
#     except:
#         return "erroror"



@register.filter()
def image_path_remove(value):
    value = value.replace("media/home/bidcruit/bidcruit/","")
    return value

@register.filter()
def to_str(value):
    return str(value)


@register.filter()
def get_candidate_image(value,profile):
    print(value,profile)
    logo = CandidateProfile.objects.get(candidate_id=int(value),profile_id=Profile.objects.get(id=int(profile)))
    print('=============',logo)
    return logo.user_image.url

@register.filter()
def get_candidatename(value):
    user = User.objects.get(id=value)
    candidatename = str(user.first_name)+' '+str(user.last_name)
    return candidatename


# for searching
@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()

@register.filter()
def get_candidat_counter(value):
    user = User.objects.get(id=value)
    # active_profile = ""
    profiles = Profile.objects.filter(candidate_id=user)
    for i in profiles:
        if i.active == True:
            # candidate_profile = CandidateProfile.objects.get(profile_id=i)
            active_profile = i
            break

    candidate_counter = CandidateCounter.objects.filter(candidate_id =user,profile_id = active_profile.id).count()
    # candidatename = str(user.first_name)+' '+str(user.last_name)
    return candidate_counter
import re
@register.filter()
def email_hide(value):
    p = re.compile("@(.*)")
    return '************@'+p.findall(value)[0]


@register.filter()
def title(value):
    return value.title()
    
@register.filter()
def get_latest_active_date(value):
    
    user = User.objects.get(id=value)
    print("mnop",user.last_login)
    print("mnop",type(user.last_login))
    last_login =user.last_login
    year = last_login.year
    month = last_login.month
    day = last_login.day    
    return calendar.month_name[int(month)] + ' ' + str(day) + ', ' + str(year)
    
@register.filter()
def is_shortlisted(value,login_user):
    user_id = User.objects.get(id=int(value))
    company_id = Company.objects.get(user_id=User.objects.get(id=login_user))
    if ShortlistedCandidates.objects.filter(candidate_id=user_id, company_id=company_id).exists():
        return True
    else:
        return False
    
@register.filter()
def get_timeline_li_color(value):
    if isinstance(value,CandidateExperience):
        return "cc-green"
    elif isinstance(value,CandidateEducation):
        return "cc-purple"
    elif isinstance(value,CandidateCertificationAttachment):
        return "cc-pink"
    elif isinstance(value,CandidateAward):
        return "cc-yellow"
    elif isinstance(value,Gap):
        return "cc-red"
       

@register.filter()
def get_timeline_start_date(value):
    if isinstance(value, CandidateExperience):
        return value.start_date
    elif isinstance(value, CandidateEducation):
        return value.start_date
    # elif isinstance(value, CandidateCertificationAttachment):
    #     return value.year
    # elif isinstance(value, CandidateAward):
    #     return value.start_date
    elif isinstance(value, Gap):
        return value.start_date


@register.filter()
def get_timeline_end_date(value):
    if isinstance(value, CandidateExperience):
        return value.end_date
    elif isinstance(value, CandidateEducation):
        return value.end_date
    # elif isinstance(value, CandidateCertificationAttachment):
    #     return value.year
    # elif isinstance(value, CandidateAward):
    #     return value.end_date
    elif isinstance(value, Gap):
        return value.end_date


@register.filter()
def category_count(stage_id,request):
    cat_count=TemplateCategory.objects.filter(stage=stage_id,company_id=Company.objects.get(user_id=request.user.id))
    print("=============",cat_count)
    # print(cat_count,"=========",len(cat_count))
    return len(cat_count)


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

from django.db.models import Count
@register.filter()
def total_applied_candidates(job_id):
    # result = AssociateJob.objects.filter(job_id=job_id).count()
    # print("=======",result)
    count = AppliedCandidate.objects.filter(job_id=job_id).count()
    return count


@register.filter()
def experiance_show(value):
    if value=='.':
        return '0 Year 0 Month'
    else:
        exp_value=value.split('.')
        if int(exp_value[0])>1 and int(exp_value[1])>1 :
            return exp_value[0]+' Years '+ exp_value[1] +' Months'
        elif int(exp_value[0])>1:
            return exp_value[0]+' Years '+ exp_value[1] +' Month'
        elif int(exp_value[1])>1:
            return exp_value[0]+' Year '+ exp_value[1] +' Months'
        elif int(exp_value[1])<=1 and int(exp_value[1])<=1:
            return exp_value[0]+' Year '+ exp_value[1] +' Month'

@register.filter()
def check_appliedcandidate(job_id,candidate_id):
    if AppliedCandidate.objects.filter(candidate_id=candidate_id,job_id=JobCreation.objects.get(id=job_id)).exists():
        return True
    elif AssociateCandidateAgency.objects.filter(candidate_id=candidate_id,job_id=JobCreation.objects.get(id=job_id)).exists():
        return True
    else:
        return False


# catagory_count
@register.filter()
def total_categories(sub_id):
    count = CodingSubjectCategory.objects.filter(subject_id=sub_id).count()
    return count


@register.filter()
def coding_total_questions(sub_id):
    categ = CodingSubjectCategory.objects.get(subject_id=sub_id)
    count = CodingQuestion.objects.filter(category_id=categ).count()
    return count


@register.filter()
def mcqtotal_categories(sub_id):
    count = mcq_Question.objects.filter(mcq_subject=sub_id).count()
    return count
@register.filter()
def descriptivetotal_categories(sub_id):
    count = Descriptive.objects.filter(subject=sub_id).count()
    return count
@register.filter()
def audiototal_categories(sub_id):
    count = Audio.objects.filter(subject=sub_id).count()
    return count
@register.filter()
def imagetotal_categories(sub_id):
    count = ImageQuestion.objects.filter(subject=sub_id).count()
    return count


@register.filter()
def total_question(cat_id):
    count = CodingQuestion.objects.filter(category_id=cat_id).count()
    return count


@register.filter()
def get_pre_requisite_id(template_creation_obj):
    pre_requisite = PreRequisites.objects.get(template=template_creation_obj)
    return pre_requisite.id


@register.filter()
def get_question_units(exam_paper):
    question_unit_list = {}

    print("\n\nn\n\n\n\exam paper",exam_paper.exam_question_units.all())
    if exam_paper.exam_template.question_wise_time or exam_paper.exam_template.marking_system == "question_wise":
        for i in exam_paper.exam_question_units.all():
            question_unit_list[i.question.id] = [i.question_mark,i.question_time]
    else:
        template = exam_paper.exam_template

        for i in template.basic_questions.all():
            question_unit_list[i.id] = [template.basic_question_marks,""]
        for i in template.intermediate_questions.all():
            question_unit_list[i.id] = [template.intermediate_question_marks,""]
        for i in template.advanced_questions.all():
            question_unit_list[i.id] = [template.advanced_question_marks,""]
    return question_unit_list

@register.filter()
def timing_system(exam_paper):
    return exam_paper.exam_template.question_wise_time

@register.filter()
def marking_system(exam_paper):
    return exam_paper.exam_template.marking_system

@register.filter()
def get_mcq_paper_id(template):
    exam_template = ExamTemplate.objects.get(template=template)
    return exam_template.id

@register.filter()
def get_descriptive_temp_id(template):
    print('\n\ntemplateeeeeeeeee', template)
    exam_template = DescriptiveExamTemplate.objects.get(template=template)
    print('exam_template', exam_template)
    return exam_template.id

@register.filter()
def get_image_temp_id(template):
    exam_template = ImageExamTemplate.objects.get(template=template)
    return exam_template.id

@register.filter()
def get_audio_temp_id(template):
    exam_template = AudioExamTemplate.objects.get(template=template)
    return exam_template.id

@register.filter()
def get_interview_temp_id(template):
    exam_template = InterviewTemplate.objects.get(template=template)
    return exam_template.id
@register.filter()
def get_descriptive_question_units(exam_paper):
    question_unit_list = {}

    print("\n\nn\n\n\n\exam paper",exam_paper.exam_question_units.all())
    if exam_paper.exam_template.question_wise_time:
        for i in exam_paper.exam_question_units.all():
            question_unit_list[i.question.id] = [i.question_mark,i.question_time]
    else:
        template = exam_paper.exam_template

        for i in template.basic_questions.all():
            question_unit_list[i.id] = [template.basic_question_marks,""]
        for i in template.intermediate_questions.all():
            question_unit_list[i.id] = [template.intermediate_question_marks,""]
        for i in template.advanced_questions.all():
            question_unit_list[i.id] = [template.advanced_question_marks,""]
    return question_unit_list


@register.filter()
def get_department(value,request):
    if Employee.objects.filter(employee_id=User.objects.get(id=value),company_id=Company.objects.get(user_id=request.user.id)).exists():
        dept=Employee.objects.get(employee_id=User.objects.get(id=value),company_id=Company.objects.get(user_id=request.user.id))
        print("=================asdasdadasd===",dept.department.name)
        return dept.department.name
    else:
        return None

@register.filter()
def nagative_marks(value,nagative_per):
    return value*nagative_per/100



@register.filter()
def total_exam_marks(template):
    print("template",template)
    basic_marks = template.basic_questions_count*template.basic_question_marks
    intermediate_marks = template.intermediate_questions_count*template.intermediate_question_marks
    advanced_marks = template.advanced_questions_count*template.advanced_question_marks
    return basic_marks + intermediate_marks +advanced_marks


@register.filter()
def agencyprofile(value,data):
    agency_type=AgencyType.objects.get(agency_id=value)
    if agency_type.is_agency:
        if AgencyProfile.objects.filter(agency_id=value).exists():
            get_profile=AgencyProfile.objects.get(agency_id=value)
            if data=='logo':
                if get_profile.agency_logo:
                    return get_profile.agency_logo.url
                else:
                    return None
            if data=='contact':
                if get_profile.contact_no:
                    return get_profile.contact_no
                else:
                    return 1234567890
        else:
            if data=='logo':
                return None
            if data=='contact':
                return 1234567890
    if agency_type.is_freelancer:
        if FreelancerProfile.objects.filter(agency_id=value).exists():
            get_profile=FreelancerProfile.objects.get(agency_id=value)
            if data=='logo':
                if get_profile.agency_logo:
                    return get_profile.agency_logo.url
                else:
                    return None
            if data=='contact':
                if get_profile.contact_no:
                    return get_profile.contact_no
                else:
                    return 1234567890
        else:
            if data=='logo':
                return None
            if data=='contact':
                return 1234567890


@register.filter()
def get_question_units(exam_paper):
    question_unit_list = {}
    print("\n\nn\n\n\n\exam paper",exam_paper.exam_question_units.all())
    if exam_paper.exam_template.question_wise_time or exam_paper.exam_template.marking_system == "question_wise":
        print("inside if")
        for i in exam_paper.exam_question_units.all():
            question_unit_list[i.question.id] = [i.question_mark,i.question_time]
    else:
        template = exam_paper.exam_template
        print("inside else")
        for i in template.basic_questions.all():
            question_unit_list[i.id] = [template.basic_question_marks,""]
        for i in template.intermediate_questions.all():
            question_unit_list[i.id] = [template.intermediate_question_marks,""]
        for i in template.advanced_questions.all():
            question_unit_list[i.id] = [template.advanced_question_marks,""]
    return question_unit_list


@register.filter()
def timing_system(exam_paper):
    return exam_paper.exam_template.question_wise_time


@register.filter()
def marking_system(exam_paper):
    return exam_paper.exam_template.marking_system

@register.filter()
def get_spaciility_split(spaciility):
    if spaciility:
        spaciilities = spaciility.split(',')
        return spaciilities
    else:
        return ''



@register.filter()
def get_experianceYear_split(exp):
    if exp:
        year = exp.split('.')[0]
        return year
    else:
        return 0

@register.filter()
def get_experianceMonth_split(exp):
    if exp:
        month = exp.split('.')[1]
        return month
    else:
        return 0



import pytz
from django.utils import timezone
from chat import models as ChatModels
@register.filter()
def convert_to_localtime(utctime):
    fmt = '%d/%m/%Y %H:%M'
    utc = utctime.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(timezone.get_current_timezone())
    return localtz.strftime(fmt)

@register.filter()
def get_company_image(value):
    logo = CompanyProfile.objects.get(company_id=int(value))
    return logo.company_logo.url

@register.filter()
def get_company_contact(value):
    logo = CompanyProfile.objects.get(company_id=int(value))
    return logo.contact_no1
@register.filter()
def get_company_industry(value):
    logo = CompanyProfile.objects.get(company_id=int(value))
    return logo.industry_type.name

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
    if delta.days >= 0:
        return str(delta.days)+' Days'
    else:
        return 'Close Job'
@register.filter()
def check_candidate_is_applied(id,job_id):
    if AppliedCandidate.objects.filter(candidate_id=id,job_id=JobCreation.objects.get(id=job_id)).exists():
        return True
    elif AssociateCandidateAgency.objects.filter(candidate_id=id,job_id=JobCreation.objects.get(id=job_id)).exists():
        return True
    else:
        return False
# @register.filter()
# def get_candidate_name(value):
#     logo = ChatModels.Member.objects.get(company_id=int(value))
#     return logo.company_logo.url

