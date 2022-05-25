import os
import shutil
from django.contrib.auth.forms import PasswordResetForm
from bidcruit import settings
import re
from elasticsearch_dsl import Q as Elastic_Q
from company.documents import CandidateDocument
import json
import random
import string
from datetime import datetime
from dateutil.relativedelta import relativedelta
import datetime
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from accounts.tokens import account_activation_token
from django.core.mail import EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from . import models
import pyotp
import re
from accounts.views import activate_account_confirmation
import socket
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, request
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from .utils.charts import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.utils import timezone
from django.utils.timezone import localdate

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from notifications.signals import notify
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
import pyqrcode
from company.models import CandidateHire, CompanyProfile, JCR, JobCreation, Workflows,WorkflowConfiguration,JobWorkflow, \
    WorkflowStages, PreRequisites, Template_creation, ExamQuestionUnit, ExamTemplate, QuestionPaper, ExamQuestionUnit, \
    mcq_Question,CodingExamConfiguration,CodingExamQuestions,Descriptive_subject,Descriptive,CodingScoreCard,\
    DescriptiveExamTemplate,DescriptiveExamQuestionUnit,DescriptiveQuestionPaper,ImageSubject,ImageQuestion,ImageOption,\
    ImageExamTemplate,ImageExamQuestionUnit,ImageQuestionPaper,CandidateJobStagesStatus,AudioExamTemplate,AudioQuestionPaper,\
    AudioExamQuestionUnit,Audio,AppliedCandidate,AssociateCandidateAgency,Company,InterviewSchedule,JobOffer,OfferNegotiation,JobOffer,\
    CompanyAssignJob,InternalCandidateBasicDetails,Employee,OnTheGoStages,CandidateJobStatus,CustomTemplate,Tracker,CustomResult,DailySubmission,\
    AssociateCandidateInternal
from agency import models as AgencyModels
import png
from pyqrcode import QRCode
import qrcode
from io import BytesIO
from django.core.files import File
import pandas as pd
from chat.models import Messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
import candidate
from io import BytesIO
import zipfile
from itertools import zip_longest
from django.utils.crypto import get_random_string

from rest_apscheduler.scheduler import Scheduler
from  apscheduler.triggers.date import DateTrigger
import pytz

from chat import models as ChatModels

User = get_user_model()
cureent_user = False
from django.core import serializers
import pdfkit
config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
def bidcruit_home(request):
    return render(request, 'candidate/landing-index.html')


def state_view(request, id):
    states = models.State.objects.filter(country_code_id=id)
    context = {"states": states}
    return render(request, "candidate/state.html", context)


#  to populate city dropdown when state is selected.
def city_view(request, id):
    cities = models.City.objects.filter(state_code_id=id)
    if cities:
        context = {"cities": cities}
    else:
        context = {"cities": ["", 0]}
    return render(request, "candidate/city.html", context)


# get all cities of selected country
def cities_by_country(request, id):
    states = models.State.objects.filter(country_code=id).values_list('id')
    cities = models.City.objects.filter(state_code_id__in=states)
    if cities:
        context = {"cities": cities}
    else:
        context = {"cities": ["", 0]}
    return render(request, "candidate/city.html", context)


def preference_cities_by_country(request, id):
    states = models.State.objects.filter(country_code=id).values_list('id')
    cities = models.City.objects.filter(state_code_id__in=states)
    if cities:
        context = {"cities": cities}
    else:
        context = {"cities": ["", 0]}
    return render(request, "candidate/preference_city.html", context)


@login_required(login_url="/")
def get_active_profile(userid):
    profiles = models.Profile.objects.filter(candidate_id=User.objects.get(id=userid))
    for i in profiles:
        if i.active == True:
            # candidate_profile = models.CandidateProfile.objects.get(profile_id=i)
            return i


def get_present_year():
    return int(datetime.datetime.now().year)


def get_present_month():
    return datetime.datetime.now().strftime('%B')

@login_required(login_url="/")
def index(request):
    if request.user.is_candidate:
        if models.candidate_job_apply_detail.objects.filter(candidate_id=request.user).exists():
            context = {}
            if models.CandidateSEO.objects.filter(candidate_id=request.user.id).exists():
                context['seo'] = models.CandidateSEO.objects.filter(candidate_id=request.user.id)[0]
            current_user = models.CandidateProfile.objects.filter(candidate_id=request.user.id).first()
            get_all_profile = models.CandidateProfile.objects.filter(candidate_id=request.user.id)
            get_profile_list = [i.profile_id.id for i in get_all_profile]
            models.Profile.objects.filter(candidate_id=request.user.id).exclude(id__in=get_profile_list).delete()
            referral_list = models.ReferralDetails.objects.filter(referred_by=User.objects.get(id=request.user.id))
            count = 0
            profiles = models.Profile.objects.filter(candidate_id=request.user.id)
            profile_count = len(profiles)
            for i in profiles:
                if i.active == True:
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",i.id)
                    request.session['active_profile_id'] = i.id
                    context['active_profile_hide_fields'] = models.Candidate_Hide_Fields.objects.get(
                        candidate_id=request.user, profile_id=i)
                    context['active_profile'] = i
                    context['userdata'] = models.CandidateProfile.objects.get(candidate_id=request.user, profile_id=i)
                    break
            for i in referral_list:
                if i.referred_to.is_active:
                    count += 1
        
            context['profile'] = current_user
            context['get_all_profile'] = get_all_profile
            context['referral_list'] = referral_list
            context['count'] = count
            context['profiles'] = profiles
            context['profile_count'] = profile_count

            context['applied_job'] = AppliedCandidate.objects.filter(candidate=User.objects.get(id=request.user.id))
            print(request.user.id)
            context['applied_agency_job'] = AgencyModels.AppliedCandidate.objects.filter(candidate_id=User.objects.get(id=request.user.id))
        else:
            return redirect('candidate:basic_detail')
    else:
        return redirect('accounts:user_logout')
    return render(request, 'candidate/Dashbord-profile.html', context)

def generate_referral_code():
    num = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(12)])
    return num


def ragister(request):
    alert = {}
    if not request.user.is_authenticated:
        if request.method == 'POST':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            referred_by = request.POST.get('referral_code')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            checkbox = request.POST.get('checkbox')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            device_type = ""
            if request.user_agent.is_mobile:
                device_type = "Mobile"
            if request.user_agent.is_tablet:
                device_type = "Tablet"
            if request.user_agent.is_pc:
                device_type = "PC"
            browser_type = request.user_agent.browser.family
            browser_version = request.user_agent.browser.version_string
            os_type = request.user_agent.os.family
            os_version = request.user_agent.os.version_string
            context1 = {
                "ip": ip,
                "device_type": device_type,
                "browser_type": browser_type,
                "browser_version": browser_version,
                "os_type": os_type,
                "os_version": os_version
            }
            if User.objects.filter(email=request.POST['email']).exists():
                alert['message'] = "email already exists"
            else:
                usr = User.objects.create_candidate(email=email, first_name=fname, last_name=lname,
                                                    password=password, ip=ip, device_type=device_type,
                                                    browser_type=browser_type,
                                                    browser_version=browser_version, os_type=os_type,
                                                    os_version=os_version,
                                                    referral_number=generate_referral_code(), referred_by=referred_by)
                try:
                    mail_subject = 'Activate your account.'
                    current_site = get_current_site(request)
                    # print('domain----===========',current_site.domain)
                    html_content = render_to_string('accounts/acc_active_email.html', {'user': usr,
                                                                                       'name': fname + ' ' + lname,
                                                                                       'email': email,
                                                                                       'domain': current_site.domain,
                                                                                       'uid': urlsafe_base64_encode(
                                                                                           force_bytes(usr.pk)),
                                                                                       'token': account_activation_token.make_token(
                                                                                           usr), })
                    to_email = usr.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    if models.User.objects.filter(referral_number=referred_by).exists():
                        referred_by_user = User.objects.get(referral_number=referred_by)
                        referred_to_user = User.objects.get(email__exact=email)
                        models.ReferralDetails.objects.create(referred_by=referred_by_user,
                                                              referred_to=referred_to_user)
                except BadHeaderError:
                    new_registered_usr = User.objects.get(email__exact=email).delete()
                    models.ReferralDetails.objects.get(referred_to=new_registered_usr).delete()
                    alert['message'] = "email not send"
                return activate_account_confirmation(request, fname + ' ' + lname, email)

    else:
        if request.user.is_authenticated:
            if request.user.is_candidate:
                return redirect('candidate:home')
            if request.user.is_company:
                profile = CompanyProfile.objects.filter(company_id=request.user.id)
                if profile:
                    return redirect('company:company_profile')
                else:
                    return redirect('company:add_edit_profile')
    return render(request, 'candidate/candidate_signup.html', alert)
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:user_logout')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'candidate/ATS/change-password.html', {
        'form': form
    })

# def upload_resume(request,**kargs):
#     # if request.method == "POST":
#     #   request_file = request.FILES['resume'] if 'resume' in request.FILES else None
#     print('\n\n\nrequest_file', kargs)
#     personal = models.CandidateProfile.objects.filter(candidate_id=User.objects.get(email=request.user.email))
#     country = models.Country.objects.all()
#     state = models.State.objects.all()
#     city = models.City.objects.all()
#     language = models.Languages.objects.all()
#     fluency = models.Fluency.objects.all()
#     gender = models.Gender.objects.all()
#     maritial_type = models.MaritalType.objects.all()
#     notice_period = models.NoticePeriod.objects.all()
#     #  uploaded_cv = models.UploadCv.objects.create(candidate_id=User.objects.get(email=request.user.email),
#     #                                               resume=request_file)
#     fileurl = models.UploadCv.objects.filter(candidate_id=User.objects.get(email=request.user.email)).order_by(
#         '-id').first()
#     resume_data = False
#     exp_years = [str(yearrange) if yearrange <= 30 else '30+' for yearrange in range(32)]
#     exp_months = [str(i) for i in range(12)]
#     kargs['add']= 'add'
#     models.Profile.objects.get(id=request.session['profile_id'])=None
#     if kargs['add'] != 'add':    
#         if personal:
#             for profile in personal:
#                 total_experience_years = str(profile.total_experience).split('.')[0]
#                 total_experience_months = str(profile.total_experience).split('.')[1]
#                 candidate_preferred_cities = []
#                 for city_id in profile.preferred_cities.split(","):
#                     city_obj = models.City.objects.get(id=city_id)
#                     candidate_preferred_cities.append({'id': city_obj.id, 'city_name': city_obj.city_name})
#                 state = models.State.objects.filter(country_code=profile.country.id)
#                 city = models.City.objects.filter(state_code=profile.state.id)
#             education_reload = models.CandidateEducation.objects.filter(
#                 candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#             if education_reload:
#                 experience_reload = models.CandidateExperience.objects.filter(
#                     candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                 if experience_reload:
#                     certification_reload = models.CandidateCertificationAttachment.objects.filter(
#                         candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                     if certification_reload:
#                         skillusermap_reload = models.CandidateSkillUserMap.objects.filter(
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         if skillusermap_reload:
#                             portfolio_reload = models.CandidatePortfolio.objects.filter(
#                                 candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                             if portfolio_reload:
#                                 summa_reload = models.CandidateSummary.objects.filter(
#                                     candidate_id=User.objects.get(email=request.user.email))
#                                 if summa_reload:
#                                     socialnetwork_reload = models.CandidateSocialNetwork.objects.filter(
#                                         candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                                     if socialnetwork_reload:
#                                         awards_reload = models.CandidateAward.objects.filter(
#                                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                                         if awards_reload:
#                                             language_reload = models.CandidateLanguage.objects.filter(candidate_id=
#                                             User.objects.get(
#                                                 email=request.user.email)).order_by('record_id')
#                                             if language_reload:
#                                                 otherfield_reload = models.CandidateOtherField.objects.filter(
#                                                     candidate_id=User.objects.get(email=request.user.email)).order_by(
#                                                     'record_id')
#                                                 if otherfield_reload:
#                                                     return render(request, "candidate/candidate_wizard_form.html",
#                                                                 {'fileurl': fileurl, 'personal': personal,
#                                                                 'education_get': education_reload,
#                                                                 'experience_get': experience_reload,
#                                                                 'certification_get': certification_reload,
#                                                                 'skillusermap_get': skillusermap_reload,
#                                                                 'portfolio_get': portfolio_reload,
#                                                                 'resume_data': resume_data,
#                                                                 'summa_get': summa_reload,
#                                                                 'otherfield_get': otherfield_reload,
#                                                                 'country': country, 'fluency': fluency,
#                                                                 'language': language,
#                                                                 'language_reload': language_reload,
#                                                                 'socialnetwork_reload': socialnetwork_reload,
#                                                                 'awards_get': awards_reload,
#                                                                 'notice_period':notice_period,'city':city,'state':state,
#                                                                 'maritial_type': maritial_type,
#                                                                 'gender': gender,
#                                                                 'exp_years':exp_years,'exp_months':exp_months,
#                                                                 'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                                 ,'candidate_preferred_cities':candidate_preferred_cities})
#                                                 return render(request, "candidate/candidate_wizard_form.html",
#                                                             {'fileurl': fileurl, 'personal': personal,
#                                                             'education_get': education_reload,
#                                                             'experience_get': experience_reload,
#                                                             'certification_get': certification_reload,
#                                                             'skillusermap_get': skillusermap_reload,
#                                                             'portfolio_get': portfolio_reload,
#                                                             'resume_data': resume_data,
#                                                             'summa_get': summa_reload,
#                                                             'country': country, 'fluency': fluency, 'language': language,
#                                                             'language_reload': language_reload,
#                                                             'socialnetwork_reload': socialnetwork_reload,
#                                                             'awards_get': awards_reload,'notice_period':notice_period,
#                                                             'maritial_type': maritial_type,
#                                                             'gender': gender,
#                                                             'city':city,'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                                                             'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                             ,'candidate_preferred_cities':candidate_preferred_cities})
#                                             return render(request, "candidate/candidate_wizard_form.html",
#                                                         {'fileurl': fileurl, 'personal': personal,
#                                                         'education_get': education_reload,
#                                                         'experience_get': experience_reload,
#                                                         'certification_get': certification_reload,
#                                                         'skillusermap_get': skillusermap_reload,
#                                                         'portfolio_get': portfolio_reload, 'resume_data': resume_data,
#                                                         'summa_get': summa_reload, 'country': country,
#                                                         'fluency': fluency,
#                                                         'language': language,
#                                                         'maritial_type': maritial_type,
#                                                         'gender': gender,
#                                                         'socialnetwork_reload': socialnetwork_reload,
#                                                         'awards_get': awards_reload,'notice_period':notice_period,
#                                                         'city':city,'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                                                         'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                         ,'candidate_preferred_cities':candidate_preferred_cities})
#                                         return render(request, "candidate/candidate_wizard_form.html",
#                                                     {'fileurl': fileurl, 'personal': personal,
#                                                     'education_get': education_reload,
#                                                     'experience_get': experience_reload,
#                                                     'certification_get': certification_reload,
#                                                     'skillusermap_get': skillusermap_reload,
#                                                     'portfolio_get': portfolio_reload, 'resume_data': resume_data,
#                                                     'country': country, 'fluency': fluency, 'language': language,'maritial_type':maritial_type,
#                         'gender':gender,
#                                                     'notice_period':notice_period,'city':city,'state':state,
#                                                     'exp_years':exp_years,'exp_months':exp_months,
#                                                     'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                     ,'candidate_preferred_cities':candidate_preferred_cities})
#                                     return render(request, "candidate/candidate_wizard_form.html",
#                                                 {'fileurl': fileurl, 'personal': personal,
#                                                 'education_get': education_reload,
#                                                 'experience_get': experience_reload,
#                                                 'certification_get': certification_reload, 'resume_data': resume_data,
#                                                 'skillusermap_get': skillusermap_reload, 'country': country,
#                                                 'fluency': fluency, 'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,
#                                                 'city':city,'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                                                 'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                 ,'candidate_preferred_cities':candidate_preferred_cities})
#                                 return render(request, "candidate/candidate_wizard_form.html",
#                                             {'fileurl': fileurl, 'personal': personal, 'education_get': education_reload,
#                                             'resume_data': resume_data,
#                                             'experience_get': experience_reload,
#                                             'certification_get': certification_reload,
#                                             'country': country, 'fluency': fluency, 'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,
#                                             'city':city,'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                                             'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                             ,'candidate_preferred_cities':candidate_preferred_cities})
#                             return render(request, "candidate/candidate_wizard_form.html",
#                                         {'fileurl': fileurl, 'personal': personal, 'certification_get': certification_reload,'education_get': education_reload,
#                                         'resume_data': resume_data,
#                                         'experience_get': experience_reload, 'country': country, 'fluency': fluency,
#                                         'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,'city':city,'state':state,
#                                         'exp_years':exp_years,'exp_months':exp_months,
#                                         'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                         ,'candidate_preferred_cities':candidate_preferred_cities})
#                         return render(request, "candidate/candidate_wizard_form.html",
#                                     {'fileurl': fileurl, 'personal': personal, 'resume_data': resume_data,
#                                     'education_get': education_reload, 'experience_get': experience_reload, 'country': country, 'fluency': fluency,
#                                     'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,'city':city,'state':state,
#                                     'exp_years':exp_years,'exp_months':exp_months,
#                                     'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                     ,'candidate_preferred_cities':candidate_preferred_cities})
#                     return render(request, "candidate/candidate_wizard_form.html",
#                                 {'fileurl': fileurl, 'personal': personal, 'resume_data': resume_data, 'country': country,
#                                 'fluency': fluency, 'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,
#                                 'city':city,'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                                 'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                 ,'candidate_preferred_cities':candidate_preferred_cities})
#                 return render(request, "candidate/candidate_wizard_form.html",
#                             {'fileurl': fileurl, 'personal': personal, 'resume_data': resume_data, 'country': country,
#                             'fluency': fluency, 'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,'city':city,
#                             'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                             'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                             ,'candidate_preferred_cities':candidate_preferred_cities})
#             return render(request, "candidate/candidate_wizard_form.html",
#                         {'fileurl': fileurl, 'personal': personal, 'resume_data': resume_data, 'country': country,
#                         'fluency': fluency, 'language': language,'maritial_type':maritial_type,
#                         'gender':gender,'notice_period':notice_period,
#                         'city':city,'state':state,'exp_years':exp_years,'exp_months':exp_months,
#                         'total_experience_years':total_experience_years,'total_experience_months':total_experience_months,
#                         'candidate_preferred_cities':candidate_preferred_cities})
#         else:
#             return render(request, "candidate/candidate_wizard_form.html",
#                         {'fileurl': fileurl, 'resume_data': resume_data, 'country': country, 'fluency': fluency,'maritial_type':maritial_type,
#                         'gender':gender,'language': language,'notice_period':notice_period,'exp_years':exp_years,'exp_months':exp_months})
#     else:
#         if models.Profile.objects.get(id=request.session['profile_id']):
#             personal = models.CandidateProfile.objects.filter(candidate_id=User.objects.get(email=request.user.email),profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])))
#             if personal:
#                 for profile in personal:
#                     total_experience_years = str(profile.total_experience).split('.')[0]
#                     total_experience_months = str(profile.total_experience).split('.')[1]
#                     candidate_preferred_cities = []
#                     for city_id in profile.preferred_cities.split(","):
#                         city_obj = models.City.objects.get(id=city_id)
#                         candidate_preferred_cities.append({'id': city_obj.id, 'city_name': city_obj.city_name})
#                     state = models.State.objects.filter(country_code=profile.country.id)
#                     city = models.City.objects.filter(state_code=profile.state.id)
#                 education_reload = models.CandidateEducation.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                     candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                 if education_reload:
#                     experience_reload = models.CandidateExperience.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                     candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                     if experience_reload:
#                         certification_reload = models.CandidateCertificationAttachment.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         skillusermap_reload = models.CandidateSkillUserMap.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         portfolio_reload = models.CandidatePortfolio.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         summa_reload = models.CandidateSummary.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email))
#                         socialnetwork_reload = models.CandidateSocialNetwork.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         awards_reload = models.CandidateAward.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         language_reload = models.CandidateLanguage.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         otherfield_reload = models.CandidateOtherField.objects.filter(profile_id=models.Profile.objects.get(id=models.Profile.objects.get(id=request.session['profile_id'])),
#                             candidate_id=User.objects.get(email=request.user.email)).order_by('record_id')
#                         return render(request, "candidate/candidate_wizard_form.html",
#                                                                 {'fileurl': fileurl, 'personal': personal,
#                                                                 'education_get': education_reload,
#                                                                 'experience_get': experience_reload,
#                                                                 'certification_get': certification_reload,
#                                                                 'skillusermap_get': skillusermap_reload,
#                                                                 'portfolio_get': portfolio_reload,
#                                                                 'resume_data': resume_data,
#                                                                 'summa_get': summa_reload,
#                                                                 'otherfield_get': otherfield_reload,
#                                                                 'country': country, 'fluency': fluency,
#                                                                 'language': language,
#                                                                 'language_reload': language_reload,
#                                                                 'socialnetwork_reload': socialnetwork_reload,
#                                                                 'awards_get': awards_reload,
#                                                                 'notice_period':notice_period,'city':city,'state':state,
#                                                                 'maritial_type': maritial_type,
#                                                                 'gender': gender,
#                                                                 'exp_years':exp_years,'exp_months':exp_months,
#                                                                 'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                                 ,'candidate_preferred_cities':candidate_preferred_cities})
#                     else:
#                         return render(request, "candidate/candidate_wizard_form.html",
#                                                                 {'fileurl': fileurl, 'personal': personal,
#                                                                 'education_get': education_reload,
#                                                                 'experience_get': experience_reload,
#                                                                 'notice_period':notice_period,'city':city,'state':state,
#                                                                 'maritial_type': maritial_type,
#                                                                 'gender': gender,
#                                                                 'exp_years':exp_years,'exp_months':exp_months,
#                                                                 'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                                 ,'candidate_preferred_cities':candidate_preferred_cities})
#                 else:
#                     return render(request, "candidate/candidate_wizard_form.html",
#                                                             {'fileurl': fileurl, 'personal': personal,
#                                                             'education_get': education_reload,
#                                                             'notice_period':notice_period,'city':city,'state':state,
#                                                             'maritial_type': maritial_type,
#                                                             'gender': gender,
#                                                             'exp_years':exp_years,'exp_months':exp_months,
#                                                             'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                             ,'candidate_preferred_cities':candidate_preferred_cities})
#             else:
#                 return render(request, "candidate/candidate_wizard_form.html",
#                                                         {'fileurl': fileurl, 'personal': personal,
#                                                         'notice_period':notice_period,'city':city,'state':state,
#                                                         'maritial_type': maritial_type,
#                                                         'gender': gender,
#                                                         'exp_years':exp_years,'exp_months':exp_months,
#                                                         'total_experience_years':total_experience_years,'total_experience_months':total_experience_months
#                                                         ,'candidate_preferred_cities':candidate_preferred_cities})
#         return render(request, "candidate/candidate_wizard_form.html",
#                         {'fileurl': fileurl, 'resume_data': resume_data, 'country': country, 'fluency': fluency,'maritial_type':maritial_type,
#                         'gender':gender,'language': language,'notice_period':notice_period,'exp_years':exp_years,'exp_months':exp_months})

@login_required(login_url="/")
def upload_resume(request, **kargs):
    country = models.Country.objects.all()
    state = models.State.objects.all()
    city = models.City.objects.all()
    language = models.Languages.objects.all()
    fluency = models.Fluency.objects.all()
    gender = models.Gender.objects.all()
    maritial_type = models.MaritalType.objects.all()
    notice_period = models.NoticePeriod.objects.all()
    industry_type = models.IndustryType.objects.all()
    months = models.Month.objects.all()
    profile_themes = models.CandidateProfileTheme.objects.all()
    exp_years = [str(yearrange) if yearrange <= 30 else '30+' for yearrange in range(32)]
    exp_months = [str(i) for i in range(12)]
    candid_basic_details = None
    if models.candidate_job_apply_detail.objects.filter(candidate_id=request.user).exists():
        candid_basic_details = models.candidate_job_apply_detail.objects.get(candidate_id=request.user)
    if kargs['url']:
        return render(request, "candidate/candidate_wizard_form.html", {'country': country,
                                                                        'fluency': fluency, 'language': language,
                                                                        'maritial_type': maritial_type,
                                                                        'gender': gender,
                                                                        'notice_period': notice_period, 'city': city,
                                                                        'state': state, 'exp_years': exp_years,
                                                                        'exp_months': exp_months,
                                                                        'industry_type': industry_type,
                                                                        'profile_themes': profile_themes,
                                                                        'candid_basic_details':candid_basic_details,
                                                                        'months': months})


def check_email_is_valid(request):
    email = request.POST.get("email")
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        user_obj = models.User.objects.filter(email=email).exists()
        if user_obj:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    else:
        return HttpResponse('Invalid')


@login_required(login_url="/")
def personal_detail_temp(request):
    if request.method == 'POST':
        if request.POST.get('emailAddress') == request.user.email:
            user_id = User.objects.get(email=request.POST.get('emailAddress'))
        else:
            return HttpResponse(False)
        if user_id:
            gender = models.Gender.objects.get(id=request.POST.get('gender'))
            notice_period_obj = models.NoticePeriod.objects.get(id=request.POST.get('notice_period'))
            marital_status = models.MaritalType.objects.get(id=request.POST.get('marital_status'))
            if request.POST.get('salary_checkbox') == '1':
                expected_salary_min = 'As Per Company'
                expected_salary_max = 'As Per Company'
            else:
                expected_salary_min = request.POST.get('expected_salary_min')
                expected_salary_max = request.POST.get('expected_salary_max')
            random_no = random.randint(1000, 99999)
            url_name = request.user.first_name + '_' + request.user.last_name + '_' + str(random_no)
            custom_url = url_name
            current_site = get_current_site(request)
            qr_share_link = "https://bidcruit.com/" + url_name + "/"
            # qr_share_link = "https://www.google.com/"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=4,
            )
            qr.add_data(qr_share_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            blob = BytesIO()
            img.save(blob, 'JPEG')
            preferred_cities = ','.join(map(str, request.POST.getlist('preferred_cities')))
            total_experience = request.POST.get('total_experience_year') + '.' + request.POST.get(
                'total_experience_month')

            about = request.POST.get('about-me')
            about = re.sub('\s+style="(.*?)"', "", about)
            technical = request.POST.get('technical-knowledge')
            technical = re.sub('\s+style="(.*?)"', "", technical)
            print('\n\n\n=========== session', request.session['profile_id'])
            candidate_profile_obj, obj_created = models.CandidateProfile.objects.update_or_create(candidate_id=user_id,
                                                                                                  profile_id=models.Profile.objects.get(
                                                                                                      id=
                                                                                                      request.session[
                                                                                                          'profile_id']),
                                                                                                  defaults={
                                                                                                      'contact_no': request.POST.get(
                                                                                                          'phone'),
                                                                                                      'address': request.POST.get(
                                                                                                          'address'),
                                                                                                      'dob': request.POST.get(
                                                                                                          'dob') or None,
                                                                                                      'country': models.Country.objects.get(
                                                                                                          id=int(
                                                                                                              request.POST.get(
                                                                                                                  'country'))),
                                                                                                      'state': models.State.objects.get(
                                                                                                          id=int(
                                                                                                              request.POST.get(
                                                                                                                  'state'))),
                                                                                                      'city': models.City.objects.get(
                                                                                                          id=int(
                                                                                                              request.POST.get(
                                                                                                                  'city'))),
                                                                                                      'gender': gender,
                                                                                                      'marital_status': marital_status,
                                                                                                      'user_image': request.FILES.get(
                                                                                                          'user_image'),
                                                                                                      'current_salary': int(
                                                                                                          request.POST.get(
                                                                                                              'current_salary')),
                                                                                                      'notice_period': notice_period_obj,
                                                                                                      'expected_salary_min': expected_salary_min,
                                                                                                      'expected_salary_max': expected_salary_max,
                                                                                                      'url_name': url_name,
                                                                                                      'designation': request.POST.get(
                                                                                                          'designation'),
                                                                                                      'preferred_cities': preferred_cities,
                                                                                                      'total_experience': float(
                                                                                                          total_experience),
                                                                                                      'technical_knowledge': technical,
                                                                                                      'about_me': about,
                                                                                                      'custom_url': custom_url
                                                                                                  })
            candidate_profile_obj.qr_code.save(request.user.first_name + '.jpg', File(blob), save=True)
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    else:
        print('fail')


@login_required(login_url="/")
def education_temp(request):
    if request.method == 'POST':
        updatedData = json.loads(request.POST.get('education_data'))
        user_id = models.User.objects.get(email=request.user.email)
        for i in updatedData:
            for j in updatedData[i]:
                education_data = updatedData[i][j]

                edu_start_month = models.Month.objects.get(id=education_data['edu_start_month'])
                edu_end_month = models.Month.objects.get(id=education_data['edu_end_month'])
                edu_start_date = edu_start_month.name + "," + " " + education_data['edu_start_year']
                edu_end_date = edu_end_month.name + "," + " " + education_data['edu_end_year']

                attached_file = request.FILES.get('edu_file' + education_data['record_id'], None)
                university_board, uni_created = models.UniversityBoard.objects.update_or_create(
                    name=education_data['c_university'], defaults={'name': education_data['c_university']})
                degree, deg_created = models.Degree.objects.update_or_create(name=education_data['c_degree'])
                summary = education_data['e_summary']
                summary = re.sub('\s+style="(.*?)"', "", summary)
                temp_education, created = models.CandidateEducation.objects.update_or_create(
                    record_id=education_data['record_id'], candidate_id=user_id,
                    profile_id=models.Profile.objects.get(id=int(request.session['profile_id'])),
                    defaults={'university_board': university_board,
                              'degree': degree, 'candidate_id': user_id, 'certificate': attached_file,
                              'start_date': edu_start_date, 'end_date': edu_end_date,
                              'grade': education_data['c_grade'],
                              'summary': summary,
                              })
                if created:
                    pass
                else:
                    temp_education.update_at = datetime.datetime.now()
        # print("\n\n\n\n\n\n////////////////", request.POST.get('gap_checkbox'))
        if request.POST.get('gap_checkbox') == 'true':
            gapData = json.loads(request.POST.get('gap_data'))
            for i in gapData:
                for j in gapData[i]:
                    gap_data = gapData[i][j]

                    edu_gap_start_month = models.Month.objects.get(id=gap_data['edu_gap_start_month'])
                    edu_gap_end_month = models.Month.objects.get(id=gap_data['edu_gap_end_month'])
                    gap_start_date = edu_gap_start_month.name + "," + " " + gap_data['edu_gap_start_year']
                    gap_end_date = edu_gap_end_month.name + "," + " " + gap_data['edu_gap_end_year']

                    models.Gap.objects.update_or_create(candidate_id=user_id, profile_id=models.Profile.objects.get(
                        id=request.session['profile_id']),
                                                        record_id=gap_data['record_id'], type="education",
                                                        defaults={'start_date': gap_start_date,
                                                                  'end_date': gap_end_date,
                                                                  'reason': gap_data['gap_reason']})

        certiData = json.loads(request.POST.get('certi_data'))
        for i in certiData:
            for j in certiData[i]:
                certificate_data = certiData[i][j]
                attached_file = request.FILES.get('certi_file' + certificate_data['record_id'], None)
                summary = certificate_data['c_summary']
                summary = re.sub('\s+style="(.*?)"', "", summary)
                if certificate_data['c_certificate_name'] and certificate_data['c_certificate_organization'] and \
                        certificate_data['c_certificate_year']:
                    TempCertificationAttachment, created = models.CandidateCertificationAttachment.objects.update_or_create(
                        candidate_id=user_id, record_id=certificate_data['record_id'],
                        profile_id=models.Profile.objects.get(id=request.session['profile_id']),
                        defaults={'name_of_certificate': certificate_data['c_certificate_name'],
                                  'institute_organisation': certificate_data['c_certificate_organization'],
                                  'summary': summary,
                                  'attached_certificate': attached_file,
                                  'year': certificate_data['c_certificate_year']})
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@login_required(login_url="/")
def work_experience_temp(request):
    if request.method == 'POST':
        updatedData = json.loads(request.POST.get('exp_data'))
        user_id = User.objects.get(email=request.user.email)
        for i in updatedData:
            for j in updatedData[i]:
                work_experience = updatedData[i][j]
                exp_start_month = models.Month.objects.get(id=work_experience['exp_start_month'])
                # print('\n\n\n\n\n',work_experience['exp_current_checkbox'])
                exp_start_date = exp_start_month.name + "," + " " + work_experience['exp_start_year']
                if work_experience['exp_current_checkbox']:
                    exp_end_date = 'present'
                    end_salary = 'present'
                else:
                    exp_end_month = models.Month.objects.get(id=work_experience['exp_end_month'])
                    exp_end_date = exp_end_month.name + "," + " " + work_experience['exp_end_year']
                    end_salary = work_experience['w_end_salary']
                w_job_description = work_experience['w_job_description']
                w_job_description = re.sub('\s+style="(.*?)"', "", w_job_description)
                company, com_created = models.Company.objects.update_or_create(
                    company_name=work_experience['c_company_name'])
                temp_experience, created = models.CandidateExperience.objects.update_or_create(
                    record_id=work_experience['record_id'], candidate_id=user_id,
                    profile_id=models.Profile.objects.get(id=request.session['profile_id']),
                    defaults={'job_profile_name': work_experience['c_job_profile'], 'company': company,
                              'start_date': exp_start_date, 'end_date': exp_end_date,
                              'start_salary': work_experience['w_start_salary'],
                              'end_salary': end_salary,
                              'job_description_responsibility': w_job_description})
                attached_file = request.FILES.getlist('file' + work_experience['record_id'], None)
                attached_file_name = request.POST.getlist('file_name' + work_experience['record_id'], None)
                for (file_name, file) in zip(attached_file_name, attached_file):
                    models.CandidateExpDocuments.objects.create(candidate_id=user_id, candidate_exp_id=temp_experience,
                                                                record_id=work_experience['record_id'],
                                                                document_name=file_name,
                                                                exp_document=file)

        if request.POST.get('gap_checkbox') == 'true':
            gapData = json.loads(request.POST.get('gap_data'))
            for i in gapData:
                for j in gapData[i]:
                    gap_data = gapData[i][j]

                    exp_gap_start_month = models.Month.objects.get(id=gap_data['exp_gap_start_month'])
                    exp_gap_end_month = models.Month.objects.get(id=gap_data['exp_gap_end_month'])
                    gap_start_date = exp_gap_start_month.name + "," + " " + gap_data['exp_gap_start_year']
                    gap_end_date = exp_gap_end_month.name + "," + " " + gap_data['exp_gap_end_year']

                    models.Gap.objects.update_or_create(candidate_id=user_id, profile_id=models.Profile.objects.get(
                        id=request.session['profile_id']),
                                                        record_id=gap_data['record_id'], type="experience",
                                                        defaults={'start_date': gap_start_date,
                                                                  'end_date': gap_end_date,
                                                                  'reason': gap_data['gap_reason']})

        portfolioData = json.loads(request.POST.get('portfolio_data'))
        for i in portfolioData:
            for j in portfolioData[i]:
                portfolio = portfolioData[i][j]
                attached_file = request.FILES.get('portfolio_file' + portfolio['record_id'], None)
                project_learning = portfolio['project_learning']
                project_learning = re.sub('\s+style="(.*?)"', "", w_job_description)
                if portfolio['project_year'] and portfolio['project_title'] and portfolio['project_description']:
                    portfolio_id, created = models.CandidatePortfolio.objects.update_or_create(candidate_id=user_id,
                                                                                               profile_id=
                                                                                               models.Profile.objects.get(
                                                                                                   id=request.session[
                                                                                                       'profile_id']),
                                                                                               record_id=portfolio[
                                                                                                   'record_id'],
                                                                                               defaults={
                                                                                                   'year': portfolio[
                                                                                                       'project_year'],
                                                                                                   'project_title':
                                                                                                       portfolio[
                                                                                                           'project_title'],
                                                                                                   'description':
                                                                                                       portfolio[
                                                                                                           'project_description'],
                                                                                                   'link': portfolio[
                                                                                                       'project_website'],
                                                                                                   'project_document': attached_file,
                                                                                                   'learning_from_project':
                                                                                                       project_learning})
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@login_required(login_url="/")
def skill_temp(request):
    if request.method == 'POST':
        updatedData = json.loads(request.body.decode('UTF-8'))
        user_id = models.User.objects.get(email=request.user.email)
        for i in updatedData['total_skills']:
            for j in updatedData['total_skills'][i]:
                skill = updatedData['total_skills'][i][j]
                skill_id, created = models.Skill.objects.get_or_create(name=skill['skill_name'])
                models.CandidateSkillUserMap.objects.update_or_create(candidate_id=user_id,
                                                                      profile_id=models.Profile.objects.get(
                                                                          id=request.session['profile_id']),
                                                                      record_id=skill['record_id'],
                                                                      defaults={'skill': skill_id,
                                                                                'total_exp': skill[
                                                                                    'skill_total_experience'],
                                                                                'last_used': skill['last_used']})
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@login_required(login_url="/")
def other_temp(request):
    if request.method == 'POST':
        user_id = models.User.objects.get(email=request.user.email)
        languageData = json.loads(request.POST.get('languages_data'))
        for i in languageData:
            for j in languageData[i]:
                language_data = languageData[i][j]
                language = models.Languages.objects.get(id=language_data['c_language'])
                fluency = models.Fluency.objects.get(id=language_data['c_fluency'])
                candidate_language, created = models.CandidateLanguage.objects.update_or_create(
                    record_id=language_data['record_id'], candidate_id=user_id,
                    profile_id=models.Profile.objects.get(id=request.session['profile_id']),
                    defaults={
                        'language_id': language,
                        'fluency_id': fluency})
        awardData = json.loads(request.POST.get('awards_data'))
        for i in awardData:
            for j in awardData[i]:
                award_data = awardData[i][j]
                if award_data['award_title'] and award_data['award_date'] and award_data['awarder']:
                    award, created = models.CandidateAward.objects.update_or_create(candidate_id=user_id,
                                                                                    profile_id=models.Profile.objects.get(
                                                                                        id=request.session[
                                                                                            'profile_id']),
                                                                                    record_id=award_data['record_id'],
                                                                                    defaults={
                                                                                        'title': award_data[
                                                                                            'award_title'],
                                                                                        'year': award_data[
                                                                                            'award_date'],
                                                                                        'awarder': award_data[
                                                                                            'awarder']})
        socialData = json.loads(request.POST.get('social_data'))
        for i in socialData:
            for j in socialData[i]:
                social_data = socialData[i][j]
                # print(social_data)
                social, created = models.CandidateSocialNetwork.objects.update_or_create(candidate_id=user_id,
                                                                                         profile_id=models.Profile.objects.get(
                                                                                             id=request.session[
                                                                                                 'profile_id']),
                                                                                         record_id=social_data[
                                                                                             'record_id'], defaults={

                        'url': social_data['network_url'], 'network_name': social_data['network_name']})
        # models.CandidateSEO.objects.create(candidate_id=user_id)
        models.CandidateProfile.objects.filter(candidate_id=user_id).update(final_status=True)
        models.CandidateEducation.objects.filter(candidate_id=user_id).update(final_status=True)
        models.CandidateExperience.objects.filter(candidate_id=user_id).update(final_status=True)
        models.CandidateCertificationAttachment.objects.filter(candidate_id=user_id).update(final_status=True)
        models.CandidateSkillUserMap.objects.filter(candidate_id=user_id).update(final_status=True)
        models.CandidatePortfolio.objects.filter(candidate_id=user_id).update(final_status=True)
        all_profiles = models.Profile.objects.filter(candidate_id=User.objects.get(id=request.user.id))
        for m in all_profiles:
            m.active = False
            m.update_at = datetime.datetime.now()
            m.save()
        current_page = request.POST.get('profile_url')
        # print('\n\n\n\ncurrent_page >>>>>>>>>>>>', current_page)
        profile_url = current_page.split('/')[-1]
        profile = models.Profile.objects.get(url=profile_url)
        profile.active = True
        profile.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@login_required(login_url="/")
def remove_record(request):
    if request.method == 'POST':
        if request.POST.get('step') == 'education':
            models.CandidateEducation.objects.filter(record_id=request.POST.get('record_id'),
                                                     profile_id=models.Profile.objects.get(
                                                         id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'work_experience':
            # print("WOOOOOOOOOOOOORK EXPERIENCE DEETELEDEDE")
            models.CandidateExperience.objects.filter(record_id=request.POST.get('record_id'),
                                                      profile_id=models.Profile.objects.get(
                                                          id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
            models.CandidateExpDocuments.objects.filter(record_id=request.POST.get('record_id'),
                                                        profile_id=models.Profile.objects.get(
                                                            id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'certificate':
            models.CandidateCertificationAttachment.objects.filter(record_id=request.POST.get('record_id'),
                                                                   profile_id=models.Profile.objects.get(
                                                                       id=request.session['profile_id']),
                                                                   candidate_id=(
                                                                       models.User.objects.get(
                                                                           email=request.user.email))).delete()
        if request.POST.get('step') == 'skill':
            models.CandidateSkillUserMap.objects.filter(record_id=request.POST.get('record_id'),
                                                        profile_id=models.Profile.objects.get(
                                                            id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'portfolio':
            models.CandidatePortfolio.objects.filter(record_id=request.POST.get('record_id'),
                                                     profile_id=models.Profile.objects.get(
                                                         id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'social':
            models.CandidateSocialNetwork.objects.filter(record_id=request.POST.get('record_id'),
                                                         profile_id=models.Profile.objects.get(
                                                             id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'award':
            models.CandidateAward.objects.filter(record_id=request.POST.get('record_id'),
                                                 profile_id=models.Profile.objects.get(
                                                     id=request.session['profile_id']),
                                                 candidate_id=(
                                                     models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'language':
            models.CandidateLanguage.objects.filter(record_id=request.POST.get('record_id'),
                                                    profile_id=models.Profile.objects.get(
                                                        id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'other':
            models.CandidateOtherField.objects.filter(record_id=request.POST.get('record_id'),
                                                      profile_id=models.Profile.objects.get(
                                                          id=request.session['profile_id']), candidate_id=(
                    models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'experience_gap':
            models.Gap.objects.filter(record_id=request.POST.get('record_id'),
                                      profile_id=models.Profile.objects.get(
                                          id=request.session['profile_id']),
                                      type="experience",
                                      candidate_id=(models.User.objects.get(email=request.user.email))).delete()
        if request.POST.get('step') == 'education_gap':
            models.Gap.objects.filter(record_id=request.POST.get('record_id'),
                                      profile_id=models.Profile.objects.get(
                                          id=request.session['profile_id']),
                                      type="education",
                                      candidate_id=(models.User.objects.get(email=request.user.email))).delete()

        return HttpResponse(True)
    else:
        return HttpResponse(False)


# def timeline(request,url):
#     # dictonary to convert month to number
#     month = {'January':1,
#         'February':2,
#         'March':3,
#         'April':4,
#         'May':5,
#         'June':6,
#         'July':7,
#         'August':8,
#         'September':9,
#         'October':10,
#         'November':11,
#         'December':12
#         }
#     profile_id_get=models.CandidateProfile.objects.get(url_name=url)
#     activeprofile=models.Profile.objects.get(candidate_id=profile_id_get.candidate_id,active=True)
#     hire={}
#     looking_job=models.CandidateSEO.objects.get(candidate_id=activeprofile.candidate_id)
#     company_data_status={}
#     # activeprofile=models.Profile.objects.get(id=profile_id_get.profile_id)
#     if activeprofile.active:
#         profile=profile_id_get.profile_id
#         candidate_id=''
#         if request.user.is_authenticated:
#             print('asdddasddas')
#             if request.user.is_company:
#                 candidate_id=profile_id_get.candidate_id_id
#                 hire=CandidateHire.objects.filter(profile_id=activeprofile.id,candidate_id=candidate_id,company_id=User.objects.get(id=request.user.id))
#                 company_data_status=models.company_data_request.objects.filter(profile_id=activeprofile.id,candidate_id=candidate_id,company_id=User.objects.get(id=request.user.id))
#             elif request.user.is_candidate:
#                 candidate_id=request.user.id
#         else:
#             candidate_id=profile_id_get.candidate_id.id
#         user = User.objects.get(id=activeprofile.candidate_id.id)
#         print()
#         count= 0
#         year_title_pairs={}
#         print("before hide field")
#         print("user is ",user)
#         print("profile is ",profile)
#         hidefield=models.Candidate_Hide_Fields.objects.get(candidate_id=user,profile_id=profile)
#         profile_show=models.CandidateProfile.objects.get(candidate_id=user,profile_id=profile)
#         skills = models.CandidateSkillUserMap.objects.filter(candidate_id =user,profile_id=profile)
#         start_years =[]
#         end_years =[]
#         skill_names = ''
#         last_used=0
#         if skills:
#             for i in skills:
#                 if i.last_used=='present':
#                     last_used=int(get_present_year())
#
#                 skill_names += i.skill.name +','
#                 start_year = int(last_used) - int(i.total_exp)
#                 start_years.append(start_year)
#                 end_years.append(last_used)
#         year_salary_pair =[]
#         company_names =[]
#         experiences = models.CandidateExperience.objects.filter(candidate_id=user,profile_id=activeprofile.id)
#         if experiences:
#             for i in experiences:
#                 company_names.append(i.company.company_name)
#                 end_salary=0
#                 end_date=0
#                 if i.end_date:
#                     salary_start_year  =int(i.start_date.split(',')[1])
#                     salary_start_year += month[i.start_date.split(',')[0]] /12
#                     salary_end_year=0
#                     if i.end_date=='present':
#                         end_date=int(get_present_year())
#                         salary_end_year = int(get_present_year())
#                         salary_end_year += month[get_present_month()] /12
#                     else:
#                         end_date=int(i.end_date.split(',')[1])
#                     if i.end_salary=='present':
#                         end_salary=i.start_salary
#                     year_salary_pair.append([salary_start_year,i.start_salary])
#                     year_salary_pair.append([salary_end_year,end_salary])
#                     if int(end_date) not in list(year_title_pairs.keys()):
#                         year_title_pairs[end_date] =[]
#                         year_title_pairs[end_date].append(i)
#                     else:
#                         year_title_pairs[end_date].append(i)
#                 # year_title_pairs.add(i.end_date.split(',')[1],i.job_profile_name)
#         company_names = ','.join(company_names)
#         educations = models.CandidateEducation.objects.filter(candidate_id = user,profile_id=activeprofile.id)
#         if educations:
#             for i in educations:
#                 count += 1
#                 if i.end_date:
#                     if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
#                         year_title_pairs[int(i.end_date.split(',')[1])] =[]
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#                     else:
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#         certificates = models.CandidateCertificationAttachment.objects.filter(candidate_id=user,profile_id=activeprofile.id)
#         if certificates:
#             for i in certificates:
#                 count += 1
#                 if i.year:
#                     if int(i.year) not in list(year_title_pairs.keys()):
#                         year_title_pairs[int(i.year)] =[]
#                         year_title_pairs[int(i.year)].append(i)
#                     else:
#                         year_title_pairs[int(i.year)].append(i)
#         awards = models.CandidateAward.objects.filter(candidate_id=user,profile_id=activeprofile.id)
#         if awards:
#             for i in awards:
#                 count += 1
#                 if i.year:
#                     if int(i.year) not in list(year_title_pairs.keys()):
#                         year_title_pairs[int(i.year)] =[]
#                         year_title_pairs[int(i.year)].append(i)
#                     else:
#                         year_title_pairs[int(i.year)].append(i)
#         print(hidefield.edu_document)
#         portfolio = models.CandidatePortfolio.objects.filter(candidate_id=user,profile_id=activeprofile.id)
#         if portfolio:
#             for i in portfolio:
#                 count += 1
#                 if i.year:
#                     if int(i.year) not in list(year_title_pairs.keys()):
#                         year_title_pairs[int(i.year)] =[]
#                         year_title_pairs[int(i.year)].append(i)
#                     else:
#                         year_title_pairs[int(i.year)].append(i)
#         print(hidefield.edu_document)
#         gaps = models.Gap.objects.filter(candidate_id=user,profile_id = activeprofile.id)
#         print(gaps)
#         if gaps:
#             print("gaaaaaaaaaps ",gaps)
#             for i in gaps:
#                 print("enterrred for loop for jgaps")
#                 if i.end_date:
#                     if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
#                         print("ifffffffffffffffffffffffffffffffffffffffffffffff")
#                         year_title_pairs[int(i.end_date.split(',')[1])] =[]
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#                     else:
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#
#         print(year_title_pairs)
#     sorted_key_list = sorted(year_title_pairs)
#     sorted_key_list.reverse()
#     job_preference=models.CandidateJobPreference.objects.filter(candidate_id=user)
#
#
#
#     return render(request,'candidate/candidate_resume.html',
#                   {'company_data_status':company_data_status,'looking_job':looking_job,'hire':hire,'profile':profile_id_get,'hidefield':hidefield,'profile_show':profile_show,'user':user,'experiences':experiences,'portfolios':portfolio,'educations':educations,'certificates':certificates,'awards':awards,'sorted_keys':sorted_key_list,'year_title_pairs':year_title_pairs,'start_years':start_years,'end_years':end_years,'skills':skill_names,'year_salary_pair':year_salary_pair,'company_names':company_names,'job_preference':job_preference})
@login_required(login_url="/")
def candidate_profile(request):
    existing_user = models.CandidateProfile.objects.filter(candidate_id=request.user.id).count()
    # context['existing_user'] = existing_user
    profile = models.CandidateProfile.objects.get(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    education = models.CandidateEducation.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    experience = models.CandidateExperience.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    skills = models.CandidateSkillUserMap.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    summary = models.CandidateSummary.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    certificates = models.CandidateCertificationAttachment.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    portfolio = models.CandidatePortfolio.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    languages = models.CandidateLanguage.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    return render(request, 'candidate/candidate_profile.html',
                  {'existing_user': 0, 'profile': profile, 'education': education,
                   'experience': experience, 'skills': skills, 'summary': summary,
                   'certificates': certificates, 'portfolio': portfolio, 'languages': languages})


def statistics_view(request):
    dict1 = {'a1': 1, 'a2': 2, 'a3': 3}
    sample_data = json.dumps(dict1)
    profile = models.CandidateProfile.objects.get(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    return render(request, 'candidate/statistics.html', {'sample_data': sample_data, 'profile': profile})


def get_filter_options(request):
    # grouped_purchases = Purchase.objects.annotate(year=ExtractYear('time')).values('year').order_by('-year').distinct()
    # options = [purchase['year'] for purchase in grouped_purchases]

    return JsonResponse({
        'options': {'2020': 2020},
    })


def payment_method_chart(request):
    skills = models.CandidateSkillUserMap.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    skill = []
    exp = []
    level = []
    for i in skills:
        skill.append(i.skill.name)
        exp.append(int(i.end_year) - int(i.start_year))
        level.append(i.level.fluency)
    # print("==================",skill)
    return JsonResponse({
        'title': 'Skills With Experience(years)',
        'data': {
            'labels': skill,
            'datasets': [
                {
                    'label': 'Skills',
                    'backgroundColor': generate_color_palette(len(skill)),
                    'borderColor': generate_color_palette(len(skill)),
                    'data': exp,
                },
            ]
        },
    })


def job_exp_Chart(request):
    c_experience = models.CandidateExperience.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    experience = []
    exp = []
    for i in c_experience:
        experience.append(i.company.company_name)
        start_date = datetime.datetime.strptime(i.start_date, '%B, %Y')
        end_date = datetime.datetime.strptime(i.end_date, '%B, %Y')
        difference = relativedelta(end_date, start_date)
        final_dif = str(difference.years) + '.' + str(difference.months)
        exp.append(final_dif)

    return JsonResponse({
        'title': 'Experience in Years',
        'data': {
            'labels': experience,
            'datasets': [{
                'label': '',
                'backgroundColor': generate_color_palette(len(experience)),
                'borderColor': generate_color_palette(len(experience)),
                'data': exp,
            }]
        },
    })


def edu_per_chart(request):
    c_education = models.CandidateEducation.objects.filter(
        candidate_id=(models.User.objects.get(email=request.user.email)))
    degree = []
    grade = []
    exp = []
    for i in c_education:
        degree.append(i.degree.name)
        grade.append(i.grade)
        start_date = datetime.datetime.strptime(i.start_date, '%B, %Y')
        end_date = datetime.datetime.strptime(i.end_date, '%B, %Y')
        difference = relativedelta(end_date, start_date)
        final_dif = str(difference.years) + '.' + str(difference.months)
        exp.append(final_dif)
    return JsonResponse({
        'title': 'Education',
        'data': {
            'labels': degree,
            'datasets': [{
                'label': '',
                'backgroundColor': ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
                'borderColor': generate_color_palette(len(grade)),
                'data': exp,
            }]
        },
    })


# def candidate_web_profile(request,url_name):
#     profile = models.CandidateProfile.objects.get(url_name=url_name)
#     if request.user.id == profile.candidate_id.id:
#         is_self = True
#     else:
#         is_self = False
#     if profile:
#         education = models.CandidateEducation.objects.filter(candidate_id=profile.candidate_id)
#         experience = models.CandidateExperience.objects.filter(candidate_id=profile.candidate_id)
#         skills = models.CandidateSkillUserMap.objects.filter(candidate_id=profile.candidate_id)
#         summary = models.CandidateSummary.objects.filter(candidate_id=profile.candidate_id)
#         certificates = models.CandidateCertificationAttachment.objects.filter(candidate_id=profile.candidate_id)
#         portfolio = models.CandidatePortfolio.objects.filter(candidate_id=profile.candidate_id)
#         languages = models.CandidateLanguage.objects.filter(candidate_id=profile.candidate_id)
#         job_preference = models.CandidateJobPreference.objects.filter(candidate_id=profile.candidate_id)
#         job_preference_other = models.CandidateJobPreferenceOther.objects.filter(candidate_id=profile.candidate_id)
#         return render(request, 'candidate/candidate_web_profile.html',
#                       {'existing_user': 0, 'profile': profile, 'education': education,
#                        'experience': experience, 'skills': skills, 'summary': summary,
#                        'certificates': certificates, 'portfolio': portfolio, 'languages': languages,'is_self': is_self,
#                        'job_preference': job_preference,'job_preference_other': job_preference_other})
#     else:
#         return HttpResponse('Requested User Not Found')

# def get_city(request):
#     term = request.GET.get('term')
#     print('\n\nterm >>>>>>', term)
#     cities = models.City.objects.all().filter(city_name__icontains=term)
#     return JsonResponse(list(cities.values()), safe=False)


from django.db.models import Count, Sum


@login_required(login_url="/")
def toggle_field_state(request):
    element_tag = request.GET.get('name')
    # print("taaaaaag", element_tag)
    # print(request.user)
    active_profile = models.Profile.objects.get(id=request.session['active_profile_id'])
    candidatehidefields = models.Candidate_Hide_Fields.objects.get(candidate_id=request.user, profile_id=active_profile)
    if element_tag == 'email':
        if candidatehidefields.email == 0:
            candidatehidefields.email = 1
        elif candidatehidefields.email == 1:
            candidatehidefields.email = 0
        candidatehidefields.save()
        return HttpResponse(candidatehidefields.email)

    elif element_tag == 'exp_document':
        if candidatehidefields.exp_document == 0:
            candidatehidefields.exp_document = 1
        elif candidatehidefields.exp_document == 1:
            candidatehidefields.exp_document = 0
        candidatehidefields.save()
        return HttpResponse(candidatehidefields.edu_document)

    elif element_tag == 'edu_document':
        if candidatehidefields.edu_document == 0:
            candidatehidefields.edu_document = 1
        elif candidatehidefields.edu_document == 1:
            candidatehidefields.edu_document = 0
        candidatehidefields.save()
        return HttpResponse(candidatehidefields.edu_document)

    elif element_tag == 'certificate_document':
        if candidatehidefields.certificate_document == 0:
            candidatehidefields.certificate_document = 1
        elif candidatehidefields.certificate_document == 1:
            candidatehidefields.certificate_document = 0
        candidatehidefields.save()
        return HttpResponse(candidatehidefields.certificate_document)

    elif element_tag == 'portfolio_document':
        if candidatehidefields.portfolio_document == 0:
            candidatehidefields.portfolio_document = 1
        elif candidatehidefields.portfolio_document == 1:
            candidatehidefields.portfolio_document = 0
        candidatehidefields.save()
        return HttpResponse(candidatehidefields.portfolio_document)

    elif element_tag == 'contact':
        if candidatehidefields.contact == 0:
            candidatehidefields.contact = 1
        elif candidatehidefields.contact == 1:
            candidatehidefields.contact = 0
        candidatehidefields.save()
        return HttpResponse(candidatehidefields.contact)

        # candidatehidefields.save()
    # print("emaiiiiiiillllllll",candidatehidefields.email)
    # print("iddd",request.user.id)
    # print(candidatehidefields)
    # return HttpResponse(candidatehidefields.email)    


@login_required(login_url="/")
def add_profile(request):
    # print("heeeeeeelllllasdaslo")

    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    # print(random_string)
    #    all_profiles = models.Profile.objects.filter(candidate_id=User.objects.get(id=request.user.id))
    #    for m in all_profiles:
    #       m.active = False
    #      m.update_at=datetime.datetime.now()
    #     m.save()
    profile = models.Profile.objects.create(candidate_id=User.objects.get(id=request.user.id), url=random_string)
    print('\n\n\nprofile obj', profile)
    candidatehidefield = models.Candidate_Hide_Fields.objects.create(candidate_id=User.objects.get(id=request.user.id),
                                                                     profile_id=profile)
    request.session['profile_id'] = profile.id
    return redirect('candidate:upload_resume_add', url=random_string)


@login_required(login_url="/")
def add_profile_detail(request, url):
    return redirect('candidate:home')


@login_required(login_url="/")
def toggle_profile(request):
    profile_id = request.GET.get('id')
    # print("profille  iddddddddddddddddddddddddd", profile_id)
    profiles = models.Profile.objects.filter(candidate_id=request.user)
    # print(profiles)
    for i in profiles:
        if int(i.id) == int(profile_id):
            i.active = True
            i.update_at = datetime.datetime.now()
            del request.session['active_profile_id']
            request.session['active_profile_id'] = i.id

        else:
            i.active = False
            i.update_at = datetime.datetime.now()
        i.save()
    active_p = models.Profile.objects.get(candidate_id=request.user, active=True)
    q = Elastic_Q('multi_match', query=active_p.candidate_id.email, fields=['email'])
    s = CandidateDocument.search().query(q).extra(size=10000)
    for hit in s:
        # print("emaioil", hit.email)
        if User.objects.filter(email=hit.email).exists():
            user = User.objects.get(email=hit.email)
            try:
                hit.delete()
                user.indexing()
            except:
                print("indexing was not called ")
    return JsonResponse(list(profiles.values()), safe=False)


@login_required(login_url="/")
def edit_profile(request, profile_id):
    context = {}
    profile_obj = models.Profile.objects.get(id=profile_id)
    context['profileobj']=profile_obj
    user_id = User.objects.get(id=request.user.id)
    context['profile_id'] = profile_id
    request.session['profile_id'] = profile_id
    context['cities'] = models.City.objects.all()
    context['states'] = models.State.objects.all()
    context['country'] = models.Country.objects.all()
    context['months'] = models.Month.objects.all()
    context['Languages'] = models.Languages.objects.all()
    context['fluency'] = models.Fluency.objects.all()
    context['profile'] = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=profile_id)
    if context['profile'].custom_url:
        context['url_link']=context['profile'].custom_url
    else:
        context['url_link']=context['profile'].url_name
    context['experience'] = models.CandidateExperience.objects.filter(candidate_id=user_id,
                                                                      profile_id=profile_id).order_by('record_id')
    context['education'] = models.CandidateEducation.objects.filter(candidate_id=user_id,
                                                                    profile_id=profile_id).order_by('record_id')
    context['portfolios'] = models.CandidatePortfolio.objects.filter(candidate_id=user_id,
                                                                     profile_id=profile_id).order_by('record_id')
    context['certificates'] = models.CandidateCertificationAttachment.objects.filter(candidate_id=user_id,
                                                                                     profile_id=profile_id).order_by(
        'record_id')
    context['awards'] = models.CandidateAward.objects.filter(candidate_id=user_id, profile_id=profile_id).order_by(
        'record_id')
    context['c_language'] = models.CandidateLanguage.objects.filter(candidate_id=user_id,
                                                                    profile_id=profile_id).order_by('record_id')
    context['skills'] = models.CandidateSkillUserMap.objects.filter(candidate_id=user_id,
                                                                    profile_id=profile_id).order_by('record_id')
    context['social_network'] = models.CandidateSocialNetwork.objects.filter(candidate_id=user_id,
                                                                             profile_id=profile_id).order_by(
        'record_id')
    context['exp_years'] = [str(yearrange) if yearrange <= 30 else '30+' for yearrange in range(32)]
    context['exp_months'] = [str(i) for i in range(12)]
    context['industry_type'] = models.IndustryType.objects.all()
    context['notice_period'] = models.NoticePeriod.objects.all()
    context['maritial_type'] = models.MaritalType.objects.all()
    context['gender'] = models.Gender.objects.all()
    context['preferred_cities'] = []
    context['education_gaps'] = models.Gap.objects.filter(type="education", profile_id=profile_obj)
    context['experience_gaps'] = models.Gap.objects.filter(type="experience", profile_id=profile_obj)

    if context['profile'].preferred_cities:
        for city_id in context['profile'].preferred_cities.split(","):
            city_obj = models.City.objects.get(id=city_id)
            context['preferred_cities'].append({'id': city_obj.id, 'city_name': city_obj.city_name})
            # context['candidate_selected_cities'] = candidate_selected_cities

    if request.method == 'POST':
        if request.POST.get('model_name') == 'personal_details':
            # print(request.POST)
            user_id.first_name = request.POST.get('firstname')
            user_id.last_name = request.POST.get('lastname')
            user_id.save()
            candidate_profile = models.CandidateProfile.objects.filter(candidate_id=user_id, profile_id=profile_obj)
            candidate_profile.update(dob=request.POST.get('dob'),
                                     contact_no=request.POST.get('number'),
                                     gender=models.Gender.objects.get(id=request.POST.get('gender')),
                                     marital_status=models.MaritalType.objects.get(
                                         id=request.POST.get('marital_status')),
                                     designation=request.POST.get('designation'),
                                     total_experience=float(
                                         request.POST.get('total_experience_year') + '.' + request.POST.get(
                                             'total_experience_month')),
                                     notice_period=models.NoticePeriod.objects.get(
                                         id=request.POST.get('notice_period')),
                                     technical_knowledge=request.POST.get('technical-knowledge'),
                                     about_me=request.POST.get('about-me'),
                                     current_salary=request.POST.get('current_salary'))
            if request.POST.get('country'):
                candidate_profile.update(country=models.Country.objects.get(id=request.POST.get('country')))

            try:
                candidate_profile.update(state=models.State.objects.get(id=request.POST.get('state')))

            except:
                candidate_profile.update(state=None)

            try:
                candidate_profile.update(city=models.City.objects.get(id=request.POST.get('city')))

            except:
                candidate_profile.update(city=None)

            # print(candidate_profile)

            if request.POST.get('salary_checkbox'):
                models.CandidateProfile.objects.filter(candidate_id=user_id, profile_id=profile_obj).update(
                    expected_salary_min='As Per Company',
                    expected_salary_max='As Per Company')
            else:
                models.CandidateProfile.objects.filter(candidate_id=user_id, profile_id=profile_obj).update(
                    expected_salary_min=request.POST.get('expected_salary_min'),
                    expected_salary_max=request.POST.get('expected_salary_max'))

            candidate_profile = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=profile_obj)
            # print("final candidate profile is",candidate_profile)
            context['profile'] = candidate_profile
            # print("context profile is",context['profile'])
            if request.FILES.get('user_image'):
                # for i in candidate_profile:
                candidate_profile.user_image = request.FILES.get('user_image')
                candidate_profile.save()
                context['profile'] = candidate_profile
                # print("context in file is",context['profile'])

        if request.POST.get('model_name') == 'experience':
            # print("\n\nrequuuuuuuuuuuuuest\n\n\n",request.POST)

            exp_start_month = models.Month.objects.get(id=request.POST.get('exp_start_month'))
            # print("============================>",exp_start_month)
            exp_start_date = exp_start_month.name + "," + " " + request.POST.get('exp_start_year')
            if request.POST.get('exp_current_checkbox1'):
                exp_end_date = 'present'
                end_salary = 'present'
            else:
                end_salary = request.POST.get('endSalary')
                exp_end_month = models.Month.objects.get(id=request.POST.get('exp_end_month'))
                exp_end_date = exp_end_month.name + "," + " " + request.POST.get('exp_end_year')

            company, created = models.Company.objects.get_or_create(
                company_name=request.POST.get('company-name'),
                defaults={'company_name': request.POST.get('company-name')},
            )
            try:
                experience = models.CandidateExperience.objects.get(candidate_id=user_id, profile_id=profile_id,
                                                                    record_id=request.POST.get('record_id'))
            except:
                experience = None

            # print("expereince is ",experience)
            # print("created value is",created)
            if experience:
                old_company = experience.company.company_name
                if created:
                    # print("something was created")
                    # print("media root is ",settings.MEDIA_ROOT)
                    path = settings.MEDIA_ROOT + "{}/Candidate_Experience/{}".format(experience.candidate_id.id,
                                                                                     company.company_name)
                    # print("paaaaaath",path,os.path.exists(path))
                    # print("does folder exist")
                    if not os.path.exists(path):
                        os.makedirs(path)
                    exp_docs = models.CandidateExpDocuments.objects.filter(candidate_exp_id=experience)
                    for i in exp_docs:
                        file_path = i.exp_document.name
                        file_name = file_path.split('/')
                        file_name = file_name[-1]

                        abs_path = i.exp_document.name

                        # print("\n\n\nabs path>>>>>>>>>>>>>>>>>>>.",abs_path)
                        # print("path",path)
                        shutil.move(abs_path, path)
                        i.exp_document.name = path + '/{}'.format(file_name)
                        i.save()
                        abs_path = abs_path[:len(abs_path) - len(file_name)]

                    try:
                        os.rmdir(abs_path)
                    except:
                        print("there were some files in the folder")

                else:
                    if experience.company.company_name != request.POST.get('company-name'):
                        path = settings.MEDIA_ROOT + "{}/Candidate_Experience/{}".format(experience.candidate_id.id,
                                                                                         request.POST.get(
                                                                                             'company-name'))

                        if not os.path.exists(path):
                            os.makedirs(path)
                        exp_docs = models.CandidateExpDocuments.objects.filter(candidate_exp_id=experience)
                        for i in exp_docs:
                            file_path = i.exp_document.name
                            file_name = file_path.split('/')
                            file_name = file_name[-1]

                            abs_path = i.exp_document.name
                            # print("\n\n\nabs path",abs_path)
                            # print("path",path)
                            shutil.move(abs_path, path)

                            i.exp_document.name = path + '/{}'.format(file_name)
                            i.save()
                            abs_path = abs_path[:len(abs_path) - len(file_name)]
                        try:
                            os.rmdir(abs_path)
                        except:
                            print("there were some files in the folder")

                models.CandidateExperience.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                          record_id=request.POST.get('record_id')).update(
                    job_profile_name=request.POST.get('job-name'), company=company,
                    start_date=exp_start_date,
                    end_date=exp_end_date, start_salary=request.POST.get('startSalary'),
                    end_salary=end_salary, job_description_responsibility=request.POST.get('job_desc'),
                    website=request.POST.get('website-name'), update_at=datetime.datetime.now())

                exp_documents = models.CandidateExpDocuments.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                                            record_id=request.POST.get('record_id'))

                # print("experience is ",experience)
                # print(exp_documents)
                for i in range(exp_documents.count()):
                    temp = exp_documents[i]

                    file_name = 'exp_docs_' + str(temp.id)
                    file = request.FILES.get(file_name)
                    # print("FILE IS ",file)
                    if file:
                        temp.exp_document.delete(save=True)
                        temp.exp_document = file
                        temp.save()
            else:

                experience = models.CandidateExperience.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                                                       record_id=request.POST.get('record_id'),
                                                                       job_profile_name=request.POST.get('job-name'),
                                                                       company=company,
                                                                       start_date=exp_start_date,
                                                                       end_date=exp_end_date,
                                                                       start_salary=request.POST.get('startSalary'),
                                                                       end_salary=request.POST.get('endSalary'),
                                                                       job_description_responsibility=request.POST.get(
                                                                           'job_desc'),
                                                                       website=request.POST.get('website-name'),
                                                                       update_at=datetime.datetime.now(),
                                                                       create_at=datetime.datetime.now(),
                                                                       final_status=True
                                                                       )

            files = request.FILES.getlist('exp_docs_new')
            names = request.POST.getlist('exp_docs_name')
            # print('names',names)
            # print("files ",files)
            # print("==================>",experience)
            record_ids = models.CandidateExpDocuments.objects.filter(candidate_exp_id=experience).values_list(
                'record_id', flat=True)
            # print("record ids",record_ids)

            if record_ids:
                max_record_id = int(max(record_ids))
            else:
                max_record_id = 0
            # print("max ")
            count = 0
            for (file_name, file) in zip(names, files):
                count += 1
                models.CandidateExpDocuments.objects.create(candidate_id=user_id,
                                                            profile_id=profile_obj,
                                                            record_id=max_record_id + count,
                                                            candidate_exp_id=experience,
                                                            exp_document=file,
                                                            document_name=file_name
                                                            )

        if request.POST.get('model_name') == 'portfolio':
            # print(request.POST)
            try:
                portfolio = models.CandidatePortfolio.objects.get(candidate_id=user_id, profile_id=profile_id,
                                                                  record_id=request.POST.get('record_id'))
            except:
                portfolio = None

            if portfolio:
                # print('\n\n\nproject_year', request.POST.get('project_year'))
                old_project_title = portfolio.project_title
                if portfolio.project_title != request.POST.get('project-title'):
                    # portfolio.project_title = request.POST.get('project-title')
                    # portfolio.save()
                    path = settings.MEDIA_ROOT + "{}/Candidate_Portfolio/{}".format(portfolio.candidate_id.id,
                                                                                    request.POST.get('project-title'))
                    if not os.path.exists(path):
                        os.makedirs(path)

                    file_path = portfolio.project_document.name
                    file_name = file_path.split('/')
                    file_name = file_name[-1]

                    abs_path = portfolio.project_document.name
                    # print("abs path ",abs_path)
                    # print("path ",path)
                    shutil.move(abs_path, path)
                    portfolio.project_document.name = path + '/{}'.format(file_name)
                    portfolio.save()
                    abs_path = abs_path[:len(abs_path) - len(file_name)]
                    # print("updated path is ",abs_path)
                    os.rmdir(abs_path)
                # print("update was callllleed")
                portfolios = models.CandidatePortfolio.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                                      record_id=request.POST.get('record_id'))
                # print("the queryset is ",portfolios)
                portfolios.update(
                    project_title=request.POST.get('project-title'), link=request.POST.get('project_website1'),
                    year=request.POST.get('project_year'), description=request.POST.get('project_description'),
                    learning_from_project=request.POST.get('learning_from_project'), update_at=datetime.datetime.now())

                file_name = "portfolio_docs_" + str(portfolio.id)
                # print("file_name is ",file_name)
                file = request.FILES.get(file_name)
                # print("the file in request post portfolio is",file)
                for i in portfolios:
                    if file:
                        i.project_document.delete(save=True)
                        i.project_document = file
                        i.save()
            else:
                models.CandidatePortfolio.objects.create(candidate_id=user_id,
                                                         profile_id=profile_obj,
                                                         record_id=request.POST.get('record_id'),
                                                         project_title=request.POST.get('project-title'),
                                                         link=request.POST.get('project_website1'),
                                                         year=request.POST.get('project_year'),
                                                         description=request.POST.get('project_description'),
                                                         learning_from_project=request.POST.get(
                                                             'learning_from_project'),
                                                         create_at=datetime.datetime.now(),
                                                         update_at=datetime.datetime.now(),
                                                         project_document=request.FILES.get('portfolio_docs_new'))

        if request.POST.get('model_name') == 'education':
            # print("MEEEEEEEEEEEEEEEEEEEEEDIAAAAAAAAAA",settings.MEDIA_ROOT)
            university, created = models.UniversityBoard.objects.get_or_create(
                name=request.POST.get('university_board'),
                defaults={'name': request.POST.get('university_board')},
            )
            degree, created = models.Degree.objects.get_or_create(
                name=request.POST.get('degree-name'), defaults={'name': request.POST.get('degree-name')})

            try:
                education = models.CandidateEducation.objects.get(candidate_id=user_id, profile_id=profile_id,
                                                                  record_id=request.POST.get('record_id'))
            except:
                education = None

            edu_start_month = models.Month.objects.get(id=request.POST.get('edu_start_month'))
            edu_end_month = models.Month.objects.get(id=request.POST.get('edu_end_month'))
            edu_start_date = edu_start_month.name + "," + " " + request.POST.get('edu_start_year')
            edu_end_date = edu_end_month.name + "," + " " + request.POST.get('edu_end_year')

            if education:

                old_degree = education.degree.name
                if created:

                    # print("something was created")
                    # print("media root is ",settings.MEDIA_ROOT)
                    path = settings.MEDIA_ROOT + "{}/Candidate_Education/{}".format(education.candidate_id.id,
                                                                                    degree.name)
                    # print("paaaaaath",path,os.path.exists(path))
                    # print("does folder exist")
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file_path = education.certificate.name
                    file_name = file_path.split('/')
                    file_name = file_name[-1]

                    abs_path = education.certificate.name

                    # print("abs path",abs_path)
                    # print("path",path)
                    shutil.move(abs_path, path)
                    education.certificate.name = path + '/{}'.format(file_name)
                    education.save()
                    abs_path = abs_path[:len(abs_path) - len(file_name)]
                    os.rmdir(abs_path)
                else:
                    if education.degree.name != request.POST.get('degree-name'):
                        path = settings.MEDIA_ROOT + "{}/Candidate_Education/{}".format(education.candidate_id.id,
                                                                                        request.POST.get('degree-name'))

                        if not os.path.exists(path):
                            os.makedirs(path)
                        file_path = education.certificate.name
                        file_name = file_path.split('/')
                        file_name = file_name[-1]

                        abs_path = education.certificate.name

                        # print("abs path",abs_path)
                        # print("path",path)
                        shutil.move(abs_path, path)
                        education.certificate.name = path + '/{}'.format(file_name)
                        education.save()
                        abs_path = abs_path[:len(abs_path) - len(file_name)]
                        os.rmdir(abs_path)

                educations = models.CandidateEducation.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                                      record_id=request.POST.get('record_id'))
                educations.update(
                    university_board=university, degree=degree, start_date=edu_start_date,
                    end_date=edu_end_date, summary=request.POST.get('summary'),
                    update_at=datetime.datetime.now(), grade=request.POST.get('edu_grade'))

                # educations = models.CandidateEducation.objects.filter(candidate_id=user_id, profile_id=profile_id,
                #                                          record_id=request.POST.get('record_id'))

                file_name = 'edu_docs_' + str(education.id)
                file = request.FILES.get(file_name)

                for i in educations:
                    if file:
                        i.certificate.delete(save=True)
                        i.certificate = file
                        i.save()
                # for i in educations:
                #     file_name = 'edu_docs_'+str(i.id)
                #     print("file_name",file_name)
                #     file = request.FILES.get(file_name)
                #     print("file",file)
                #     if file:
                #         i.certificate = file
                #         i.save()
            else:
                models.CandidateEducation.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                                         record_id=request.POST.get('record_id'),
                                                         university_board=university,
                                                         degree=degree,
                                                         start_date=edu_start_date,
                                                         end_date=edu_end_date,
                                                         summary=request.POST.get('summary'),
                                                         create_at=datetime.datetime.now(),
                                                         update_at=datetime.datetime.now(),
                                                         grade=request.POST.get('edu_grade'),
                                                         certificate=request.FILES.get('edu_docs_new'),
                                                         final_status=True)

        if request.POST.get('model_name') == 'certificate':
            # print("POOOOOST ",request.POST)
            # print("fiiiiiiiiiiiles",request.FILES)
            certificate_obj = models.CandidateCertificationAttachment.objects.filter(candidate_id=user_id,
                                                                                     profile_id=profile_id,
                                                                                     record_id=request.POST.get(
                                                                                         'record_id'))
            if certificate_obj.exists():

                for i in certificate_obj:
                    if i.name_of_certificate != request.POST.get('certificate-name'):
                        old_certificate_name = i.name_of_certificate
                        path = settings.MEDIA_ROOT + '{}/Candidate_Certificate/{}'.format(i.candidate_id.id,
                                                                                          request.POST.get(
                                                                                              'certificate-name'))

                        if not os.path.exists(path):
                            os.makedirs(path)

                        file_path = i.attached_certificate.name
                        file_name = file_path.split('/')
                        file_name = file_name[-1]

                        abs_path = i.attached_certificate.name
                        # print("abs path ",abs_path)
                        # print("path ",path)
                        shutil.move(abs_path, path)
                        i.attached_certificate.name = path + '/{}'.format(file_name)
                        i.save()
                        abs_path = abs_path[:len(abs_path) - len(file_name)]
                        # print("updated path is ",abs_path)
                        os.rmdir(abs_path)

                certificates = models.CandidateCertificationAttachment.objects.filter(candidate_id=user_id,
                                                                                      profile_id=profile_id,
                                                                                      record_id=request.POST.get(
                                                                                          'record_id'))
                certificates.update(name_of_certificate=request.POST.get('certificate-name'),
                                    institute_organisation=request.POST.get('certificate-organization'),
                                    year=request.POST.get('certificate-year'),
                                    summary=request.POST.get('certificate-summary'),
                                    update_at=datetime.datetime.now())

                if request.FILES.get('certificate-file'):
                    for i in certificates:
                        i.attached_certificate.delete(save=True)
                        i.attached_certificate = request.FILES.get('certificate-file')
                        i.save()
            else:
                certificate_obj.create(candidate_id=user_id, profile_id=profile_obj,
                                       record_id=request.POST.get('record_id'),
                                       name_of_certificate=request.POST.get('certificate-name'),
                                       institute_organisation=request.POST.get('certificate-organization'),
                                       year=request.POST.get('certificate-year'),
                                       attached_certificate=request.FILES.get('certificate-file'),
                                       summary=request.POST.get('certificate-summary'))
        if request.POST.get('model_name') == 'award':
            award_obj = models.CandidateAward.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                             record_id=request.POST.get('record_id'))
            if award_obj.exists():
                award_obj.update(title=request.POST.get('award-name'), year=request.POST.get('award-year'),
                                 awarder=request.POST.get('award-awarder'), update_at=datetime.datetime.now())
            else:
                models.CandidateAward.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                                     record_id=request.POST.get('record_id'),
                                                     title=request.POST.get('award-name'),
                                                     year=request.POST.get('award-year'),
                                                     awarder=request.POST.get('award-awarder'))
        if request.POST.get('model_name') == 'language':
            language_id = models.Languages.objects.get(id=request.POST.get('language'))
            fluency_id = models.Fluency.objects.get(id=request.POST.get('fluency'))
            language_obj = models.CandidateLanguage.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                                   record_id=request.POST.get('record_id'))
            if language_obj.exists():
                language_obj.update(language_id=language_id, fluency_id=fluency_id)
            else:
                models.CandidateLanguage.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                                        record_id=request.POST.get('record_id'),
                                                        language_id=language_id, fluency_id=fluency_id)
        if request.POST.get('model_name') == 'skill':
            skill_id, created = models.Skill.objects.get_or_create(name=request.POST.get('skill-name'))
            skill_obj = models.CandidateSkillUserMap.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                                    record_id=request.POST.get('record_id'))
            if skill_obj.exists():
                skill_obj.update(skill=skill_id, total_exp=request.POST.get('skill_total_experience'),
                                 last_used=request.POST.get('skill-last-used'))
            else:
                models.CandidateSkillUserMap.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                                            record_id=request.POST.get('record_id'), skill=skill_id,
                                                            total_exp=request.POST.get('skill_total_experience'),
                                                            last_used=request.POST.get('skill-last-used'))
        if request.POST.get('model_name') == 'social':
            print("\n\n\n\npoooost", request.POST)
            social_obj = models.CandidateSocialNetwork.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                                      record_id=request.POST.get('record_id'))
            if social_obj.exists():
                social_obj.update(
                    network_name=request.POST.get('network_name'),
                    url=request.POST.get('network-url'), update_at=datetime.datetime.now())
            else:
                models.CandidateSocialNetwork.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                                             record_id=request.POST.get('record_id'),
                                                             network_name=request.POST.get('network_name'),
                                                             url=request.POST.get('network-url'),
                                                             update_at=datetime.datetime.now())
        if request.POST.get('model_name') == 'education_gap':
            print("\n\n\n\npoooost", request.POST)
            gap_obj = models.Gap.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                record_id=request.POST.get('record_id'), type="education")
            print("asasdasdasd", gap_obj)
            # social_obj = models.CandidateSocialNetwork.objects.filter(candidate_id=user_id, profile_id=profile_id,record_id=request.POST.get('record_id'))

            if gap_obj.exists():
                gap_obj.update(
                    start_date=models.Month.objects.get(
                        id=request.POST.get('edu_gap_start_month')).name + ", " + request.POST.get(
                        'edu_gap_start_year'),
                    end_date=models.Month.objects.get(
                        id=request.POST.get('edu_gap_end_month')).name + ", " + request.POST.get('edu_gap_end_year'),
                    reason=request.POST.get('edu_gap_reason'))
            else:
                models.Gap.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                          record_id=request.POST.get('record_id'),
                                          start_date=models.Month.objects.get(id=request.POST.get(
                                              'edu_gap_start_month')).name + ", " + request.POST.get(
                                              'edu_gap_start_year'),
                                          end_date=models.Month.objects.get(
                                              id=request.POST.get('edu_gap_end_month')).name + ", " + request.POST.get(
                                              'edu_gap_end_year'),
                                          reason=request.POST.get('edu_gap_reason'),
                                          type="education")
        if request.POST.get('model_name') == 'experience_gap':
            print("\n\n\n\npoooost", request.POST)
            gap_obj = models.Gap.objects.filter(candidate_id=user_id, profile_id=profile_id,
                                                record_id=request.POST.get('record_id'), type="experience")
            print("asasdasdasd", gap_obj)
            # social_obj = models.CandidateSocialNetwork.objects.filter(candidate_id=user_id, profile_id=profile_id,record_id=request.POST.get('record_id'))

            if gap_obj.exists():
                gap_obj.update(
                    start_date=models.Month.objects.get(
                        id=request.POST.get('exp_gap_start_month')).name + ", " + request.POST.get(
                        'exp_gap_start_year'),
                    end_date=models.Month.objects.get(
                        id=request.POST.get('exp_gap_end_month')).name + ", " + request.POST.get('exp_gap_end_year'),
                    reason=request.POST.get('exp_gap_reason'))
            else:
                models.Gap.objects.create(candidate_id=user_id, profile_id=profile_obj,
                                          record_id=request.POST.get('record_id'),
                                          start_date=models.Month.objects.get(id=request.POST.get(
                                              'exp_gap_start_month')).name + ", " + request.POST.get(
                                              'exp_gap_start_year'),
                                          end_date=models.Month.objects.get(
                                              id=request.POST.get('exp_gap_end_month')).name + ", " + request.POST.get(
                                              'exp_gap_end_year'),
                                          reason=request.POST.get('exp_gap_reason'),
                                          type="experience")
    return render(request, 'candidate/candidate_profile_edit.html', context)


@login_required(login_url="/")
def candidate_job_preference(request):
    if request.is_ajax():
        term = request.GET.get('term')
        cities = models.City.objects.all().filter(city_name__icontains=term)
        return JsonResponse(list(cities.values()), safe=False)
    candidate_id = models.User.objects.get(id=request.user.id)
    context = {}
    context['seo'] = models.CandidateSEO.objects.get(candidate_id=request.user.id)
    if models.CandidateJobPreference.objects.filter(candidate_id=candidate_id).exists():
        context['candidate_preference_exist'] = True
        context['candidate_preference_get'] = models.CandidateJobPreference.objects.get(candidate_id=candidate_id)
        context['candidate_preference_other_get'] = models.CandidateJobPreferenceOther.objects.filter(
            candidate_id=candidate_id)
        candidate_selected_cities = []
        if context['candidate_preference_get'].relocation_cities:
            for city_id in context['candidate_preference_get'].relocation_cities.split(","):
                city_obj = models.City.objects.get(id=city_id)
                candidate_selected_cities.append({'id': city_obj.id, 'city_name': city_obj.city_name})
            context['candidate_selected_cities'] = candidate_selected_cities
    else:
        context['candidate_preference_exist'] = False
    context['job_types'] = models.CandidateJobPreference.job_type_choices
    context['number_of_employee'] = models.CandidateJobPreference.number_of_employee_choices
    context['working_day_types'] = models.CandidateJobPreference.working_day_choices
    context['preferred_shift_types'] = models.CandidateJobPreference.preferred_shift_choices
    if request.method == 'POST':
        print('================')
        print('================', request.POST.get('no-of-employee'))
        if request.POST.get('relocate') == 'on':
            relocation = True
        else:
            relocation = False
        relocation_cities = ','.join(map(str, request.POST.getlist('relocation_cities')))
        models.CandidateJobPreference.objects.update_or_create(candidate_id=candidate_id,
                                                               defaults={'job_type': request.POST.get('job-type'),
                                                                         'number_of_employee': request.POST.get(
                                                                             'no-of-employee'),
                                                                         'working_days': request.POST.get(
                                                                             'working-day'),
                                                                         'preferred_shift': request.POST.get(
                                                                             'shift-type'), 'relocation': relocation,
                                                                         'relocation_cities': relocation_cities
                                                                         })
        models.CandidateJobPreferenceOther.objects.all().delete()
        for (label, value) in zip(request.POST.getlist('label'), request.POST.getlist('value')):
            models.CandidateJobPreferenceOther.objects.update_or_create(candidate_id=candidate_id, label=label,
                                                                        value=value,
                                                                        defaults={
                                                                            'label': label,
                                                                            'value': value,
                                                                        })
        return redirect('candidate:home')
    return render(request, 'candidate/Dashbord-preference.html', context)


from django.db.models import Count, Sum


@login_required(login_url="/")
def hire_request(request):
    seo = models.CandidateSEO.objects.get(candidate_id=request.user.id)
    active = CandidateHire.objects.filter(candidate_id=request.user.id, request_status=1).values('id', 'message',
                                                                                                 'company_id',
                                                                                                 'candidate_id',
                                                                                                 'profile_id')
    new_request = CandidateHire.objects.filter(candidate_id=request.user.id, request_status=0).values('id', 'message',
                                                                                                      'company_id',
                                                                                                      'candidate_id',
                                                                                                      'profile_id')
    archive = CandidateHire.objects.filter(candidate_id=request.user.id, request_status=-1).values('id', 'message',
                                                                                                   'company_id',
                                                                                                   'candidate_id',
                                                                                                   'profile_id')
    print('========================', new_request)
    data_active = models.company_data_request.objects.filter(candidate_id=request.user.id, status=1).values('id',
                                                                                                            'message',
                                                                                                            'company_id',
                                                                                                            'candidate_id',
                                                                                                            'profile_id')
    data_new_request = models.company_data_request.objects.filter(candidate_id=request.user.id, status=0).values('id',
                                                                                                                 'message',
                                                                                                                 'company_id',
                                                                                                                 'candidate_id',
                                                                                                                 'profile_id')
    data_archive = models.company_data_request.objects.filter(candidate_id=request.user.id, status=-2).values('id',
                                                                                                              'message',
                                                                                                              'company_id',
                                                                                                              'candidate_id',
                                                                                                              'profile_id')
    print('========================', data_new_request)
    profile_get = models.Profile.objects.get(candidate_id=request.user.id, active=True)
    userdata = models.CandidateProfile.objects.get(candidate_id=request.user.id, profile_id=profile_get.id)
    return render(request, 'candidate/Dashbord-request.html',
                  {'userdata': userdata, 'seo': seo, 'active': active, 'new_request': new_request, 'archive': archive,
                   'data_active': data_active, 'data_new_request': data_new_request, 'data_archive': data_archive})


@login_required(login_url="/")
def accept_request(request, profile_id, company_id, hire_id):
    if request.method == "POST":
        # MessageModel.objects.create(user=User.objects.get(id=request.user.id),recipient=User.objects.get(id=company_id),body=request.POST.get('accept_message'),request_status=1)
        status_true = Messages.objects.filter(
            Q(sender_name=User.objects.get(id=company_id), receiver_name=User.objects.get(id=request.user.id),
              status=False) | Q(sender_name=User.objects.get(id=request.user.id),
                                receiver_name=User.objects.get(id=company_id), status=False))
        for i in status_true:
            i.status = True
            i.save()
        Messages.objects.create(sender_name=User.objects.get(id=request.user.id),
                                receiver_name=User.objects.get(id=company_id),
                                description=request.POST.get('accept_message'), status=True)
        CandidateHire.objects.filter(id=hire_id, candidate_id=request.user.id, company_id=company_id,
                                     profile_id=profile_id).update(request_status=1,
                                                                   message=request.POST.get('accept_message'))
        try:
            mail_subject = 'Accept Hire Request'
            html_content = render_to_string('accounts/candidate_hire_email.html',
                                            {'message': request.POST.get('accept_message')})
            to_email = User.objects.filter(id=company_id).values('email')[0]['email']
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # messages.sucess(request, 'Your account was inactive.')
            return redirect('candidate:hire_request')
        except BadHeaderError:
            print("email not send")
            messages.erroe(request, 'mail dose not send.')
            return redirect('candidate:hire_request')

    return redirect('candidate:hire_request')


@login_required(login_url="/")
def reject_request(request, profile_id, company_id, hire_id):
    if request.method == "POST":
        status_false = Messages.objects.filter(
            Q(sender_name=User.objects.get(id=company_id), receiver_name=User.objects.get(id=request.user.id),
              status=True) | Q(sender_name=User.objects.get(id=request.user.id),
                               receiver_name=User.objects.get(id=company_id), status=True))
        for i in status_false:
            i.status = False
            i.save()
        Messages.objects.create(sender_name=User.objects.get(id=request.user.id),
                                receiver_name=User.objects.get(id=company_id),
                                description=request.POST.get('reject_message'), status=False)
        CandidateHire.objects.filter(id=hire_id, candidate_id=request.user.id, company_id=company_id,
                                     profile_id=profile_id).update(request_status=-1,
                                                                   message=request.POST.get('reject_message'))
        try:
            mail_subject = 'Reject Hire Request'
            html_content = render_to_string('accounts/candidate_hire_email.html',
                                            {'message': request.POST.get('reject_message')})
            to_email = User.objects.filter(id=company_id).values('email')[0]['email']
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # messages.sucess(request, 'Your account was inactive.')
            return redirect('candidate:hire_request')
        except BadHeaderError:
            print("email not send")
            messages.erroe(request, 'mail dose not send.')
            return redirect('candidate:hire_request')

    return redirect('candidate:hire_request')


@login_required(login_url="/")
def data_accept_request(request, profile_id, company_id, data_id):
    if request.method == "POST":
        # MessageModel.objects.create(user=User.objects.get(id=request.user.id),recipient=User.objects.get(id=company_id),body=request.POST.get('accept_message'),request_status=1)
        models.company_data_request.objects.filter(id=data_id, candidate_id=request.user.id, company_id=company_id,
                                                   profile_id=profile_id).update(status=1, message=request.POST.get(
            'accept_message'))
    return redirect('candidate:hire_request')


@login_required(login_url="/")
def data_reject_request(request, profile_id, company_id, data_id):
    if request.method == "POST":
        # MessageModel.objects.create(user=User.objects.get(id=request.user.id),recipient=User.objects.get(id=company_id),body=request.POST.get('reject_message'),request_status=-1)
        models.company_data_request.objects.filter(id=data_id, candidate_id=request.user.id, company_id=company_id,
                                                   profile_id=profile_id).update(status=-2, message=request.POST.get(
            'reject_message'))
    return redirect('candidate:hire_request')


@login_required(login_url="/")
def charts(request):
    data = pd.read_csv("media/bar-chart.csv")
    json_data = data.to_json()

    print(data)

    print("json data", json_data)
    return render(request, 'candidate/chart-chartjs.html', {'json_data': json_data})


@login_required(login_url="/")
def save_resume(request):
    if request.method == 'POST':
        print('\n\n\ncandidate_resume', request.session['profile_id'])
        user_id = models.User.objects.get(email=request.user.email)
        profile = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=models.Profile.objects.get(
            id=request.session['profile_id']))
        profile.resume = request.FILES.get('candidate_resume')
        profile.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@login_required(login_url="/")
def create_resume_pass(request):
    if request.method == 'POST':
        # print('\n\n\ncreate_resume_pass', request.POST.get('resume-pass'), request.session['profile_id'])
        user_id = models.User.objects.get(email=request.user.email)
        password = make_password(request.POST.get('resume-pass'))
        profile = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=models.Profile.objects.get(
            id=request.session['profile_id']))
        profile.resume_password = password
        profile.save()
        return HttpResponse(True)


@login_required(login_url="/")
def update_resume_pass(request):
    if request.method == 'POST':
        # del request.session['active_profile_id']
        print('===============create_resume_pass', request.POST.get('resume-pass'),
              request.session['active_profile_id'])
        user_id = models.User.objects.get(email=request.user.email)
        password = make_password(request.POST.get('resume-pass'))
        profile = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=models.Profile.objects.get(
            id=request.session['active_profile_id']))
        profile.resume_password = password
        profile.save()
        return HttpResponse(True)


def update_share_url(request):
    print('\n\n\ncreate_url', request.POST.get('share-url'))
    user_id = models.User.objects.get(email=request.user.email)
    url_name = request.POST.get('share-url')
    profile = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=models.Profile.objects.get(
        id=request.session['active_profile_id']))
    profile.custom_url = url_name
    profile.save()
    qr_share_link = "https://bidcruit.com/" + url_name + "/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=4,
    )
    qr.add_data(qr_share_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    blob = BytesIO()
    img.save(blob, 'JPEG')
    profile.qr_code.save(request.user.first_name + '.jpg', File(blob), save=True)
    return HttpResponse(True)


def check_sharing_url_is_valid(request):
    url = request.POST.get("url")
    print('===============', url)
    regex = re.compile('[@!#$%^&*()<>?/\|}{~:]')
    if (regex.search(url) == None):
        user_obj = models.CandidateProfile.objects.filter(custom_url=url).exists()
        print('===============', user_obj)
        if user_obj:
            print('exit')
            return HttpResponse(True)
        else:
            print('not exit')
            return HttpResponse(False)
    else:
        return HttpResponse('Invalid')


def file_download(request):
    data = json.loads(request.body.decode('UTF-8'))

    if request.method == 'POST':
        print("#####", data)
        recored_id = data['id']
        candidate_id = data['candidate_id']
        profile_id = data['profile_id']
        password_12 = data['password']
        file_password_get = models.CandidateProfile.objects.get(id=recored_id,
                                                                candidate_id=User.objects.get(id=candidate_id),
                                                                profile_id=models.Profile.objects.get(id=profile_id))

        check_file_password = check_password(password_12, file_password_get.resume_password)

        if check_file_password:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    else:
        return HttpResponse(False)


def look_for_job_check(request):
    print('==============-----------=====================')
    seo_obj, created = models.CandidateSEO.objects.get_or_create(candidate_id=User.objects.get(id=request.user.id))
    seo_obj.looking_for_job = True if request.GET.get('look_for_job_check') == 'on' else False
    seo_obj.google_search = True if request.GET.get('google_search_check') == 'on' else False
    seo_obj.save()
    return HttpResponse(True)


# def timeline(request, url):
#     # get_url=models.CandidateProfile.objects.filter(url_name=url)
#     # if len(get_url)!=0:
#     #     return redirect('timeline',get_url[0].custom_url)
#     # else:
#     #     return redirect('timeline',url)
#     # dictonary to convert month to number
#     month = {'January': 1,
#              'February': 2,
#              'March': 3,
#              'April': 4,
#              'May': 5,
#              'June': 6,
#              'July': 7,
#              'August': 8,
#              'September': 9,
#              'October': 10,
#              'November': 11,
#              'December': 12
#              }
#     profile_id_get = models.CandidateProfile.objects.filter(Q(url_name=url)|Q(custom_url=url))[0]
#     activeprofile = models.Profile.objects.get(candidate_id=profile_id_get.candidate_id, active=True)
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     ip=''
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     try:
#         socket.inet_aton(ip)
#         ip_valid = True
#     except socket.error:
#         ip_valid = False
#     #----- check if ip adress is valid -----#
#     if ip_valid:
#         if not models.CandidateCounter.objects.filter(ip_address=ip).exists():
#             models.CandidateCounter.objects.create(candidate_id=profile_id_get.candidate_id,profile_id=models.Profile.objects.get(id=activeprofile.id),ip_address=ip)
#     hire = {}
#     looking_job = models.CandidateSEO.objects.get(candidate_id=activeprofile.candidate_id)
#     company_data_status = {}
#     # activeprofile=models.Profile.objects.get(id=profile_id_get.profile_id)
#     if activeprofile.active:
#         profile = profile_id_get.profile_id
#         candidate_id = ''
#         if request.user.is_authenticated:
#             print('asdddasddas')
#             if request.user.is_company:
#                 candidate_id = profile_id_get.candidate_id_id
#                 hire = CandidateHire.objects.filter(profile_id=activeprofile.id, candidate_id=candidate_id,
#                                                     company_id=User.objects.get(id=request.user.id))
#                 company_data_status = models.company_data_request.objects.filter(profile_id=activeprofile.id,
#                                                                                  candidate_id=candidate_id,
#                                                                                  company_id=User.objects.get(
#                                                                                      id=request.user.id))
#             elif request.user.is_candidate:
#                 candidate_id = request.user.id
#         else:
#             candidate_id = profile_id_get.candidate_id.id
#         user = User.objects.get(id=activeprofile.candidate_id.id)
#         count = 0
#         year_title_pairs = {}
#         print("before hide field")
#         print("user is ", user)
#         print("profile is ", profile)
#         hidefield = models.Candidate_Hide_Fields.objects.get(candidate_id=user, profile_id=profile)
#         profile_show = models.CandidateProfile.objects.get(candidate_id=user, profile_id=profile)
#         skills = models.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=profile)
#         start_years = []
#         end_years = []
#         skill_names = ''
#         last_used = 0
#         if skills:
#             for i in skills:
#                 if i.last_used == 'present':
#                     last_used = int(get_present_year())

#                 skill_names += i.skill.name + ','
#                 start_year = int(last_used) - int(i.total_exp)
#                 start_years.append(start_year)
#                 end_years.append(last_used)
#         year_salary_pair = []
#         company_names = []
#         exp_seq={}
#         experiences = models.CandidateExperience.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#         if experiences:
#             for i in experiences:
#                 company_names.append(i.company.company_name)
#                 end_salary = 0
#                 end_date = 0
#                 if i.end_date:
#                     salary_start_year = int(i.start_date.split(',')[1])
#                     salary_start_year += month[i.start_date.split(',')[0]] / 12
#                     salary_end_year = 0
#                     if i.end_date == 'present':
#                         end_date = int(get_present_year())
#                         salary_end_year = int(get_present_year())
#                         salary_end_year += month[get_present_month()] / 12
#                     else:
#                         end_date = int(i.end_date.split(',')[1])
#                     if i.end_salary == 'present':
#                         end_salary = i.start_salary
#                     year_salary_pair.append([salary_start_year, i.start_salary])
#                     year_salary_pair.append([salary_end_year, end_salary])
#                     if int(end_date) not in list(year_title_pairs.keys()):
#                         year_title_pairs[end_date] = []
#                         year_title_pairs[end_date].append(i)
#                         exp_seq[end_date] = []
#                         exp_seq[end_date].append(i)
#                     else:
#                         year_title_pairs[end_date].append(i)
#                         exp_seq[end_date].append(i)
#                 # year_title_pairs.add(i.end_date.split(',')[1],i.job_profile_name)
#         company_names = ','.join(company_names)
#         exp=dict(sorted(exp_seq.items(),reverse=True))
#         experiences =exp
#         educations = models.CandidateEducation.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#         edu_seq={}
#         if educations:
#             for i in educations:
#                 count += 1
#                 if i.end_date:
#                     if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
#                         year_title_pairs[int(i.end_date.split(',')[1])] = []
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#                         edu_seq[int(i.end_date.split(',')[1])] = []
#                         edu_seq[int(i.end_date.split(',')[1])].append(i)
#                     else:
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#                         edu_seq[int(i.end_date.split(',')[1])] = []
#                         edu_seq[int(i.end_date.split(',')[1])].append(i)
#         edu=dict(sorted(edu_seq.items(),reverse=True))
#         educations =edu
#         certificates = models.CandidateCertificationAttachment.objects.filter(candidate_id=user,
#                                                                               profile_id=activeprofile.id)
#         # cer_seq={}
#         # if certificates:
#         #     for i in certificates:
#         #         count += 1
#         #         if i.year:
#         #             if int(i.year) not in list(year_title_pairs.keys()):
#         #                 year_title_pairs[int(i.year)] = []
#         #                 year_title_pairs[int(i.year)].append(i)
#         #                 cer_seq[int(i.year)] = []
#         #                 cer_seq[int(i.year)].append(i)
#         #             else:
#         #                 year_title_pairs[int(i.year)].append(i)
#         #                 cer_seq[int(i.year)] = []
#         #                 cer_seq[int(i.year)].append(i)
#         # cer=dict(sorted(cer_seq.items(),reverse=True))
#         # certificates =cer
#         awards = models.CandidateAward.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#         # awrd_seq={}
#         # if awards:
#         #     for i in awards:
#         #         count += 1
#         #         if i.year:
#         #             if int(i.year) not in list(year_title_pairs.keys()):
#         #                 year_title_pairs[int(i.year)] = []
#         #                 year_title_pairs[int(i.year)].append(i)
#         #                 awrd_seq[int(i.year)] = []
#         #                 awrd_seq[int(i.year)].append(i)
#         #             else:
#         #                 year_title_pairs[int(i.year)].append(i)
#         #                 awrd_seq[int(i.year)] = []
#         #                 awrd_seq[int(i.year)].append(i)
#         # awad=dict(sorted(awrd_seq.items(),reverse=True))
#         # awards =awad
#         # print(hidefield.edu_document)
#         portfolio = models.CandidatePortfolio.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#         # port_seq={}
#         # if portfolio:
#         #     for i in portfolio:
#         #         count += 1
#         #         if i.year:
#         #             if int(i.year) not in list(year_title_pairs.keys()):
#         #                 year_title_pairs[int(i.year)] = []
#         #                 year_title_pairs[int(i.year)].append(i)
#         #                 port_seq[int(i.year)] = []
#         #                 port_seq[int(i.year)].append(i)
#         #             else:
#         #                 year_title_pairs[int(i.year)].append(i)
#         #                 port_seq[int(i.year)] = []
#         #                 port_seq[int(i.year)].append(i)
#         # port=dict(sorted(port_seq.items(),reverse=True))
#         # portfolio =port
#         gaps = models.Gap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#         print(gaps)
#         if gaps:
#             print("gaaaaaaaaaps ", gaps)
#             for i in gaps:
#                 print("enterrred for loop for jgaps")
#                 if i.end_date:
#                     if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
#                         print("ifffffffffffffffffffffffffffffffffffffffffffffff")
#                         year_title_pairs[int(i.end_date.split(',')[1])] = []
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)
#                     else:
#                         year_title_pairs[int(i.end_date.split(',')[1])].append(i)

#         print(year_title_pairs)
#         skills_show = models.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#     sorted_key_list = sorted(year_title_pairs)
#     sorted_key_list.reverse()
#     job_preference = models.CandidateJobPreference.objects.filter(candidate_id=user)
#     skills_keywoard = models.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
#     keywoard=[]
#     for i in skills_show:
#         keywoard.append(i.skill.name)
#     preferredcity=profile_show.preferred_cities.split(',')
#     preferredcity=list(filter(None,preferredcity))
#     # preferredcity=list(filter('0',preferredcity))
#     # preferredcity=list(filter(0,preferredcity))
#     for i in preferredcity:
#         city = models.City.objects.get(id=int(i))
#         keywoard.append(city.city_name)
#     keywoard = ",".join(keywoard)
#     share_url=""
#     if profile_show.url_name:
#         share_url=profile_show.url_name
#     about_me=''
#     if profile_show.about_me:
#         about_me=profile_show.about_me
#         clean = re.compile('<.*?>')
#         about_me=re.sub(clean, '', about_me)

#     return render(request,'candidate/profile-third.html',
#                   {'company_data_status':company_data_status,'about_me':about_me,'share_url':share_url,'keywoard':keywoard,'skills_show':skills_show,'looking_job':looking_job,'hire':hire,'profile':profile_id_get,'hidefield':hidefield,'profile_show':profile_show,'user':user,'experiences':experiences,'portfolios':portfolio,'educations':educations,'certificates':certificates,'awards':awards,'sorted_keys':sorted_key_list,'year_title_pairs':year_title_pairs,'start_years':start_years,'end_years':end_years,'skills':skill_names,'year_salary_pair':json.dumps(year_salary_pair),'company_names':company_names,'job_preference':job_preference})


def timeline(request, url):
    profile_id_get = models.CandidateProfile.objects.filter(Q(url_name=url) | Q(custom_url=url))[0]
    # dictonary to convert month to number
    month = {'January': 1,
             'February': 2,
             'March': 3,
             'April': 4,
             'May': 5,
             'June': 6,
             'July': 7,
             'August': 8,
             'September': 9,
             'October': 10,
             'November': 11,
             'December': 12
             }
    # profile_id_get = models.CandidateProfile.objects.filter(Q(url_name=url)|Q(custom_url=url))[0]
    activeprofile = models.Profile.objects.get(candidate_id=profile_id_get.candidate_id, active=True)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ''
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    try:
        socket.inet_aton(ip)
        ip_valid = True
    except socket.error:
        ip_valid = False
    # ----- check if ip adress is valid -----#
    if ip_valid:
        if not models.CandidateCounter.objects.filter(candidate_id=profile_id_get.candidate_id,
                                                      profile_id=models.Profile.objects.get(id=activeprofile.id),
                                                      ip_address=ip).exists():
            models.CandidateCounter.objects.create(candidate_id=profile_id_get.candidate_id,
                                                   profile_id=models.Profile.objects.get(id=activeprofile.id),
                                                   ip_address=ip)
    hire = {}
    looking_job = models.CandidateSEO.objects.get(candidate_id=activeprofile.candidate_id)
    company_data_status = {}
    # activeprofile=models.Profile.objects.get(id=profile_id_get.profile_id)
    if activeprofile.active:
        profile = profile_id_get.profile_id
        candidate_id = ''
        if request.user.is_authenticated:
            print('asdddasddas')
            if request.user.is_company:
                candidate_id = profile_id_get.candidate_id_id
                hire = CandidateHire.objects.filter(profile_id=activeprofile.id, candidate_id=candidate_id,
                                                    company_id=User.objects.get(id=request.user.id))
                company_data_status = models.company_data_request.objects.filter(profile_id=activeprofile.id,
                                                                                 candidate_id=candidate_id,
                                                                                 company_id=User.objects.get(
                                                                                     id=request.user.id))
            elif request.user.is_candidate:
                candidate_id = request.user.id
        else:
            candidate_id = profile_id_get.candidate_id.id
        user = User.objects.get(id=activeprofile.candidate_id.id)
        count = 0
        year_title_pairs = {}
        print("before hide field")
        print("user is ", user)
        print("profile is ", profile)
        hidefield = models.Candidate_Hide_Fields.objects.get(candidate_id=user, profile_id=profile)
        profile_show = models.CandidateProfile.objects.get(candidate_id=user, profile_id=profile)
        skills = models.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=profile)
        start_years = []
        end_years = []
        skill_names = ''
        if skills:
            for i in skills:
                if i.last_used == 'present':
                    last_used = int(get_present_year())
                else:
                    last_used = int(i.last_used)
                skill_names += i.skill.name + ','
                print("last useddd---------", last_used)
                print("exxaasdasas[---------", i.total_exp)
                start_year = last_used - int(i.total_exp)
                start_years.append(start_year)
                end_years.append(last_used)
        year_salary_pair = []
        company_names = []
        exp_seq = {}
        exp_pie_chart_companies = []
        exp_pie_chart_total_exp = []
        experiences = models.CandidateExperience.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        for i in experiences:
            exp_pie_chart_companies.append(i.company.company_name)
            start_date = datetime.datetime.strptime(i.start_date, '%B, %Y')
            if i.end_date == 'present':
                current_date = datetime.datetime.now().strftime('%B') + ', ' + datetime.datetime.now().strftime('%Y')
                end_date = datetime.datetime.strptime(current_date, '%B, %Y')
            else:
                end_date = datetime.datetime.strptime(i.end_date, '%B, %Y')
            difference = relativedelta(end_date, start_date)
            final_dif = str(difference.years) + '.' + str(difference.months)
            exp_pie_chart_total_exp.append(float(final_dif))

        exp_df = ''
        if experiences:
            q = experiences.values('start_date', 'end_date')
            exp_df = pd.DataFrame.from_records(q)
            exp_df['start_date'] = pd.to_datetime(exp_df.start_date, format='%B, %Y')
            now = datetime.datetime.now()
            now_date = now.strftime('%B') + ', ' + now.strftime('%Y')
            exp_df['end_date'] = exp_df['end_date'].apply(lambda x: now_date if x == "present" else x)
            exp_df['start_date'] = pd.to_datetime(exp_df.start_date, format='%B, %Y')
            exp_df['type'] = 'experience'
            exp_df['end_date'] = pd.to_datetime(exp_df.end_date, format='%B, %Y')
            exp_df['s_year'] = pd.DatetimeIndex(exp_df['start_date']).year
            exp_df['e_year'] = pd.DatetimeIndex(exp_df['end_date']).year
            exp_df['s_month'] = pd.DatetimeIndex(exp_df['start_date']).month
            exp_df['e_month'] = pd.DatetimeIndex(exp_df['end_date']).month
            exp_df = exp_df.sort_values(by="start_date")
            exp_df = exp_df.rename(columns={'start_date': 'start', 'end_date': 'end'}, inplace=False)
            for i in experiences:
                company_names.append(i.company.company_name)
                end_salary = 0
                end_date = 0
                if i.end_date:
                    salary_start_year = int(i.start_date.split(',')[1])
                    salary_start_year += month[i.start_date.split(',')[0]] / 12
                    salary_end_year = 0
                    if i.end_date == 'present':
                        end_date = int(get_present_year())
                        salary_end_year = int(get_present_year())
                        salary_end_year += month[get_present_month()] / 12
                    else:
                        end_date = int(i.end_date.split(',')[1])
                        salary_end_year = int(end_date)
                        salary_end_year += month[i.end_date.split(',')[0]] / 12
                    if i.end_salary == 'present':
                        end_salary = i.start_salary
                    else:
                        end_salary = i.end_salary
                    year_salary_pair.append([salary_start_year, i.start_salary])
                    year_salary_pair.append([salary_end_year, end_salary])
                    if int(end_date) not in list(year_title_pairs.keys()):
                        year_title_pairs[end_date] = []
                        year_title_pairs[end_date].append(i)
                        exp_seq[end_date] = []
                        exp_seq[end_date].append(i)
                    else:
                        year_title_pairs[end_date].append(i)
                        exp_seq[end_date].append(i)
                # year_title_pairs.add(i.end_date.split(',')[1],i.job_profile_name)
        company_names = ','.join(company_names)
        exp = dict(sorted(exp_seq.items(), reverse=True))
        experiences = exp
        educations = models.CandidateEducation.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        edu_df = ''
        edu_seq = {}
        if educations:
            q = educations.values('start_date', 'end_date')
            edu_df = pd.DataFrame.from_records(q)
            edu_df['start_date'] = pd.to_datetime(edu_df.start_date, format='%B, %Y')
            now = datetime.datetime.now()
            now_date = now.strftime('%B') + ', ' + now.strftime('%Y')
            edu_df['end_date'] = edu_df['end_date'].apply(lambda x: now_date if x == "present" else x)
            edu_df['start_date'] = pd.to_datetime(edu_df.start_date, format='%B, %Y')
            edu_df['type'] = 'education'
            edu_df['end_date'] = pd.to_datetime(edu_df.end_date, format='%B, %Y')
            edu_df['s_year'] = pd.DatetimeIndex(edu_df['start_date']).year
            edu_df['e_year'] = pd.DatetimeIndex(edu_df['end_date']).year
            edu_df['s_month'] = pd.DatetimeIndex(edu_df['start_date']).month
            edu_df['e_month'] = pd.DatetimeIndex(edu_df['end_date']).month
            edu_df = edu_df.sort_values(by="start_date")
            edu_df = edu_df.rename(columns={'start_date': 'start', 'end_date': 'end'}, inplace=False)
            for i in educations:
                count += 1
                if i.end_date:
                    if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
                        year_title_pairs[int(i.end_date.split(',')[1])] = []
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
                        edu_seq[int(i.end_date.split(',')[1])] = []
                        edu_seq[int(i.end_date.split(',')[1])].append(i)
                    else:
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
                        edu_seq[int(i.end_date.split(',')[1])] = []
                        edu_seq[int(i.end_date.split(',')[1])].append(i)
        edu = dict(sorted(edu_seq.items(), reverse=True))
        educations = edu
        certificates = models.CandidateCertificationAttachment.objects.filter(candidate_id=user,
                                                                              profile_id=activeprofile.id)
        # cer_seq={}
        # if certificates:
        #     for i in certificates:
        #         count += 1
        #         if i.year:
        #             if int(i.year) not in list(year_title_pairs.keys()):
        #                 year_title_pairs[int(i.year)] = []
        #                 year_title_pairs[int(i.year)].append(i)
        #                 cer_seq[int(i.year)] = []
        #                 cer_seq[int(i.year)].append(i)
        #             else:
        #                 year_title_pairs[int(i.year)].append(i)
        #                 cer_seq[int(i.year)] = []
        #                 cer_seq[int(i.year)].append(i)
        # cer=dict(sorted(cer_seq.items(),reverse=True))
        # certificates =cer
        awards = models.CandidateAward.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        # awrd_seq={}
        # if awards:
        #     for i in awards:
        #         count += 1
        #         if i.year:
        #             if int(i.year) not in list(year_title_pairs.keys()):
        #                 year_title_pairs[int(i.year)] = []
        #                 year_title_pairs[int(i.year)].append(i)
        #                 awrd_seq[int(i.year)] = []
        #                 awrd_seq[int(i.year)].append(i)
        #             else:
        #                 year_title_pairs[int(i.year)].append(i)
        #                 awrd_seq[int(i.year)] = []
        #                 awrd_seq[int(i.year)].append(i)
        # awad=dict(sorted(awrd_seq.items(),reverse=True))
        # awards =awad
        # print(hidefield.edu_document)
        portfolio = models.CandidatePortfolio.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        # port_seq={}
        # if portfolio:
        #     for i in portfolio:
        #         count += 1
        #         if i.year:
        #             if int(i.year) not in list(year_title_pairs.keys()):
        #                 year_title_pairs[int(i.year)] = []
        #                 year_title_pairs[int(i.year)].append(i)
        #                 port_seq[int(i.year)] = []
        #                 port_seq[int(i.year)].append(i)
        #             else:
        #                 year_title_pairs[int(i.year)].append(i)
        #                 port_seq[int(i.year)] = []
        #                 port_seq[int(i.year)].append(i)
        # port=dict(sorted(port_seq.items(),reverse=True))
        # portfolio =port
        gaps = models.Gap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        gap_df = ''
        if gaps:
            q = gaps.values('start_date', 'end_date')
            gap_df = pd.DataFrame.from_records(q)
            gap_df['start_date'] = pd.to_datetime(gap_df.start_date, format='%B, %Y')
            now = datetime.datetime.now()
            now_date = now.strftime('%B') + ', ' + now.strftime('%Y')
            gap_df['end_date'] = gap_df['end_date'].apply(lambda x: now_date if x == "present" else x)
            gap_df['start_date'] = pd.to_datetime(gap_df.start_date, format='%B, %Y')
            gap_df['type'] = 'gap'
            gap_df['end_date'] = pd.to_datetime(gap_df.end_date, format='%B, %Y')
            gap_df['s_year'] = pd.DatetimeIndex(gap_df['start_date']).year
            gap_df['e_year'] = pd.DatetimeIndex(gap_df['end_date']).year
            gap_df['s_month'] = pd.DatetimeIndex(gap_df['start_date']).month
            gap_df['e_month'] = pd.DatetimeIndex(gap_df['end_date']).month
            gap_df = gap_df.sort_values(by="start_date")
            gap_df = gap_df.rename(columns={'start_date': 'start', 'end_date': 'end'}, inplace=False)
            print("gaaaaaaaaaps ", gaps)
            for i in gaps:
                print("enterrred for loop for jgaps")
                if i.end_date:
                    if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
                        print("ifffffffffffffffffffffffffffffffffffffffffffffff")
                        year_title_pairs[int(i.end_date.split(',')[1])] = []
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
                    else:
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
        df = [exp_df, edu_df, gap_df]
        print(year_title_pairs)
        skills_show = models.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
    sorted_key_list = sorted(year_title_pairs)
    sorted_key_list.reverse()
    job_preference = models.CandidateJobPreference.objects.filter(candidate_id=user)
    skills_keywoard = models.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
    keywoard = []
    for i in skills_show:
        keywoard.append(i.skill.name)
    preferredcity = profile_show.preferred_cities.split(',')
    preferredcity = list(filter(None, preferredcity))
    # preferredcity=list(filter('0',preferredcity))
    # preferredcity=list(filter(0,preferredcity))
    for i in preferredcity:
        city = models.City.objects.get(id=int(i))
        keywoard.append(city.city_name)
    keywoard = ",".join(keywoard)
    share_url = ""
    if profile_show.url_name:
        share_url = profile_show.url_name
    about_me = ''
    if profile_show.about_me:
        about_me = profile_show.about_me
        clean = re.compile('<.*?>')
        about_me = re.sub(clean, '', about_me)

    return render(request, 'candidate/profile-third.html',
                  {'df': df, 'company_data_status': company_data_status,
                   'about_me': about_me, 'share_url': share_url, 'keywoard': keywoard, 'skills_show': skills_show,
                   'looking_job': looking_job, 'hire': hire, 'profile': profile_id_get, 'hidefield': hidefield,
                   'profile_show': profile_show, 'user': user, 'experiences': experiences, 'portfolios': portfolio,
                   'educations': educations, 'certificates': certificates, 'awards': awards,
                   'sorted_keys': sorted_key_list,
                   'year_title_pairs': year_title_pairs, 'start_years': start_years, 'end_years': end_years,
                   'skills': skill_names, 'year_salary_pair': json.dumps(year_salary_pair),
                   'company_names': company_names,
                   'job_preference': job_preference, 'exp_pie_chart_companies': json.dumps(exp_pie_chart_companies),
                   'exp_pie_chart_total_exp': json.dumps(exp_pie_chart_total_exp)})


def delete_exp_doc(request):
    # print(request.POST)
    record_id = request.POST.get('record_id')
    print(request.POST.get('record_id'))
    experience_id = request.POST.get('experience_id')
    print(request.POST.get('experience_id'))
    experience = models.CandidateExperience.objects.get(id=experience_id)
    print("========================>", experience)

    exp_document = models.CandidateExpDocuments.objects.get(candidate_exp_id=experience.id, record_id=record_id)
    exp_document.delete()
    return HttpResponse(True)


def candidate_resume_update(request):
    if request.method == 'POST':
        print('\n\n\n\n\n\n===============candidate_resume_update', request.FILES.get('resume-file'),
              request.session['active_profile_id'])
        user_id = models.User.objects.get(email=request.user.email)
        file = request.FILES.get('resume-file')
        profile = models.CandidateProfile.objects.get(candidate_id=user_id, profile_id=models.Profile.objects.get(
            id=request.session['active_profile_id']))
        profile.resume = file
        profile.save()
        return HttpResponse(True)


def referral_signup(request, referral):
    print('refer number====================', referral)
    print('referral_signup', User.objects.filter(referral_number=referral))
    if User.objects.filter(referral_number=referral).exists():
        alert = {}
        if not request.user.is_authenticated:
            if request.method == 'POST':
                fname = request.POST.get('fname')
                lname = request.POST.get('lname')
                email = request.POST.get('email')
                referred_by = request.POST.get('referral_code')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                checkbox = request.POST.get('checkbox')
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                device_type = ""
                if request.user_agent.is_mobile:
                    device_type = "Mobile"
                if request.user_agent.is_tablet:
                    device_type = "Tablet"
                if request.user_agent.is_pc:
                    device_type = "PC"
                browser_type = request.user_agent.browser.family
                browser_version = request.user_agent.browser.version_string
                os_type = request.user_agent.os.family
                os_version = request.user_agent.os.version_string
                context1 = {
                    "ip": ip,
                    "device_type": device_type,
                    "browser_type": browser_type,
                    "browser_version": browser_version,
                    "os_type": os_type,
                    "os_version": os_version
                }
                if User.objects.filter(email=request.POST['email']).exists():
                    alert['message'] = "email already exists"
                else:
                    usr = User.objects.create_candidate(email=email, first_name=fname, last_name=lname,
                                                        password=password, ip=ip, device_type=device_type,
                                                        browser_type=browser_type,
                                                        browser_version=browser_version, os_type=os_type,
                                                        os_version=os_version,
                                                        referral_number=generate_referral_code(),
                                                        referred_by=referred_by)
                    try:
                        mail_subject = 'Activate your account.'
                        current_site = get_current_site(request)
                        print('domain----===========', current_site.domain)
                        html_content = render_to_string('accounts/acc_active_email.html', {'user': usr,
                                                                                           'name': fname + ' ' + lname,
                                                                                           'email': email,
                                                                                           'domain': current_site.domain,
                                                                                           'uid': urlsafe_base64_encode(
                                                                                               force_bytes(usr.pk)),
                                                                                           'token': account_activation_token.make_token(
                                                                                               usr), })
                        to_email = usr.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        models.CandidateSEO.objects.create(candidate_id=User.objects.get(email__exact=email))
                        if models.User.objects.filter(referral_number=referred_by).exists():
                            referred_by_user = User.objects.get(referral_number=referred_by)
                            referred_to_user = User.objects.get(email__exact=email)
                            
                            models.ReferralDetails.objects.create(referred_by=referred_by_user,
                                                                  referred_to=referred_to_user)
                    except BadHeaderError:
                        new_registered_usr = User.objects.get(email__exact=email).delete()
                        models.ReferralDetails.objects.get(referred_to=new_registered_usr).delete()
                        alert['message'] = "email not send"
                    return activate_account_confirmation(request, fname + ' ' + lname, email)

        else:
            if request.user.is_authenticated:
                if request.user.is_candidate:
                    return redirect('candidate:home')
                if request.user.is_company:
                    profile = CompanyProfile.objects.filter(company_id=request.user.id)
                    if profile:
                        return redirect('company:company_profile')
                    else:
                        return redirect('company:add_edit_profile')
        return render(request, 'candidate/candidate_signup.html', {'referral_number': referral})
    else:
        return render(request, 'accounts/404.html')


import shutil
from django.conf import settings
from wsgiref.util import FileWrapper


def download_folder(request, candidate_id):
    path = settings.MEDIA_ROOT + str(candidate_id)
    path_to_zip = shutil.make_archive(path, "zip", path)
    name = User.objects.get(id=candidate_id)
    response = HttpResponse(FileWrapper(open(path_to_zip, 'rb')), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=' + name.first_name + ' ' + name.last_name + '.zip'
    # response['Content-Length'] = zip_io.tell()
    return response


def test_redirect(request):
    print('\n\n\n\ntest_redirect >>>>>>>>>>>>>>>>>>>')
    return redirect('candidate:home')


from django.utils.crypto import get_random_string


def job_view(request):
    context={}
    check_applied=None
    if 'job_type' in request.session:
        if request.session['job_type']=='company':
            context['company']=True
            job_obj = JobCreation.objects.get(id=request.session['view_job'])
            check_applied=AppliedCandidate.objects.filter(candidate=User.objects.get(id=request.user.id),job_id=JobCreation.objects.get(id=job_obj.id)).exists()
            context['job_obj']= job_obj
            context['appliedjob']= check_applied
            context['active_job_count'] = len(
                JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=False,
                                                        close_job_targetdate=False,
                                                        is_publish=True))
            context['close_job_count'] = len(
                JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=True))
            context['last_close_job'] = JobCreation.objects.filter(company_id=job_obj.company_id.id,
                                                                                close_job=True).order_by(
                '-close_job_at').first()
            context['latest_10_job'] = JobCreation.objects.filter(company_id=job_obj.company_id.id,
                                                                                close_job=False,
                                                                                close_job_targetdate=False,
                                                                                is_publish=True).order_by(
                '-publish_at')

            if JobWorkflow.objects.filter(job_id=job_obj).exists():
                job_workflow = JobWorkflow.objects.get(job_id=job_obj)
                if job_workflow.workflow_id:
                    main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
                    workflow_stages = WorkflowStages.objects.filter(workflow=main_workflow).order_by('sequence_number')
                    context['workflow_stages'] = workflow_stages
                    context['main_workflow'] = main_workflow

                    workflow_data = []
                    for stage in workflow_stages:
                        stage_dict = {'stage': stage, 'data': ''}
                        if stage.stage.name == 'MCQ Test':
                            mcq_template = ExamTemplate.objects.get(company_id=stage.company_id, template=stage.template,
                                                                        stage=stage.stage)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            if mcq_template.question_wise_time:
                                get_template_que = ExamQuestionUnit.objects.filter(template=mcq_template.template.id)

                                for time in get_template_que:
                                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                    "%M:%S")
                                stage_dict['mcq_time'] = total_time.time()
                            else:
                                stage_dict['mcq_time'] = datetime.datetime.strptime(mcq_template.duration, "%M:%S").time()
                            if mcq_template.marking_system == "question_wise":
                                get_template_que = ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
                                total_marks = 0
                                for mark in get_template_que:
                                    total_marks += int(mark.question_mark)
                                stage_dict['mcq_marks'] = total_marks
                            else:
                                stage_dict['mcq_marks'] = (int(mcq_template.basic_questions_count) * int(
                                    mcq_template.basic_question_marks)) + (int(mcq_template.intermediate_questions_count) * int(
                                    mcq_template.intermediate_question_marks)) + (
                                                                int(mcq_template.advanced_questions_count) * int(
                                                            mcq_template.advanced_question_marks))

                            stage_dict['data'] = mcq_template

                        if stage.stage.name == 'Descriptive Test':
                            descriptive_template = DescriptiveExamTemplate.objects.get(
                                company_id=stage.company_id,
                                stage=stage.stage,
                                template=stage.template)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')

                            get_template_que = DescriptiveExamQuestionUnit.objects.filter(
                                template=descriptive_template.template.id)

                            for time in get_template_que:
                                total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time, "%M:%S")
                            stage_dict['descriptive_time'] = total_time.time()

                            get_template_que = DescriptiveExamQuestionUnit.objects.filter(
                                template=descriptive_template.template.id)
                            total_marks = 0
                            for mark in get_template_que:
                                total_marks += int(mark.question_mark)
                            stage_dict['descriptive_marks'] = total_marks
                            stage_dict['data'] = descriptive_template

                        if stage.stage.name == 'Image Test':
                            image_template = ImageExamTemplate.objects.get(company_id=stage.company_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            if image_template.question_wise_time:
                                get_template_que = ImageExamQuestionUnit.objects.filter(
                                    template=image_template.template.id)

                                for time in get_template_que:
                                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                    "%M:%S")
                                stage_dict['image_time'] = total_time.time()
                            else:
                                stage_dict['image_time'] = datetime.datetime.strptime(image_template.duration, "%M:%S").time()
                            if image_template.marking_system == "question_wise":
                                get_template_que = ImageExamQuestionUnit.objects.filter(
                                    template=image_template.template.id)
                                total_marks = 0
                                for mark in get_template_que:
                                    total_marks += int(mark.question_mark)
                                stage_dict['image_marks'] = total_marks
                            else:
                                stage_dict['image_marks'] = (int(image_template.basic_questions_count) * int(
                                    image_template.basic_question_marks)) + (
                                                                    int(image_template.intermediate_questions_count) * int(
                                                                image_template.intermediate_question_marks)) + (
                                                                    int(image_template.advanced_questions_count) * int(
                                                                image_template.advanced_question_marks))

                            stage_dict['data'] = image_template

                        if stage.stage.name == 'Audio Test':

                            audio_template = AudioExamTemplate.objects.get(company_id=stage.company_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)

                            get_template_que = AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                            total_marks = 0
                            for mark in get_template_que:
                                total_marks += int(mark.question_mark)
                            stage_dict['audio_marks'] = total_marks
                            stage_dict['data'] = audio_template

                        if stage.stage.name == 'Coding Test':

                            coding_template = CodingExamConfiguration.objects.get(company_id=stage.company_id,
                                                                                        template_id=stage.template)
                            if coding_template.assignment_type == 'marks':
                                coding_que_marks = CodingExamQuestions.objects.filter(
                                    coding_exam_config_id=coding_template.id)
                                total_marks = 0
                                for i in coding_que_marks:
                                    total_marks += int(i.marks)
                                stage_dict['total_marks'] = total_marks
                            else:
                                coding_que_rating = CodingScoreCard.objects.filter(coding_exam_config_id=coding_template)
                                stage_dict['coding_que_rating'] = coding_que_rating
                            stage_dict['data'] = coding_template

                        workflow_data.append(stage_dict)

                    context['workflow_data'] = workflow_data
        if request.session['job_type']=='agency':
            context['agency']=True
            job_obj = AgencyModels.JobCreation.objects.get(id=request.session['view_job'])
            check_applied=AgencyModels.AppliedCandidate.objects.filter(candidate=User.objects.get(id=request.user.id),job_id=job_obj).exists()
            context['job_obj']= job_obj
            context['appliedjob']= check_applied
            context['active_job_count'] = len(
                AgencyModels.JobCreation.objects.filter(agency_id=job_obj.agency_id.id, close_job=False,
                                                        close_job_targetdate=False,
                                                        is_publish=True))
            context['close_job_count'] = len(
                AgencyModels.JobCreation.objects.filter(agency_id=job_obj.agency_id, close_job=True))
            context['last_close_job'] = AgencyModels.JobCreation.objects.filter(agency_id=job_obj.agency_id,
                                                                                close_job=True).order_by(
                '-close_job_at').first()
            context['latest_10_job'] = AgencyModels.JobCreation.objects.filter(agency_id=job_obj.agency_id,
                                                                                close_job=False,
                                                                                close_job_targetdate=False,
                                                                                is_publish=True).order_by(
                '-publish_at')

            if AgencyModels.JobWorkflow.objects.filter(job_id=job_obj).exists():
                job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
                if job_workflow.workflow_id:
                    main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
                    workflow_stages = AgencyModels.WorkflowStages.objects.filter(workflow=main_workflow).order_by('sequence_number')
                    context['workflow_stages'] = workflow_stages
                    context['main_workflow'] = main_workflow

                    workflow_data = []
                    for stage in workflow_stages:
                        stage_dict = {'stage': stage, 'data': ''}
                        if stage.stage.name == 'MCQ Test':
                            mcq_template = AgencyModels.ExamTemplate.objects.get(agency_id=stage.agency_id, template=stage.template,
                                                                        stage=stage.stage)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            if mcq_template.question_wise_time:
                                get_template_que = AgencyModels.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)

                                for time in get_template_que:
                                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                    "%M:%S")
                                stage_dict['mcq_time'] = total_time.time()
                            else:
                                stage_dict['mcq_time'] = datetime.datetime.strptime(mcq_template.duration, "%M:%S").time()
                            if mcq_template.marking_system == "question_wise":
                                get_template_que = AgencyModels.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
                                total_marks = 0
                                for mark in get_template_que:
                                    total_marks += int(mark.question_mark)
                                stage_dict['mcq_marks'] = total_marks
                            else:
                                stage_dict['mcq_marks'] = (int(mcq_template.basic_questions_count) * int(
                                    mcq_template.basic_question_marks)) + (int(mcq_template.intermediate_questions_count) * int(
                                    mcq_template.intermediate_question_marks)) + (
                                                                int(mcq_template.advanced_questions_count) * int(
                                                            mcq_template.advanced_question_marks))

                            stage_dict['data'] = mcq_template

                        if stage.stage.name == 'Descriptive Test':
                            descriptive_template = AgencyModels.DescriptiveExamTemplate.objects.get(
                                agency_id=stage.agency_id,
                                stage=stage.stage,
                                template=stage.template)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')

                            get_template_que = AgencyModels.DescriptiveExamQuestionUnit.objects.filter(
                                template=descriptive_template.template.id)

                            for time in get_template_que:
                                total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time, "%M:%S")
                            stage_dict['descriptive_time'] = total_time.time()

                            get_template_que = AgencyModels.DescriptiveExamQuestionUnit.objects.filter(
                                template=descriptive_template.template.id)
                            total_marks = 0
                            for mark in get_template_que:
                                total_marks += int(mark.question_mark)
                            stage_dict['descriptive_marks'] = total_marks
                            stage_dict['data'] = descriptive_template

                        if stage.stage.name == 'Image Test':
                            image_template = AgencyModels.ImageExamTemplate.objects.get(agency_id=stage.agency_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            if image_template.question_wise_time:
                                get_template_que = AgencyModels.ImageExamQuestionUnit.objects.filter(
                                    template=image_template.template.id)

                                for time in get_template_que:
                                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                    "%M:%S")
                                stage_dict['image_time'] = total_time.time()
                            else:
                                stage_dict['image_time'] = datetime.datetime.strptime(image_template.duration, "%M:%S").time()
                            if image_template.marking_system == "question_wise":
                                get_template_que = AgencyModels.ImageExamQuestionUnit.objects.filter(
                                    template=image_template.template.id)
                                total_marks = 0
                                for mark in get_template_que:
                                    total_marks += int(mark.question_mark)
                                stage_dict['image_marks'] = total_marks
                            else:
                                stage_dict['image_marks'] = (int(image_template.basic_questions_count) * int(
                                    image_template.basic_question_marks)) + (
                                                                    int(image_template.intermediate_questions_count) * int(
                                                                image_template.intermediate_question_marks)) + (
                                                                    int(image_template.advanced_questions_count) * int(
                                                                image_template.advanced_question_marks))

                            stage_dict['data'] = image_template

                        if stage.stage.name == 'Audio Test':

                            audio_template = AgencyModels.AudioExamTemplate.objects.get(agency_id=stage.agency_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)

                            get_template_que = AgencyModels.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                            total_marks = 0
                            for mark in get_template_que:
                                total_marks += int(mark.question_mark)
                            stage_dict['audio_marks'] = total_marks
                            stage_dict['data'] = audio_template

                        if stage.stage.name == 'Coding Test':

                            coding_template = AgencyModels.CodingExamConfiguration.objects.get(agency_id=stage.agency_id,
                                                                                        template_id=stage.template)
                            if coding_template.assignment_type == 'marks':
                                coding_que_marks = AgencyModels.CodingExamQuestions.objects.filter(
                                    coding_exam_config_id=coding_template.id)
                                total_marks = 0
                                for i in coding_que_marks:
                                    total_marks += int(i.marks)
                                stage_dict['total_marks'] = total_marks
                            else:
                                coding_que_rating = AgencyModels.CodingScoreCard.objects.filter(coding_exam_config_id=coding_template)
                                stage_dict['coding_que_rating'] = coding_que_rating
                            stage_dict['data'] = coding_template

                        workflow_data.append(stage_dict)

                    context['workflow_data'] = workflow_data

    if check_applied:
        del request.session['view_job']
        del request.session['job_type']
    return render(request, 'candidate/ATS/job_view.html', context)


def basic_detail(request,cand_detail_id=None):
    context={}
    context['source']=models.Source.objects.all()
    context['notice_period']= models.NoticePeriod.objects.all()
    context['countries']= models.Country.objects.all()
    if models.candidate_job_apply_detail.objects.filter(candidate_id=request.user).exists():
        edit_internal_candidate = models.candidate_job_apply_detail.objects.get(candidate_id=request.user)
        context['edit_internal_candidate'] = edit_internal_candidate
    if request.method == 'POST':
        fname = request.POST.get('f-name')
        lname = request.POST.get('l-name')
        user=User.objects.get(id=request.user.id)
        user.first_name=fname
        user.last_name=lname
        user.save()
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        resume = request.FILES.get('resume')
        if resume==None:
            resume=edit_internal_candidate.resume
        profile_pic = request.FILES.get('profile_pic')
        contact = request.POST.get('contact_num')
        designation = request.POST.get('designation-input')
        notice = models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
        current_city = models.City.objects.get(id=request.POST.get('candidate_current_city'))
        ctc = request.POST.get('ctc-input')
        expectedctc = request.POST.get('expected-ctc')
        total_exper = request.POST.get('professional-experience-year') +'.'+ request.POST.get(
            'professional-experience-month')
        models.candidate_job_apply_detail.objects.update_or_create(candidate_id=request.user,defaults={
            'gender' : gender,
            'resume' : resume,
            'contact' : contact,
            'designation': designation,
            'notice' : notice,
            'ctc' : ctc,
            'current_city':current_city,
            'expectedctc' : expectedctc,
            'total_exper' : total_exper,
            'profile_pic':profile_pic,
            'update_at':datetime.datetime.now()
        })
        add_skill=models.candidate_job_apply_detail.objects.get(candidate_id=request.user)
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                add_skill.skills.add(main_skill_obj)
            else:
                main_skill_obj=models.Skill.objects.create(name=i)
                add_skill.skills.add(main_skill_obj)
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                add_skill.prefered_city.add(main_city_obj)
        add_skill.save()
        company_internalcandidates=InternalCandidateBasicDetails.objects.filter(candidate_id=request.user)
        for company_internalcandidate in company_internalcandidates:
            company_internalcandidate.first_name = fname
            company_internalcandidate.last_name = lname
            company_internalcandidate.email = request.user.email
            company_internalcandidate.gender =  gender
            company_internalcandidate.resume = resume
            company_internalcandidate.contact = contact
            company_internalcandidate.designation = designation
            company_internalcandidate.current_city = current_city
            company_internalcandidate.notice =notice
            company_internalcandidate.ctc =ctc
            company_internalcandidate.expectedctc =expectedctc
            company_internalcandidate.total_exper = total_exper
            company_internalcandidate.profile_pic =profile_pic
            for i in request.POST.getlist('professional_skills'):
                if i.isnumeric():
                    main_skill_obj = models.Skill.objects.get(id=i)
                    company_internalcandidate.skills.add(main_skill_obj)
                else:
                    main_skill_obj=models.Skill.objects.get(name=i)
                    company_internalcandidate.skills.add(main_skill_obj)
            for i in request.POST.getlist('candidate_search_city'):
                if i.isnumeric():
                    main_city_obj = models.City.objects.get(id=i)
                    company_internalcandidate.prefered_city.add(main_city_obj)
            company_internalcandidate.save()
        
        agency_internalcandidates=AgencyModels.InternalCandidateBasicDetail.objects.filter(candidate_id=request.user)
        for agency_internalcandidate in agency_internalcandidates:
            agency_internalcandidate.first_name = request.user.first_name
            agency_internalcandidate.last_name = request.user.last_name
            agency_internalcandidate.email = request.user.email
            agency_internalcandidate.gender =  gender
            agency_internalcandidate.resume = resume
            agency_internalcandidate.contact = contact
            agency_internalcandidate.designation = designation
            agency_internalcandidate.current_city = current_city
            agency_internalcandidate.notice =notice
            agency_internalcandidate.ctc =ctc
            agency_internalcandidate.expectedctc =expectedctc
            agency_internalcandidate.total_exper = total_exper
            agency_internalcandidate.profile_pic =profile_pic
            for i in request.POST.getlist('professional_skills'):
                if i.isnumeric():
                    main_skill_obj = models.Skill.objects.get(id=i)
                    agency_internalcandidate.skills.add(main_skill_obj)
                else:
                    main_skill_obj=models.Skill.objects.get(name=i)
                    agency_internalcandidate.skills.add(main_skill_obj)
            for i in request.POST.getlist('candidate_search_city'):
                if i.isnumeric():
                    main_city_obj = models.City.objects.get(id=i)
                    agency_internalcandidate.prefered_city.add(main_city_obj)
            agency_internalcandidate.save()
        return redirect('candidate:home')
    return render(request,'candidate/ATS/basic_detail_form.html',context)

def applied_job(request,id):
    context = {'notice_period': models.NoticePeriod.objects.all()}
    job = JobCreation.objects.get(id=id)
    context['job_obj'] = job
    if request.user.is_candidate:
        if models.candidate_job_apply_detail.objects.filter(candidate_id=User.objects.get(id=request.user.id)).exists():
            context['candidate_apply_detail']=models.candidate_job_apply_detail.objects.get(candidate_id=User.objects.get(id=request.user.id))
    return render(request,'candidate/ATS/applied_job_detail.html',context)


def applyed_jod_afterlogin(request):
    alert={}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    if request.method == 'POST':
        print("==========================================================")
        fname = request.POST.get('f-name')
        lname = request.POST.get('l-name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        resume = request.FILES.get('resume')
        profile_pic = request.FILES.get('profile_pic')
        contact = request.POST.get('contact-num')
        designation = request.POST.get('designation-input')
        notice = models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period')),
        ctc = request.POST.get('ctc-input')
        expectedctc = request.POST.get('expected-ctc')
        total_exper = request.POST.get('professional-experience-year')+'.'+ request.POST.get(
            'professional-experience-month')
        mail_subject = 'Activate your account.'
        # print('domain----===========',current_site.domain)
        html_content = render_to_string('company/email/send_credentials.html', {'user': '',
                                                                            'name': fname + ' ' + lname,
                                                                            'email': email,
                                                                            'domain': current_site.domain,
                                                                            'password': '', 
                                                                            'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(request.user.id) })
        to_email = request.user.email
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        apply_data,created = models.candidate_job_apply_detail.objects.update_or_create(
                candidate_id=User.objects.get(id=request.user.id),defaults={
                    'gender':gender,
                    'contact':contact,
                    'designation':designation,
                    'notice':models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period')),
                    'ctc':ctc,
                    'current_city':models.City.objects.get(id=request.POST.get('candidate_current_city')),
                    'expectedctc':expectedctc,
                    'total_exper':total_exper})
        apply_data.skills.clear()
        if resume:
            apply_data.resume=resume
        if profile_pic:
            apply_data.profile_pic = profile_pic
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                apply_data.skills.add(main_skill_obj)
            else:
                tag_cre=models.Skill.objects.create(name=i)
                apply_data.skills.add(tag_cre)
        apply_data.prefered_city.clear()
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                apply_data.prefered_city.add(main_city_obj)
        apply_data.save()
        job_obj = JobCreation.objects.get(id=int(request.POST.get('job_id')))
        alert['job_obj']=job_obj
        DailySubmission.objects.update_or_create(email=email,company_job_id=job_obj,company_id = job_obj.company_id,defaults={
            'candidate_id':User.objects.get(email=email),
            'job_type':'company',
            'first_name' : fname,
            'last_name' : lname,
            'gender' : gender,
            'resume' : resume,
            'contact' : contact,
            'designation': designation,
            'notice' : models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period')),
            'ctc' : ctc,
            'verify':True,
            'current_city':models.City.objects.get(id=request.POST.get('candidate_current_city')),
            'expectedctc' : expectedctc,
            'total_exper' : total_exper,
            'update_at':datetime.datetime.now()
        })
        add_deatil=DailySubmission.objects.get(email=email,company_job_id=job_obj,company_id = job_obj.company_id)
        
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                add_deatil.skills.add(main_skill_obj)
            else:
                main_skill_obj=models.Skill.objects.create(name=i)
                add_deatil.skills.add(main_skill_obj)
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                add_deatil.prefered_city.add(main_city_obj)
        add_deatil.verified=True
        add_deatil.applied=True
        add_deatil.save()
        # fit_score(apply_data,job_obj)
        AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,dailysubmission=add_deatil,candidate=User.objects.get(email=email),
                                        job_id=job_obj,defaults={
                                    'submit_type':'Direct'
                                })
        notify.send(request.user, recipient=User.objects.get(email=email), verb="Application",
                            description="You have succesfully applied for the Job "+str(job_obj.job_title)+".",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        workflow = JobWorkflow.objects.get(job_id=job_obj)
        current_stage = None
        currentcompleted=False
        next_stage = None
        next_stage_sequance=0
        # onthego change
        if workflow.withworkflow:
            print("==========================withworkflow================================")
            workflow_stages = WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
            if workflow.is_application_review:
                print("==========================is_application_review================================")
                print('\n\n is_application_review')
                for stage in workflow_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        sequence_number = stage.sequence_number
                    elif stage.sequence_number == 2:
                        print("==========================Application Review================================")
                        status = 1
                        stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                        current_stage = stage_list_obj
                        next_stage_sequance=stage.sequence_number+1
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage_list_obj,
                                                                sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                        sequence_number = stage.sequence_number + 1
                        status = 0
                    else:
                        status = 0
                        sequence_number = stage.sequence_number + 1
                        next_stage = stage.stage
                    CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                            candidate_id=User.objects.get(email=email),
                                                            job_id=job_obj, stage=stage.stage,
                                                            template=stage.template,
                                                            sequence_number=sequence_number,status=status,custom_stage_name=stage.stage_name)
            else:
                for stage in workflow_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        current_stage = stage.stage
                    elif stage.sequence_number == 2:
                        status = 1
                        next_stage = stage.stage
                        notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                    else:
                        status = 0
                    CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                            candidate_id=User.objects.get(email=email),
                                                            job_id=job_obj, stage=stage.stage,
                                                            template=stage.template,
                                                            sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
        if workflow.onthego:
            print("==========================onthego================================")
            onthego_stages = OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

            if workflow.is_application_review:
                for stage in onthego_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        sequence_number = stage.sequence_number
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                        status = 1
                        sequence_number = stage.sequence_number + 1
                        stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                        current_stage = stage_list_obj
                        next_stage_sequance=stage.sequence_number+1
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage_list_obj,
                                                                sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                    else:
                        status = 0
                        sequence_number = stage.sequence_number + 1
                        current_stage = stage_list_obj
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)
            else:
                for stage in onthego_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        current_stage = stage.stage
                    elif stage.sequence_number == 2:
                        status = 1
                        next_stage = stage.stage
                        notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                    else:
                        status = 0
                    CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                            candidate_id=User.objects.get(id=request.user.id),
                                                            job_id=job_obj, stage=stage.stage,
                                                            template=stage.template,
                                                            sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
        action_required=''
        if next_stage_sequance!=0:
            if CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                            candidate_id=User.objects.get(id=request.user.id),
                                                            job_id=job_obj,
                                                            sequence_number=next_stage_sequance).exists():
                next_stage=CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
                                                            candidate_id=User.objects.get(id=request.user.id),
                                                            job_id=job_obj,
                                                            sequence_number=next_stage_sequance).stage
        if not current_stage==None:
            if current_stage.name == 'Interview' :
                action_required='By Company/Agency'
            elif current_stage.name == 'Application Review' :
                print('===========================onthe go action required')
                action_required='By Company'
            else:
                action_required='By Candidate'
        if current_stage!='':
            print("==========================Tracker================================")
            Tracker.objects.update_or_create(job_id=job_obj,candidate_id=User.objects.get(email=email),company_id=job_obj.company_id,defaults={
                                                    'current_stage':current_stage,'next_stage':next_stage,
                                                    'action_required':action_required,'update_at':datetime.datetime.now()})
        assign_job_internal = list(CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
                                                                          company_id=Company.objects.get(
                                                                              id=job_obj.company_id.id)).values_list(
            'recruiter_id', flat=True))
        assign_job_internal.append(job_obj.job_owner.id)
        assign_job_internal.append(job_obj.contact_name.id)
        assign_job_internal = list(set(assign_job_internal))
        title = job_obj.job_title
        chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=request.user.id, title=title,candidate_id=request.user)
        print(assign_job_internal)
        ChatModels.Member.objects.create(chat_id=chat.id, user_id=request.user.id)
        for i in assign_job_internal:
            ChatModels.Member.objects.create(chat_id=chat.id, user_id=i)
        ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
        candidate=User.objects.get(email=email)
        job_assign_recruiter = CompanyAssignJob.objects.filter(job_id=job_obj)
        description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
        to_email=[]
        to_email.append(job_obj.contact_name.email)
        to_email.append(job_obj.job_owner.email)
        if job_obj.contact_name.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission",
                                                                        description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                            job_obj.id))
        if job_obj.job_owner.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission",
                                                                        description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                            job_obj.id))
        all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        for i in all_assign_users:
            if i.recruiter_type_internal:
                to_email.append(i.recruiter_id.email)
                if i.recruiter_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
                                                                        description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                            job_obj.id))
        all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        stage_detail=''
        if not current_stage==None:
            if current_stage.name == 'Interview':
                stage_detail='Interview'
                description="You have one application to review for the job "+job_obj.job_title
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
                                                                                description=description,image="/static/notifications/icon/company/Application_Review.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
            elif current_stage.name=='Application Review':
                stage_detail='Application Review'
                description="You have one application to review for the job "+job_obj.job_title
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
                                                                                description=description,image="/static/notifications/icon/company/Application_Review.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
        to_email=list(set(to_email))
        mail_subject = "New Candidate submission"
        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"New candidate has been submitted by "+request.user.first_name+" "+request.user.last_name+" – <a href="+header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(job_obj.id)+" >Applicant profile link.</a> Please login to review"})
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
        msg.attach_alternative(html_content, "text/html")
        # try:
        msg.send()
        del request.session['view_job']
        return redirect('candidate:home')
    return render(request, 'candidate/ATS/applied_job_detail.html', alert)


def apply_job(request, id):
    context = {'notice_period': models.NoticePeriod.objects.all()}
    job = JobCreation.objects.get(id=id)
    context['job_obj'] = job
    return render(request, 'candidate/ATS/apply-jobs-form.html', context)

def job_apply(request, id):
    context = {'notice_period': models.NoticePeriod.objects.all()}
    job = AgencyModels.JobCreation.objects.get(id=id)
    context['job_obj_agency'] = job
    return render(request, 'candidate/ATS/apply-jobs-form.html', context)

def apply_candidate(request):
    alert = {}
    # get_random_string(length=32, allowed_chars='ACTG')
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if not request.user.is_authenticated:
        print('not is_authenticated')
        if request.method == 'POST':
            fname = request.POST.get('f-name')
            lname = request.POST.get('l-name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            resume = request.FILES['resume']
            contact = request.POST.get('contact-num')
            designation = request.POST.get('designation-input')
            notice = request.POST.get('professional-notice-period')
            ctc = request.POST.get('ctc-input')
            expectedctc = request.POST.get('expected-ctc')
            total_exper = request.POST.get('professional-experience-year')+'.'+ request.POST.get(
                'professional-experience-month')
            password = get_random_string(length=12)
            # checkbox = request.POST.get('checkbox')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            device_type = ""
            if request.user_agent.is_mobile:
                device_type = "Mobile"
            if request.user_agent.is_tablet:
                device_type = "Tablet"
            if request.user_agent.is_pc:
                device_type = "PC"
            browser_type = request.user_agent.browser.family
            browser_version = request.user_agent.browser.version_string
            os_type = request.user_agent.os.family
            os_version = request.user_agent.os.version_string
            context1 = {
                "ip": ip,
                "device_type": device_type,
                "browser_type": browser_type,
                "browser_version": browser_version,
                "os_type": os_type,
                "os_version": os_version
            }
            if not User.objects.filter(email=request.POST['email']).exists():
                print('created')
                usr = User.objects.apply_candidate(email=email, first_name=fname, last_name=lname,
                                                   password=password, ip=ip, device_type=device_type,
                                                   browser_type=browser_type,
                                                   browser_version=browser_version, os_type=os_type,
                                                   os_version=os_version,
                                                   referral_number=generate_referral_code())
                mail_subject = 'Activate your account.'
                current_site = get_current_site(request)
                # print('domain----===========',current_site.domain)
                html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                                                                                    'name': fname + ' ' + lname,
                                                                                    'email': email,
                                                                                    'domain': current_site.domain,
                                                                                    'password': password, })
                to_email = usr.email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                apply_data = models.candidate_job_apply_detail.objects.create(
                    candidate_id=User.objects.get(email=email), gender=gender, resume=resume, contact=contact,
                    designation=designation, notice=models.NoticePeriod.objects.get(id=int(notice)), ctc=ctc,
                    expectedctc=expectedctc, total_exper=total_exper, )
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = models.Skill.objects.get(id=i)
                        apply_data.skills.add(main_skill_obj)
                    else:
                        tag_cre=models.Skill.objects.create(name=i)
                        apply_data.skills.add(tag_cre)
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_tags_obj = models.Tags.objects.get(id=i)
                        apply_data.tags.add(main_tags_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i)
                        apply_data.tags.add(tag_cre)
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = models.City.objects.get(id=i)
                        apply_data.prefered_city.add(main_city_obj)
                apply_data.save()
            job_obj = AgencyModels.JobCreation.objects.get(id=int(request.POST.get('job_id')))
            alert['job_obj']=job_obj
            # fit_score(apply_data,job_obj)
            AgencyModels.AppliedCandidate.objects.update_or_create(agency_id=job_obj.agency_id,candidate=User.objects.get(email=email),
                                        job_id=job_obj,defaults={
                                    'submit_type':'Direct'
                                })
            
            # notify.send(job_obj.agency_id.agency_id, recipient=User.objects.get(email=email), verb="Application",
            #                 description="You have succesfully applied for the Job "+str(job_obj.job_title)+".",image="/static/notifications/icon/company/Job_Create.png",
            #                 target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
            #                     job_obj.id)+"/agency")
            workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
            currentcompleted=False
            next_stage = None
            next_stage_sequance=0
            # onthego change
            if workflow.withworkflow:
                print("==========================withworkflow================================")
                workflow_stages = AgencyModels.WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
                if workflow.is_application_review:
                    print("==========================is_application_review================================")
                    print('\n\n is_application_review')
                    for stage in workflow_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            sequence_number = stage.sequence_number
                        elif stage.sequence_number == 2:
                            print("==========================Application Review================================")
                            status = 1
                            stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                            current_stage = stage_list_obj
                            next_stage_sequance=stage.sequence_number+1
                            AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                    sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                            sequence_number = stage.sequence_number + 1
                            status = 0
                        else:
                            status = 0
                            sequence_number = stage.sequence_number + 1
                            next_stage = stage.stage
                        AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=sequence_number,status=status,custom_stage_name=stage.stage_name)
                else:
                    for stage in workflow_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            current_stage = stage.stage
                        elif stage.sequence_number == 2:
                            status = 1
                            next_stage = stage.stage
                            notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id))
                        else:
                            status = 0
                        AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
            if workflow.onthego:
                print("==========================onthego================================")
                onthego_stages = AgencyModels.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

                if workflow.is_application_review:
                    for stage in onthego_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            sequence_number = stage.sequence_number
                            AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                            status = 1
                            sequence_number = stage.sequence_number + 1
                            stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                            current_stage = stage_list_obj
                            next_stage_sequance=stage.sequence_number+1
                            AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                    sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                        else:
                            status = 0
                            sequence_number = stage.sequence_number + 1
                            current_stage = stage_list_obj
                            AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)
                else:
                    for stage in onthego_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            current_stage = stage.stage
                        elif stage.sequence_number == 2:
                            status = 1
                            next_stage = stage.stage
                            notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
                        else:
                            status = 0
                        AgencyModels.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
            action_required=''
            print("==========================next_stage_sequance================================",next_stage_sequance)
            if next_stage_sequance!=0:
                if AgencyModels.CandidateJobStagesStatus.objects.filter(agency_id=job_obj.agency_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj,
                                                                sequence_number=next_stage_sequance).exists():
                    next_stage=AgencyModels.CandidateJobStagesStatus.objects.get(agency_id=job_obj.agency_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj,
                                                                sequence_number=next_stage_sequance).stage
            if not current_stage==None:
                if current_stage.name=='Interview' :
                    action_required='By Agency'
                elif current_stage.name=='Application Review' :
                    print('===========================onthe go action required')
                    action_required='By Agency'
                else:
                    action_required='By Candidate'
            if current_stage!='':
                print("==========================Tracker================================")
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=User.objects.get(email=email),company_id=job_obj.company_id,defaults={
                #                                         'current_stage':current_stage,'next_stage':next_stage,
                #                                         'action_required':action_required,'update_at':datetime.datetime.now()})
            assign_job_internal = list(
                AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
                                                agency_id=job_obj.agency_id).values_list(
                    'recruiter_id', flat=True))
            assign_job_internal.append(job_obj.job_owner.id)
            assign_job_internal.append(job_obj.contact_name.id)
            assign_job_internal = list(set(assign_job_internal))
            title = job_obj.job_title
            # chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(email=email).id, title=title,candidate_id=User.objects.get(email=email))
            # print(assign_job_internal)
            # ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(email=email).id)
            # for i in assign_job_internal:
            #     ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
            # ChatModels.Message.objects.create(chat=chat,author=User.objects.get(email=email),text='Create Group')
            return redirect('accounts:signin')
    return render(request, 'candidate/ATS/apply-jobs-form.html', alert)


# def fit_score(candidate_data,job_object):
#     import pandas as pd
#     match_skill = []
#     unmatch_skill = []
#     candidate_skill=candidate_data.skills.all()
#     candidate_skill=[i.name for i in candidate_skill]
#     company_skill=job_object.required_skill.all()
#     company_skill=[i.name for i in company_skill]
#     for i in company_skill:Ffi
#         if i in candidate_skill :
#             match_skill.append(i)
#         else:
#             unmatch_skill.append(i)

#     if len(company_skill):
#         skill_per = 100
#     else:
#         skill_per = (100*len(candidate_skill))/len(company_skill)

#     candidate_skill_per = skill_per*25/100

#     # candidatecity=candidate_data.
#     company_city = job_object.city.city_name
#     company_city={company_city}
#     candidate_city=candidate_data.prefered_city.all()
#     candidate_city = {i.city_name for i in candidate_city}
#     print(candidate_city)
#     candidate_city_per = 0
#     if company_city.intersection(candidate_city):
#         candidate_city_per=10
#     else:
#         candidate_city_per=0
#     print(candidate_city_per)

#     candidate_notice_period = candidate_data.notice.notice_period
#     print(candidate_notice_period)
#     notice_period_per = 0
#     if candidate_notice_period.lower() == "immediate":
#         notice_period_per=15
#     elif candidate_notice_period.lower() == "30 days":
#         notice_period_per=14
#     elif candidate_notice_period.lower() == "45 days":
#         notice_period_per=12
#     elif candidate_notice_period.lower() == "60 days" :
#         notice_period_per=10
#     else:
#         notice_period_per=0

   
#     exp_per=0
#     candidate_experiance=candidate_data.total_exper
#     company_job_experiance=job_object.experience_year+'.'+job_object.experience_month
#     company_min_exp = (float(company_job_experiance)*50)/100
#     if float(company_job_experiance)<=float(candidate_experiance):
#         exp_per=100
#     elif company_min_exp<=float(candidate_experiance)<float(company_job_experiance):
#         exp_per=50
#     elif float(candidate_experiance)<=company_min_exp:
#         exp_per=0
#     else:
#         pass
#     candidate_exp_per = (exp_per*25)/100
   
#     ctc_per = 0
#     if float(job_object.max_salary)>= float(candidate_data.expectedctc):
#         ctc_per=25
#     elif float(job_object.max_salary) < float(candidate_data.expectedctc):
#         a = (float(job_object.max_salary)*10)/100
#         b = float(job_object.max_salary) + a
#         if b <= float(candidate_data.expectedctc):
#             c = (b*10)/100
#             d = b+c
#             if d <= float(candidate_data.expectedctc):
#                 e = (d*10)/100
#                 f = d+e
#                 if f <= float(candidate_data.expectedctc):
#                     g = (f*10)/100
#                     h = f+g
#                     if h <=float(candidate_data.expectedctc):
#                         pass
#                     else:
#                         ctc_per=0
#                 else:
#                     ctc_per=3
#             else:
#                 ctc_per=13
#         else:
#             ctc_per=23
#     else:
#         pass

#     models.FitScore.objects.create(candidate_id = User.objects.get(candidate_data.candidate_id),
#                                     job_id = JobCreation.objects.get(id=job_object.id),
#                                     match_skill=",".join(match_skill),
#                                     unmatch_skill=",".join(unmatch_skill),
#                                     fitscore=(candidate_skill_per+candidate_city_per + notice_period_per + candidate_exp_per + ctc_per))
#     return True
def add_apply_candidate(request):
    alert = {}
    # get_random_string(length=32, allowed_chars='ACTG')
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if not request.user.is_authenticated:
        print('not is_authenticated')
        if request.method == 'POST':
            fname = request.POST.get('f-name')
            lname = request.POST.get('l-name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            resume = request.FILES['resume']
            contact = request.POST.get('contact-num')
            designation = request.POST.get('designation-input')
            notice = models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
            ctc = request.POST.get('ctc-input')
            expectedctc = request.POST.get('expected-ctc')
            total_exper = request.POST.get('professional-experience-year')+'.'+ request.POST.get(
                'professional-experience-month')
            password = get_random_string(length=12)
            # checkbox = request.POST.get('checkbox')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            device_type = ""
            if request.user_agent.is_mobile:
                device_type = "Mobile"
            if request.user_agent.is_tablet:
                device_type = "Tablet"
            if request.user_agent.is_pc:
                device_type = "PC"
            browser_type = request.user_agent.browser.family
            browser_version = request.user_agent.browser.version_string
            os_type = request.user_agent.os.family
            os_version = request.user_agent.os.version_string
            context1 = {
                "ip": ip,
                "device_type": device_type,
                "browser_type": browser_type,
                "browser_version": browser_version,
                "os_type": os_type,
                "os_version": os_version
            }
            if not User.objects.filter(email=request.POST['email']).exists():
                print('created')
                usr = User.objects.apply_candidate(email=email, first_name=fname, last_name=lname,
                                                   password=password, ip=ip, device_type=device_type,
                                                   browser_type=browser_type,
                                                   browser_version=browser_version, os_type=os_type,
                                                   os_version=os_version,
                                                   referral_number=generate_referral_code())
                mail_subject = 'Activate your account.'
                current_site = get_current_site(request)
                # print('domain----===========',current_site.domain)
                html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                                                                                    'name': fname + ' ' + lname,
                                                                                    'email': email,
                                                                                    'domain': current_site.domain,
                                                                                    'password': password, })
                to_email = usr.email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                apply_data = models.candidate_job_apply_detail.objects.create(
                    candidate_id=User.objects.get(email=email), gender=gender, resume=resume, contact=contact,
                    designation=designation, notice=notice, ctc=ctc,
                    expectedctc=expectedctc, total_exper=total_exper,current_city=models.City.objects.get(id=request.POST.get('candidate_current_city')) )
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = models.Skill.objects.get(id=i)
                        apply_data.skills.add(main_skill_obj)
                    else:
                        tag_cre=models.Skill.objects.create(name=i)
                        apply_data.skills.add(tag_cre)
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_tags_obj = models.Tags.objects.get(id=i)
                        apply_data.tags.add(main_tags_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i)
                        apply_data.tags.add(tag_cre)
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = models.City.objects.get(id=i)
                        apply_data.prefered_city.add(main_city_obj)
                apply_data.save()
            job_obj = JobCreation.objects.get(id=int(request.POST.get('job_id')))
            alert['job_obj']=job_obj
            # fit_score(apply_data,job_obj)
            DailySubmission.objects.update_or_create(email=email,company_job_id=job_obj,company_id = job_obj.company_id,defaults={
                'candidate_id':User.objects.get(email=email),
                'job_type':'company',
                'first_name' : fname,
                'last_name' : lname,
                'gender' : gender,
                'resume' : resume,
                'contact' : contact,
                'designation': designation,
                'notice' : notice,
                'ctc' : ctc,
                'verify':True,
                'current_city':models.City.objects.get(id=request.POST.get('candidate_current_city')),
                'expectedctc' : expectedctc,
                'total_exper' : total_exper,
                'update_at':datetime.datetime.now()
            })
            add_deatil=DailySubmission.objects.get(email=email,company_job_id=job_obj,company_id = job_obj.company_id)
            
            for i in request.POST.getlist('professional_skills'):
                if i.isnumeric():
                    main_skill_obj = models.Skill.objects.get(id=i)
                    add_deatil.skills.add(main_skill_obj)
                else:
                    main_skill_obj=models.Skill.objects.create(name=i)
                    add_deatil.skills.add(main_skill_obj)
            for i in request.POST.getlist('candidate_search_city'):
                if i.isnumeric():
                    main_city_obj = models.City.objects.get(id=i)
                    add_deatil.prefered_city.add(main_city_obj)
            add_deatil.verified=True
            add_deatil.applied=True
            add_deatil.save()
            AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,dailysubmission=add_deatil,candidate=User.objects.get(email=email),
                                        job_id=job_obj,defaults={
                                    'submit_type':'Direct'
                                })
            
            # notify.send(request.user, recipient=User.objects.get(email=email), verb="Application",
            #                 description="You have succesfully applied for the Job "+str(job_obj.job_title)+".",image="/static/notifications/icon/company/Job_Create.png",
            #                 target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
            #                     job_obj.id)+"/company")
            workflow = JobWorkflow.objects.get(job_id=job_obj)
            currentcompleted=False
            next_stage = None
            next_stage_sequance=0
            # onthego change
            if workflow.withworkflow:
                print("==========================withworkflow================================")
                workflow_stages = WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
                if workflow.is_application_review:
                    print("==========================is_application_review================================")
                    print('\n\n is_application_review')
                    for stage in workflow_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            sequence_number = stage.sequence_number
                        elif stage.sequence_number == 2:
                            print("==========================Application Review================================")
                            status = 1
                            stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                            current_stage = stage_list_obj
                            next_stage_sequance=stage.sequence_number+1
                            CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                    sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                            sequence_number = stage.sequence_number + 1
                            status = 0
                        else:
                            status = 0
                            sequence_number = stage.sequence_number + 1
                            next_stage = stage.stage
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=sequence_number,status=status,custom_stage_name=stage.stage_name)
                else:
                    for stage in workflow_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            current_stage = stage.stage
                        elif stage.sequence_number == 2:
                            status = 1
                            next_stage = stage.stage
                            notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                        else:
                            status = 0
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
            if workflow.onthego:
                print("==========================onthego================================")
                onthego_stages = OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

                if workflow.is_application_review:
                    for stage in onthego_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            sequence_number = stage.sequence_number
                            CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                            status = 1
                            sequence_number = stage.sequence_number + 1
                            stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                            current_stage = stage_list_obj
                            next_stage_sequance=stage.sequence_number+1
                            CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                    sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                        else:
                            status = 0
                            sequence_number = stage.sequence_number + 1
                            current_stage = stage_list_obj
                            CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=User.objects.get(email=email),
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)
                else:
                    for stage in onthego_stages:
                        if stage.sequence_number == 1:
                            status = 2
                            current_stage = stage.stage
                        elif stage.sequence_number == 2:
                            status = 1
                            next_stage = stage.stage
                            notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                        else:
                            status = 0
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
            action_required=''
            print("==========================next_stage_sequance================================",next_stage_sequance)
            if next_stage_sequance!=0:
                if CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj,
                                                                sequence_number=next_stage_sequance).exists():
                    next_stage=CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
                                                                candidate_id=User.objects.get(email=email),
                                                                job_id=job_obj,
                                                                sequence_number=next_stage_sequance).stage
            if not current_stage==None:
                if current_stage.name=='Interview' :
                    action_required='By Company/Agency'
                elif current_stage.name=='Application Review' :
                    print('===========================onthe go action required')
                    action_required='By Company'
                else:
                    action_required='By Candidate'
            if current_stage!='':
                print("==========================Tracker================================")
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=User.objects.get(email=email),company_id=job_obj.company_id,defaults={
                                                        'current_stage':current_stage,'next_stage':next_stage,
                                                        'action_required':action_required,'update_at':datetime.datetime.now()})
            assign_job_internal = list(
                CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
                                                company_id=Company.objects.get(
                                                    id=job_obj.company_id.id)).values_list(
                    'recruiter_id', flat=True))
            assign_job_internal.append(job_obj.job_owner.id)
            assign_job_internal.append(job_obj.contact_name.id)
            assign_job_internal = list(set(assign_job_internal))
            title = job_obj.job_title
            chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(email=email).id, title=title,candidate_id=User.objects.get(email=email))
            print(assign_job_internal)
            ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(email=email).id)
            for i in assign_job_internal:
                ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
            ChatModels.Message.objects.create(chat=chat,author=User.objects.get(email=email),text='Create Group')
            return redirect('accounts:signin')
    return render(request, 'candidate/ATS/apply-jobs-form.html', alert)


def candidate_jcr(request, id, job_id):
    context = {}
    user_obj = User.objects.get(id=request.user.id)
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=id)
    context['job_obj'] = job_obj
    jcr_obj_temp = JCR.objects.filter(template=template_obj).order_by('id')
    jcr_categories = jcr_obj_temp.filter(pid=None).order_by('id')

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj, job_id=job_obj)

    if stage_status.status == 1:
        context['getStoreData'] = []
        for category in jcr_categories:
            add_details_item = []
            sub_categories = jcr_obj_temp.filter(pid=category)
            for sub_category in sub_categories:
                sub_type = []
                leaf_nodes = jcr_obj_temp.filter(pid=sub_category)
                for node in leaf_nodes:
                    detail = []
                    det_data = jcr_obj_temp.filter(pid=node.id)
                    for detail_data in det_data:
                        detail.append({
                            'id': detail_data.id,
                            'title': detail_data.name,
                            'percent': detail_data.ratio
                        })
                    sub_type.append({'question': node.name,
                                     'id': node.id,
                                     'q_percent': node.ratio,
                                     'matching': node.flag,
                                     'details': detail
                                     })
                add_details_item.append({'cat_type': sub_category.name,
                                         'id': sub_category.id,
                                         'cate_percent': sub_category.ratio,
                                         'cat_subtype': sub_type})
            context['getStoreData'].append({'cat_name': category.name, 'cat_value': category.ratio, 'id': category.id,
                                            'addDetailsItem': add_details_item})
        if len(context['getStoreData']) == 0:
            context['getStoreData'] = None
        if request.method == 'POST':
            final = []
            main_cat = []
            jcr = []
            for i in context['getStoreData']:
                cat_per = 0
                cat_type = []
                for j in i['addDetailsItem']:
                    qui = 0
                    question = []
                    for k in j['cat_subtype']:
                        option = []
                        if k['matching'] == 'multi':
                            detail = 0
                            for l in k['details']:
                                if l['title'] in request.POST.getlist(str(k['id'])):
                                    models.JcrFill.objects.update_or_create(
                                        candidate_id=user_obj,
                                        job_id=JobCreation.objects.get(id=job_id),
                                        template=template_obj,
                                        company_id=Company.objects.get(id=int(job_obj.company_id.id)),
                                        defaults={
                                            'jcr_id': JCR.objects.get(id=int(l['id'])),
                                        })
                                    option.append({'detail': l['title'], 'detail_per': l['percent']})
                                    detail += int(l['percent'])

                        if k['matching'] == 'single':
                            detail = 0

                            for l in k['details']:
                                if l['title'] == request.POST.get(str(k['id'])):
                                    models.JcrFill.objects.update_or_create(
                                        candidate_id=user_obj,
                                        job_id=JobCreation.objects.get(id=job_id),
                                        template=template_obj,
                                        company_id=Company.objects.get(id=job_obj.company_id.id),
                                        defaults={
                                            'jcr_id': JCR.objects.get(id=int(l['id'])),
                                        })
                                    option.append({'detail': l['title'], 'detail_per': l['percent']})
                                    detail += int(l['percent'])

                        question.append({'question': k['question'], 'q_per': k['q_percent'],
                                         'obt_per': detail * int(k['q_percent']) / 100, 'option': option})
                        qui += detail * int(k['q_percent']) / 100
                    cat_type.append({'catagory': j['cat_type'], 'cat_per': j['cate_percent'],
                                     'obt_cat': qui * int(j['cate_percent']) / 100, 'question': question})
                    cat_per += qui * int(j['cate_percent']) / 100
                final.append({i['cat_name']: cat_per * int(i['cat_value']) / 100})
                main_cat.append(
                    {'main_cat': i['cat_name'], 'main_per': i['cat_value'], 'main_obt': cat_per * int(i['cat_value']) / 100,
                     'category_detail': cat_type})
            models.JcrRatio.objects.update_or_create(candidate_id=user_obj,
                                                     job_id=JobCreation.objects.get(id=job_id),
                                                     template=template_obj,
                                                     company_id=Company.objects.get(id=job_obj.company_id.id), defaults={
                    'Primary': final[0]['primary-list'],
                    'Secondary': final[1]['secondary-list'],
                    'Objective': final[2]['objective-list'],
                    'Total': final[0]['primary-list'] + final[1]['secondary-list'] + final[2]['objective-list']
                })
            # print(main_cat)
            a = """<div style="background: #fff;">
                <div style="width: 100%;display: inline-block;padding: 8px 15px;border-bottom: 2px solid #eef4fa;">
                    <div style="float: left;width: 50%;font-size: 16px;font-weight: 700;color: #031b4e;">Skill Compatibility</div>
                    <div style="float: left;width: 50%;text-align: right;font-size: 14px;font-weight: 500;color: #51bc25;line-height: 24px;">Obtained : """ + str(
                final[0]['primary-list'] + final[1]['secondary-list'] + final[2]['objective-list']) + """%</div>
                </div>
                <div style="margin: 15px;border: 2px solid #eef4fa;">
                    <div style="font-size: 16px;font-weight: bold; text-transform: uppercase;color: #031b4e;border-bottom: 2px solid #eef4fa;padding: 6px 13px;">JCR -  <span style="color: #51bc25;">""" + str(
                final[0]['primary-list'] + final[1]['secondary-list'] + final[2][
                    'objective-list']) + """%</span> / 100%</div>"""
            for i in main_cat:
                a += """<div style="width: 100%;display: inline-block;color: #031b4e;">
                            <div style="width: 12%;float: left;font-size: 14px;color: #031b4e;padding: 10px 13px;">
                               <div>""" + str(i['main_cat']) + """ :-</div>
                               <div>(""" + str(i['main_obt']) + """% / """ + str(i['main_per']) + """%)</div>
                           </div>
                           <div style="width: 85%;float: left;border-left: 2px solid #eef4fa;">"""
                for j in i['category_detail']:
                    a += """<div style="display: inline-block;width: 100%;border-bottom: 2px solid #eef4fa;">
                                       <div style="width: 100%;">
                                           <div style="width: 17%;float: left;padding: 10px 13px;">
                                               <div>""" + str(j['catagory']) + """ :-</div>
                                               <div>(""" + str(j['obt_cat']) + """% / """ + str(j['cat_per']) + """%)</div>
                                           </div>
                                           <div style="float: left;width: 75%;border-left: 2px solid #eef4fa;">"""
                    for k in j['question']:
                        a += """              <div style="padding: 10px 13px;border-bottom: 2px solid #eef4fa;">
                                                       <div>""" + str(k['question']) + """.</div>
                                                       <div>(""" + str(k['obt_per']) + """% / """ + str(
                            k['q_per']) + """%)</div>"""
                        for l in k['option']:
                            a += """<div style="padding-top: 5px;"><svg id="SvgjsSvg1006" width="16" height="16" 
                            xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" 
                            xmlns:svgjs="http://svgjs.com/svgjs"><defs id="SvgjsDefs1007"></defs><g id="SvgjsG1008" 
                            transform="matrix(1,0,0,1,0,0)"><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" 
                            class="svg-inline--fa fa-dot-circle fa-w-16" data-icon="dot-circle" data-prefix="fas" 
                            viewBox="0 0 512 512" width="16" height="16"><path fill="#0068ff" d="M256 8C119.033 8 8 
                            119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm80 248c0 44.112-35.888 
                            80-80 80s-80-35.888-80-80 35.888-80 80-80 80 35.888 80 80z" class="colorcurrentColor 
                            svgShape"></path></svg></g></svg> <span style="padding-left: 3px;">""" + str(
                                l['detail']) + """ (""" + str(l['detail_per']) + """%)</span></div>"""
                        a += """               </div>"""
                    a += """               </div>
                                       </div>
                                   </div>"""
                a += """</div>
    
                        </div>"""
            a += """    </div>
            </div>"""
            path = settings.MEDIA_ROOT + "{}/{}/Stages/JCR/".format(request.user.id, job_obj.id)
            # pdfkit.from_string(a, output_path=path + "JCR.pdf")
            jcr_file = models.JcrRatio.objects.get(candidate_id=user_obj,
                                                   job_id=JobCreation.objects.get(id=job_id),
                                                   template=template_obj,
                                                   company_id=Company.objects.get(id=job_obj.company_id.id))
            jcr_file.jcr_pdf = path + 'JCR.pdf'
            jcr_file.save()
            
            stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                                job_id=job_obj)
            stage_status.status = 2
            stage_status.save()

            new_sequence_no = stage_status.sequence_number + 1
            if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                       sequence_number=new_sequence_no).exists():
                new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                        sequence_number=new_sequence_no)
                new_stage_status.status = 1
                new_stage_status.save()

            return redirect('candidate:applied_job_detail',job_obj.id)
        return render(request, 'candidate/ATS/jcr_candidate.html', context)
    else:
        return HttpResponse(False)


def applied_job_list(request):
    if models.candidate_job_apply_detail.objects.filter(candidate_id=request.user).exists():
        if request.user.is_candidate:
            print(request.user.id)
            applied_job = AppliedCandidate.objects.filter(candidate=User.objects.get(id=request.user.id))
            # applied_agency_job = AssociateCandidateAgency.objects.filter(candidate_id=User.objects.get(id=request.user.id))
            applied_agency_job = AgencyModels.AppliedCandidate.objects.filter(candidate_id=User.objects.get(id=request.user.id))
            return render(request, 'candidate/ATS/candidate_applied_job_list.html', {'applied_job': applied_job,'applied_agency_job':applied_agency_job})
        else:
            return HttpResponse(False)
    else:
            return redirect('candidate:basic_detail')

def prequisites_view(request, id, job_id):
    context = {}
    user_obj = User.objects.get(id=request.user.id)
    template_obj = Template_creation.objects.get(id=id)
    pre_requisite = PreRequisites.objects.get(template=template_obj)
    job_obj = JobCreation.objects.get(id=job_id)

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj, job_id=job_obj)

    if stage_status.status == 1:
        context['pre_requisite'] = {"template-data": eval(pre_requisite.data)}
        context['pre_requisite'] = json.dumps(context['pre_requisite'])
        context["html_data"] = pre_requisite.html_data
        context['job_obj'] = job_obj
        context['template_obj'] = id
        context['stage_id'] = stage_status.id

        if request.method == 'POST':
            response = ''
            pre_data = json.loads(request.body.decode('UTF-8'))
            pdf_create = """<div style="background: #fff;">
                                        <div style="width: 100%;display: inline-block;padding: 10px 15px;border-bottom: 2px solid #EEF4FA;">
                                            <div style="font-size: 16px;font-weight: 700;color: #031B4E;">02 Eligibility criteria</div>
                                        </div>
                                        <div style="margin: 15px;">
                                            <ul style="width: 100%;list-style: none;display: inline-block;padding: 0;">"""
            for i in pre_data['data']:
                if i['result'] == 'pass':
                    pdf_create += """<li style="margin-bottom:10px;border: 2px solid #E2E8F5;border-radius: 10px;padding: 16px 14px;font-size: 14px;color: #031B4E;line-height: normal;background-color: #F9FAFC;">
                                                    <div style="display: flex;"><span style="padding-right: 5px;">Question. </span> """ + \
                                  i['question'] + """</div>
                                                    <div style="margin-top: 10px;"><svg id="SvgjsSvg1006" width="16" height="16" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.com/svgjs"><defs id="SvgjsDefs1007"></defs><g id="SvgjsG1008" transform="matrix(1,0,0,1,0,0)"><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="svg-inline--fa fa-dot-circle fa-w-16" data-icon="dot-circle" data-prefix="fas" viewBox="0 0 512 512" width="16" height="16"><path fill="#51BB25" d="M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm80 248c0 44.112-35.888 80-80 80s-80-35.888-80-80 35.888-80 80-80 80 35.888 80 80z" class="colorcurrentColor svgShape"></path></svg></g></svg> <span style="font-weight: 500;color:#51bb25;padding-left: 3px;">""" + \
                                  i['ans'] + """</span></div>
                                                </li>"""
                    response = True
                    result = True
                else:
                    pdf_create += """<li style="margin-bottom:10px;border: 2px solid #E2E8F5;border-radius: 10px;padding: 16px 14px;font-size: 14px;color: #031B4E;line-height: normal;background-color: #F9FAFC;">
                                                    <div style="display: flex;"><span style="padding-right: 5px;">Question. </span> """ + \
                                  i['question'] + """ <span style="height: 24px;background-color: #FF5353;color: #fff;border-radius: 10px;font-size: 13px;padding: 4px 13px;margin-left: 10px;">Rejected</span></div>
                                                    <div style="margin-top: 10px;"><svg id="SvgjsSvg1006" width="16" height="16" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.com/svgjs"><defs id="SvgjsDefs1007"></defs><g id="SvgjsG1008" transform="matrix(1,0,0,1,0,0)"><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="svg-inline--fa fa-dot-circle fa-w-16" data-icon="dot-circle" data-prefix="fas" viewBox="0 0 512 512" width="16" height="16"><path fill="#FF5353" d="M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm80 248c0 44.112-35.888 80-80 80s-80-35.888-80-80 35.888-80 80-80 80 35.888 80 80z" class="colorcurrentColor svgShape"></path></svg></g></svg> <span style="font-weight: 500;color:#ff5353;padding-left: 3px;">""" + \
                                  i['ans'] + """</span></div>
                                                </li>"""
                    response = False
                    result = False
            pdf_create += """    </ul>
                                        </div>
                                    </div>"""
            path = settings.MEDIA_ROOT + "{}/{}/Stages/PreRequisites/".format(request.user.id, job_obj.id)

            file_name=path+request.user.first_name+"PreRequisites.pdf"
           
            models.PreRequisitesFill.objects.update_or_create(candidate_id=User.objects.get(id=request.user.id),
                                                          job_id=JobCreation.objects.get(id=job_id),
                                                          template=Template_creation.objects.get(id=id),
                                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                                          defaults={
                                                              'result':result,
                                                              'prerequisites_pdf': file_name,
                                                              'prerequisites_data': pre_data['data']
                                                          })

            stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                                job_id=job_obj)
            current_stage = ''
            currentcompleted=False
            next_stage = None
            action_required=''
            reject=False
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"  
            if result:
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=stage_status.stage
                currentcompleted=True
                stage_status.save()
                # notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                #             description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                #             target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                #                 job_id.id)+"/company")

                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj,candidate_id=user_obj,sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    next_stage=new_stage_status.stage
                    new_stage_status.action_performed = False
                    new_stage_status.assessment_done = False
                    new_stage_status.save()
            else:
                stage_status.status = -1
                current_stage=stage_status.stage
                stage_status.action_performed = True
                stage_status.assessment_done = True
                stage_status.save()
                reject=True
                # notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                #             description="Sorry! Your profile has been rejected for the Job "+str(job_id.job_title),image="/static/notifications/icon/company/Job_Create.png",
                #             target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                #                 job_id.id)+"/company")
            if not next_stage==None:
                if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                else:
                    action_required='Candidate'
            Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
                                                                'action_required':action_required,'update_at':datetime.datetime.now()})
            pdfkit.from_string(pdf_create, output_path=path+request.user.first_name+"PreRequisites.pdf")
            return HttpResponse(response)
        return render(request, 'candidate/ATS/prequisites_view.html', context)
    else:
        return HttpResponse(False)



def agency_prequisites_view(request, id, job_id):
    context = {}
    user_obj = User.objects.get(id=request.user.id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    pre_requisite = AgencyModels.PreRequisites.objects.get(template=template_obj)
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj, job_id=job_obj)

    if stage_status.status == 1:
        context['pre_requisite'] = {"template-data": eval(pre_requisite.data)}
        context['pre_requisite'] = json.dumps(context['pre_requisite'])
        context["html_data"] = pre_requisite.html_data
        context['job_obj'] = job_obj
        context['template_obj'] = id
        context['stage_id'] = stage_status.id

        if request.method == 'POST':
            response = ''
            pre_data = json.loads(request.body.decode('UTF-8'))
            pdf_create = """<div style="background: #fff;">
                                        <div style="width: 100%;display: inline-block;padding: 10px 15px;border-bottom: 2px solid #EEF4FA;">
                                            <div style="font-size: 16px;font-weight: 700;color: #031B4E;">02 Eligibility criteria</div>
                                        </div>
                                        <div style="margin: 15px;">
                                            <ul style="width: 100%;list-style: none;display: inline-block;padding: 0;">"""
            for i in pre_data['data']:
                if i['result'] == 'pass':
                    pdf_create += """<li style="margin-bottom:10px;border: 2px solid #E2E8F5;border-radius: 10px;padding: 16px 14px;font-size: 14px;color: #031B4E;line-height: normal;background-color: #F9FAFC;">
                                                    <div style="display: flex;"><span style="padding-right: 5px;">Question. </span> """ + \
                                  i['question'] + """</div>
                                                    <div style="margin-top: 10px;"><svg id="SvgjsSvg1006" width="16" height="16" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.com/svgjs"><defs id="SvgjsDefs1007"></defs><g id="SvgjsG1008" transform="matrix(1,0,0,1,0,0)"><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="svg-inline--fa fa-dot-circle fa-w-16" data-icon="dot-circle" data-prefix="fas" viewBox="0 0 512 512" width="16" height="16"><path fill="#51BB25" d="M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm80 248c0 44.112-35.888 80-80 80s-80-35.888-80-80 35.888-80 80-80 80 35.888 80 80z" class="colorcurrentColor svgShape"></path></svg></g></svg> <span style="font-weight: 500;color:#51bb25;padding-left: 3px;">""" + \
                                  i['ans'] + """</span></div>
                                                </li>"""
                    response = True
                    result = True
                else:
                    pdf_create += """<li style="margin-bottom:10px;border: 2px solid #E2E8F5;border-radius: 10px;padding: 16px 14px;font-size: 14px;color: #031B4E;line-height: normal;background-color: #F9FAFC;">
                                                    <div style="display: flex;"><span style="padding-right: 5px;">Question. </span> """ + \
                                  i['question'] + """ <span style="height: 24px;background-color: #FF5353;color: #fff;border-radius: 10px;font-size: 13px;padding: 4px 13px;margin-left: 10px;">Rejected</span></div>
                                                    <div style="margin-top: 10px;"><svg id="SvgjsSvg1006" width="16" height="16" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.com/svgjs"><defs id="SvgjsDefs1007"></defs><g id="SvgjsG1008" transform="matrix(1,0,0,1,0,0)"><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="svg-inline--fa fa-dot-circle fa-w-16" data-icon="dot-circle" data-prefix="fas" viewBox="0 0 512 512" width="16" height="16"><path fill="#FF5353" d="M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248S392.967 8 256 8zm80 248c0 44.112-35.888 80-80 80s-80-35.888-80-80 35.888-80 80-80 80 35.888 80 80z" class="colorcurrentColor svgShape"></path></svg></g></svg> <span style="font-weight: 500;color:#ff5353;padding-left: 3px;">""" + \
                                  i['ans'] + """</span></div>
                                                </li>"""
                    response = False
                    result = False
            pdf_create += """    </ul>
                                        </div>
                                    </div>"""
            path = settings.MEDIA_ROOT + "{}/{}/Stages/PreRequisites/".format(request.user.id, job_obj.id)

            file_name=path+request.user.first_name+"PreRequisites.pdf"
           
            models.Agency_PreRequisitesFill.objects.update_or_create(candidate_id=User.objects.get(id=request.user.id),
                                                          job_id=AgencyModels.JobCreation.objects.get(id=job_id),
                                                          template=AgencyModels.Template_creation.objects.get(id=id),
                                                          agency_id=job_obj.agency_id,
                                                          defaults={
                                                              'result':result,
                                                              'prerequisites_pdf': file_name,
                                                              'prerequisites_data': pre_data['data']
                                                          })

            stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                                job_id=job_obj)
            current_stage = ''
            currentcompleted=False
            next_stage = None
            action_required=''
            reject=False
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"  
            if result:
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=stage_status.stage
                currentcompleted=True
                stage_status.save()
                # notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                #             description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                #             target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                #                 job_id.id)+"/agency")

                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj,candidate_id=user_obj,sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    next_stage=new_stage_status.stage
                    new_stage_status.action_performed = False
                    new_stage_status.assessment_done = False
                    new_stage_status.save()
            else:
                stage_status.status = -1
                current_stage=stage_status.stage
                stage_status.action_performed = True
                stage_status.assessment_done = True
                stage_status.save()
                reject=True
                # notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                #             description="Sorry! Your profile has been rejected for the Job "+str(job_id.job_title),image="/static/notifications/icon/company/Job_Create.png",
                #             target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                #                 job_id.id)+"/agency")
            if not next_stage==None:
                if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                else:
                    action_required='Candidate'
            # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
            #                                                     'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
            #                                                     'action_required':action_required,'update_at':datetime.datetime.now()})
            pdfkit.from_string(pdf_create, output_path=path+request.user.first_name+"PreRequisites.pdf")
            return HttpResponse(response)
        return render(request, 'candidate/ATS/agency/prequisites_view.html', context)
    else:
        return HttpResponse(False)

def mcq_exam(request, id, job_id):
    # 1=right
    # -1=Wrong
    # 0=skip
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
         
    if stage_status.status == 1:
        job_obj = JobCreation.objects.get(id=job_id)
        mcqtem = ExamTemplate.objects.get(template=Template_creation.objects.get(id=id))


        if not mcqtem.exam_type == 'custom':
            questions = mcq_Question.objects.filter(company_id=Company.objects.get(id=mcqtem.company_id.id),mcq_subject=mcqtem.subject.id)
            basic_questions = list(questions.filter(question_level__level_name='basic'))
            intermediate_questions =list( questions.filter(question_level__level_name='intermediate'))
            advanced_questions =list( questions.filter(question_level__level_name='advance'))
            random.shuffle(basic_questions)
            random.shuffle(intermediate_questions)
            random.shuffle(advanced_questions)
            basic_questions = random.sample(basic_questions,int(mcqtem.basic_questions_count))
            intermediate_questions = random.sample(intermediate_questions,int( mcqtem.intermediate_questions_count))
            advanced_questions = random.sample(advanced_questions,int(mcqtem.advanced_questions_count))
            if models.RandomMCQExam.objects.filter(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id)).exists():
                delete_question=models.RandomMCQExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                delete_question.question.clear()
                for i in basic_questions:
                    delete_question.question.add(i)
                for i in intermediate_questions:
                    delete_question.question.add(i)
                for i in advanced_questions:
                    delete_question.question.add(i)
            else:
                add_random=models.RandomMCQExam.objects.create(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                for i in basic_questions:
                    add_random.question.add(i)
                for i in intermediate_questions:
                    add_random.question.add(i)
                for i in advanced_questions:
                    add_random.question.add(i)
        # mcqpaper = QuestionPaper.objects.get(exam_template=ExamTemplate.objects.get(template=Template_creation.objects.get(id=id)))
        que = []
        count = 0
        if not mcqtem.question_wise_time:
            time=mcqtem.duration.split(':')
            timer_obj = models.ExamTimeStatus.objects.filter(candidate_id=request.user, template=mcqtem.template,
                                                             job_id=job_obj)
            if timer_obj.exists():
                timer_obj = timer_obj.get(candidate_id=request.user, template=mcqtem.template, job_id=job_obj)
                start_time = timer_obj.start_time
            else:
                timer_obj = models.ExamTimeStatus.objects.create(candidate_id=request.user, template=mcqtem.template,
                                                                 job_id=job_obj,
                                                                 start_time=datetime.datetime.now(timezone.utc))
                start_time = datetime.datetime.now(timezone.utc)
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.now(timezone.utc)
                print(start_time)
                duration=datetime.datetime.strptime(str(mcqtem.duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
                schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
                print('end mcq===========================',schedule_end_mcq)
                getjob=Scheduler.get_jobs()
                for job in getjob:
                    if job.id==str(id)+str(job_id)+str(request.user.id):
                        print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                        Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
                Scheduler.add_job(
                                end_mcq,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )                                         

            current_date = datetime.datetime.now(timezone.utc)
            elapsed_time = current_date - start_time

            elapsed_seconds = int(elapsed_time.total_seconds())
            hours = int(elapsed_seconds / 3600) % 24
            minutes = int(elapsed_seconds / 60) % 60
            seconds = int(elapsed_seconds % 60)
            print("remaininsec", elapsed_seconds)
            elapsed_time = pad_time(hours) + ":" + pad_time(minutes) + ":" + pad_time(seconds)
            time = mcqtem.duration.split(':')
            # available_seconds = int(elapsed_seconds)
            available_seconds = ((int(time[0]) * 3600) + (int(time[1])*60))-elapsed_seconds
            if mcqtem.exam_type=='random':
                get_question=models.RandomMCQExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                for l in get_question.question.all():
                    # get_time = ExamQuestionUnit.objects.get(question=mcq_Question.objects.get(id=int(l.id)))
                    que.append({'dbid': l.id, 'id': count + 1,
                                'choice_no': ['a', 'b', 'c', 'd'],
                                'question': l.question_description,
                                'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                })
                    count += 1
            else:
                if mcqtem.marking_system=='question_wise':
                    get_times = ExamQuestionUnit.objects.filter(template_id=Template_creation.objects.get(id=id))
                    for get_time in get_times:
                        que.append({'dbid': get_time.question.id, 'id': count + 1,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'question': get_time.question.question_description,
                                    'choices': [get_time.question.option_a, get_time.question.option_b, get_time.question.option_c, get_time.question.option_d]
                                    })
                        count += 1
                else:
                    print('question_wise====================question_wise',mcqtem)
                    for l in mcqtem.basic_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
                    for l in mcqtem.intermediate_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
                    for l in mcqtem.advanced_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
            count = 0
            print(que)
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/candidate_mcq_exam.html', {'time':available_seconds,'elapsed_time':elapsed_time,'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
        elif mcqtem.question_wise_time:
            get_times = ExamQuestionUnit.objects.filter(template_id=Template_creation.objects.get(id=id))
            total_time=0
            for get_time in get_times:
                print(get_time.question_time)
                time = get_time.question_time.split(':')
                available_seconds = int(time[0]) * 60 + int(time[1])
                total_time += available_seconds
                que.append({'dbid': get_time.question.id, 'id': count + 1,
                            'time': available_seconds,
                            'choice_no': ['a', 'b', 'c', 'd'],
                            'question': get_time.question.question_description,
                            'choices': [get_time.question.option_a, get_time.question.option_b, get_time.question.option_c, get_time.question.option_d]
                            })
                count += 1
            count = 0
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            Scheduler.add_job(
                            end_mcq,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )    
            getStoreData = json.dumps(que)
            print(total_time)
            return render(request, 'candidate/ATS/candidate_mcq_exam_if_question.html',
                          {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def mcq_exam_fill(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        mcqtem = ExamTemplate.objects.get(template=template_obj)
        # models.ExamTimeStatus.objects.update_or_create(candidate_id=request.user, template=mcqtem.template,
        #                                      job_id=job_obj,defaults={
        #                                      'start_time':datetime.datetime.now(timezone.utc)})
        print("=========================", mcq_data)
        mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        que = mcq_Question.objects.get(id=int(mca_que_id))
        cat_mark=0
        if mcqtem.marking_system == 'question_wise':
            get_marks = ExamQuestionUnit.objects.get(question=mcq_Question.objects.get(id=int(mca_que_id)),
                                                     template=template_obj)
            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                if mcq_ans == que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = get_marks.question_mark
                    else:
                        getmarks = get_marks.question_mark
                    check_ans = 1
                elif mcq_ans != que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = (get_marks.question_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        elif mcqtem.marking_system == 'category_wise':
            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                get_que_type = mcq_Question.objects.get(id=int(mca_que_id))
                if get_que_type.question_level.level_name == 'basic':
                    cat_mark = int(mcqtem.basic_question_marks)
                elif get_que_type.question_level.level_name == 'intermediate':
                    cat_mark = int(mcqtem.intermediate_question_marks)
                elif get_que_type.question_level.level_name == 'advance':
                    cat_mark = int(mcqtem.advanced_question_marks)
                print(mcq_ans,"=======================",que.correct_option)
                if mcq_ans == que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = cat_mark
                    else:
                        getmarks = cat_mark
                    check_ans = 1
                elif mcq_ans != que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = (cat_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        models.Mcq_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 company_id=Company.objects.get(id=job_obj.company_id.id),
                                                 question=mcq_Question.objects.get(id=que.id),
                                                 job_id=job_obj,
                                                 template=template_obj, defaults={
                'marks': getmarks,
                'status': check_ans,
                'time': mca_que_time}
                                                 )
        if mcq_data['last']:
            data['url']=str(current_site.domain+'/candidate/mcq_result/'+str(id)+'/'+str(job_id))
            data['last']=True
        else:
            print("==================================================")
            data['last'] = False
        data["status"]= True
    else:
        data["status"]= False
    return JsonResponse(data)


def mcq_result(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = Template_creation.objects.get(id=id)
    get_result = models.Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)
    get_time=models.Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj).last()
    mcqtem = ExamTemplate.objects.get(company_id=Company.objects.get(id=job_obj.company_id.id),template=template_obj)
    # total_time = datetime.datetime.strptime(mcqtem.duration+':00', '%H:%M:%S')
    # last_time = datetime.datetime.strptime(get_time.time, '%H:%M:%S')
    obain_time = 10
    obain_marks = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            # obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.question_description + """</div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/MCQ/".format(request.user.id, job_obj.id)
    getresult,created = models.Mcq_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'mcq_pdf':path +request.user.first_name+ "mcq.pdf"})
    pdfkit.from_string(a, output_path=path +request.user.first_name+ "mcq.pdf", configuration=config)



    # move to next stage process

    # onthego change
    job_workflow = JobWorkflow.objects.get(job_id=job_obj)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_stage = ''
    currentcompleted=False
    next_stage = None
    action_required=''
    reject=False
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if job_workflow.withworkflow:
        main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = WorkflowStages.objects.get(workflow=main_workflow,template=template_obj)
        config_obj = WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)
        current_stage=stage_status.stage
        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                currentcompleted=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                reject=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                action_required='Company'
                stage_status.save()
            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            action_required='Company'
            stage_status.save()

        if not reject:
            new_sequence_no = stage_status.sequence_number + 1
            if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                        sequence_number=new_sequence_no).exists():
                new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                next_stage=new_stage_status.stage
    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    
    if not next_stage==None and action_required=='':
        if next_stage.name=='Interview' :
            action_required='Company/Agency'
        else:
            action_required='Candidate'
    if current_stage!='':
        if current_stage.name=='Job Offer':
            action_required='Offer Letter Generation By Company'
        Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                    'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
                                                                    'action_required':action_required,'update_at':datetime.datetime.now()})
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/end_exam.html',{'get_result': getresult, "job_id": job_obj.id})

def start_mcq(template_id, job_id):
    print("activaaaaaaaaaate callllllledd")

def end_mcq(template_id, job_id,loginuser_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = Template_creation.objects.get(id=template_id)
    get_result = models.Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)
    get_time=models.Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj).last()
    mcqtem = ExamTemplate.objects.get(company_id=Company.objects.get(id=job_obj.company_id.id),template=template_obj)
    # total_time = datetime.datetime.strptime(mcqtem.duration+':00', '%H:%M:%S')
    # last_time = datetime.datetime.strptime(get_time.time, '%H:%M:%S')
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    obain_time = 10
    obain_marks = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            # obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.question_description + """</div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/MCQ/".format(loginuser_id, job_obj.id)
    getresult,created = models.Mcq_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'mcq_pdf':path +user_obj.first_name+ "mcq.pdf"})
    pdfkit.from_string(a, output_path=path +user_obj.first_name+ "mcq.pdf", configuration=config)



    # move to next stage process

    # onthego change
    job_workflow = JobWorkflow.objects.get(job_id=job_obj)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_stage = ''
    currentcompleted=False
    next_stage = None
    action_required=''
    reject=False
    if job_workflow.withworkflow:
        main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = WorkflowStages.objects.get(workflow=main_workflow,template=template_obj)
        config_obj = WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)
        current_stage=stage_status.stage
        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                currentcompleted=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id))
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                reject=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                action_required='Company'
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            action_required='Company'
            stage_status.save()
            
        if not reject:
            new_sequence_no = stage_status.sequence_number + 1
            if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                        sequence_number=new_sequence_no).exists():
                new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                next_stage=new_stage_status.stage
    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    
    if not next_stage==None and action_required=='':
        if next_stage.name=='Interview' :
            action_required='Company/Agency'
        else:
            action_required='Candidate'
    if current_stage!='':
        if current_stage.name=='Job Offer':
            action_required='Offer Letter Generation By Company'
        Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                    'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
                                                                    'action_required':action_required,'update_at':datetime.datetime.now()})
    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")

import requests


def coding_test(request,id, job_id):
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user, job_id__id=job_id)
    if stage_status.status == 1:
        exam_obj = CodingExamConfiguration.objects.get(template_id=template_obj)

        no_of_questions = int(exam_obj.total_question)
        question_obj = CodingExamQuestions.objects.filter(coding_exam_config_id=exam_obj)
        questions = []
        for que in question_obj:
            dict = {'id':que.id,'title':que.question_id.coding_que_title,'description':que.question_id.coding_que_description}
            questions.append(dict)
        question_no_iterator = [i for i in range(no_of_questions)]
        time = exam_obj.total_time.split(':')
        if models.ExamTimeStatus.objects.filter(candidate_id=request.user,template=template_obj,job_id__id=job_id).exists():
            start_time = models.ExamTimeStatus.objects.get(candidate_id=request.user,template=template_obj,job_id__id=job_id).start_time
            current_time = datetime.datetime.now(timezone.utc)

            diff = current_time - start_time
            seconds = int(diff.total_seconds())

            total_hour_in_second = int(time[0]) * 3600
            total_min_in_second = int(time[1]) * 60
            total_available_seconds = (total_hour_in_second + total_min_in_second) - seconds
            available_minutes = int(total_available_seconds/60)
            available_seconds = int(total_available_seconds % 60)
        else:
            available_minutes = int(time[0]) * 60 + int(time[1])
            available_seconds = 0
            models.ExamTimeStatus.objects.create(candidate_id=request.user,template=template_obj,
                                                 job_id=JobCreation.objects.get(id=job_id),start_time=datetime.datetime.now(timezone.utc))
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            duration=datetime.datetime.strptime(str(exam_obj.total_time), '%H:%M').time()
            A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
            totalsecond = A.total_seconds()
            schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            if exam_obj.technology == 'backend':
                Scheduler.add_job(
                                end_backend_coding,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )   
            else:
                Scheduler.add_job(
                        end_frontend_coding,
                        trigger=DateTrigger(run_date=schedule_end_mcq),
                        args = [id,job_id,request.user.id],
                        misfire_grace_time=6000,
                        id=str(id)+str(job_id)+str(request.user.id)
                        # replace_existing=True
                    )                              
        if request.method == 'POST':
            language = exam_obj.coding_subject_id.api_subject_id.name
            data = json.loads(request.body.decode('UTF-8'))
            url = 'https://glot.io/api/run/'+ language +'/latest'
            payload = json.dumps(data)
            print("payload",payload)
            headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8',
                       'Authorization': 'Token 6f18027a-2ea7-40cf-8b7b-4b91b49fda0a','contentType ':'application/json'}
            r = requests.post(url, data=payload, headers=headers)
            return HttpResponse(r)
        if exam_obj.technology == 'backend':
            language = exam_obj.coding_subject_id.api_subject_id.name
            return render(request, 'candidate/ATS/back_end_editor.html', {'id': id, 'job_id': job_id,
                                                                          'available_minutes':available_minutes,
                                                                          'available_seconds':available_seconds,
                                                                          'language': language,
                                                                          'stage_id':stage_status.id,
                                                                          'no_of_questions': no_of_questions,
                                                                          'question_no_iterator': question_no_iterator,
                                                                          'coding_questions': json.dumps(questions)})
        else:
            return render(request, 'candidate/ATS/frontend_editor.html', {'id': id, 'job_id': job_id,
                                                                          'available_minutes': available_minutes,
                                                                          'available_seconds': available_seconds,
                                                                          'stage_id':stage_status.id,
                                                                          'no_of_questions': no_of_questions,
                                                                          'question_no_iterator': question_no_iterator,
                                                                          'coding_questions': json.dumps(questions)})
    else:
        return HttpResponse(False)


def preview(request):
    return render(request,'candidate/ATS/preview.html')


def save_front_end_code(request,template_id,job_id):
    if request.method == 'POST':
        user_obj = User.objects.get(id=request.user.id)
        template_obj = Template_creation.objects.get(id=template_id)
        job_obj = JobCreation.objects.get(id=job_id)
        data = json.loads(request.body.decode('UTF-8'))

        question_not_attempted_count = 0
        total_question = 0
        print("\n\n================",data)
        for (que_id, html, css, js) in zip_longest(data['que_list'], data['html_codes'],
                                                              data['css_codes'], data['js_codes'],fillvalue=None):
            print('\n\n\ndata>>>>>>>>>>', que_id,'\n\n\n',html,'\n\n\n',css,'\n\n\n',js,'\n============================')
            coding_exam_que = CodingExamQuestions.objects.get(id=que_id)
            if html and css and js == '':
                question_not_attempted_count += 1
            models.CodingFrontEndExamFill.objects.update_or_create(candidate_id=user_obj,company_id=template_obj.company_id,
                                                            template=template_obj,job_id=job_obj,
                                                            exam_question_id=coding_exam_que,
                                                            defaults={'html_code':html,'css_code':css,'js_code':js})
            total_question += 1

        models.Coding_Exam_result.objects.update_or_create(candidate_id=user_obj, company_id=template_obj.company_id,
                                                           template=template_obj, job_id=job_obj,
                                                           defaults={'total_question': total_question,
                                                                     'answered': total_question - question_not_attempted_count})

        stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                            job_id=job_obj)
        stage_status.status = 2
        stage_status.save()
        Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"
        notify.send(request.user, recipient=request.user, verb="Manual",
                                description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/company")
        getjob=Scheduler.get_jobs()
        for job in getjob:
            if job.id==str(template_id)+str(job_id)+str(request.user.id):
                print(job.id,'=====',str(template_id)+str(job_id)+str(request.user.id))
                Scheduler.remove_job(str(template_id)+str(job_id)+str(request.user.id))
        return HttpResponse(True)


def save_code(request,template_id,job_id):
    if request.method == 'POST':
        user_obj = User.objects.get(id=request.user.id)
        template_obj = Template_creation.objects.get(id=template_id)
        job_obj = JobCreation.objects.get(id=job_id)
        data = json.loads(request.body.decode('UTF-8'))
        print("\n\ndata files ==>>", data['files'])
        question_not_attempted_count = 0
        total_question = 0
        for que in data['files']:
            coding_exam_que = CodingExamQuestions.objects.get(id=que['que_id'])
            if que['content'] == 'The candidate did not attempt this question':
                question_not_attempted_count += 1
            models.CodingBackEndExamFill.objects.update_or_create(candidate_id=user_obj,company_id=template_obj.company_id,
                                                        template=template_obj,job_id=job_obj,
                                                        exam_question_id=coding_exam_que,defaults={'source_code':que['content']})
            total_question += 1
        models.Coding_Exam_result.objects.update_or_create(candidate_id=user_obj,company_id=template_obj.company_id,
                                                        template=template_obj,job_id=job_obj,
                                                      defaults={'total_question':total_question,'answered':total_question-question_not_attempted_count})

        stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                            job_id=job_obj)
        stage_status.status = 2
        stage_status.save()
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"
        notify.send(request.user, recipient=request.user, verb="Manual",
                                description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/company")
        getjob=Scheduler.get_jobs()
        for job in getjob:
            if job.id==str(template_id)+str(job_id)+str(request.user.id):
                print(job.id,'=====',str(template_id)+str(job_id)+str(request.user.id))
                Scheduler.remove_job(str(template_id)+str(job_id)+str(request.user.id))
        return HttpResponse(True)
    return render(request, 'company/back_end_editor.html')

def end_backend_coding(template_id, job_id,loginuser_id):
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = Template_creation.objects.get(id=template_id)
    job_obj = JobCreation.objects.get(id=job_id)
    question_not_attempted_count = 0
    total_question = 0
    models.Coding_Exam_result.objects.update_or_create(candidate_id=user_obj,company_id=template_obj.company_id,
                                                    template=template_obj,job_id=job_obj,
                                                    defaults={'total_question':total_question,'answered':total_question-question_not_attempted_count})

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.save()

def end_frontend_coding(template_id, job_id,loginuser_id):
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = Template_creation.objects.get(id=template_id)
    job_obj = JobCreation.objects.get(id=job_id)
    question_not_attempted_count = 0
    total_question = 0
    models.Coding_Exam_result.objects.update_or_create(candidate_id=user_obj, company_id=template_obj.company_id,
                                                        template=template_obj, job_id=job_obj,
                                                        defaults={'total_question': total_question,
                                                                    'answered': total_question - question_not_attempted_count})

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.save()
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                            'action_required':'Assessment by Company','update_at':datetime.datetime.now()})

def descriptive_exam(request, id, job_id):
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    total_time=0
    if stage_status.status == 1:
        job_obj = JobCreation.objects.get(id=job_id)
        mcqtem = DescriptiveExamTemplate.objects.get(template=Template_creation.objects.get(id=id))
        mcqpaper = DescriptiveQuestionPaper.objects.get(exam_template=mcqtem)
        que = []
        count = 0
        for l in mcqtem.descriptivequestions.all():
            get_time = DescriptiveExamQuestionUnit.objects.get(question=Descriptive.objects.get(id=int(l.id)),template=Template_creation.objects.get(id=id))
            print(get_time.question_time)
            time = get_time.question_time.split(':')
            available_seconds = int(time[0]) * 60 + int(time[1])
            total_time += available_seconds
            que.append({'dbid': l.id, 'id': count + 1,
                        'time': available_seconds,
                        'question': l.paragraph_description
                        })
            count += 1
        count = 0
        start_time = datetime.datetime.now(timezone.utc)
        time_zone = pytz.timezone("Asia/Calcutta")
        schedule_date=datetime.datetime.now(timezone.utc)
        schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
        schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
        print('end mcq===========================',schedule_end_mcq)
        getjob=Scheduler.get_jobs()
        for job in getjob:
            if job.id==str(id)+str(job_id)+str(request.user.id):
                print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
        Scheduler.add_job(
                        end_descriptive,
                        trigger=DateTrigger(run_date=schedule_end_mcq),
                        args = [id,job_id,request.user.id],
                        misfire_grace_time=6000,
                        id=str(id)+str(job_id)+str(request.user.id)
                        # replace_existing=True
                    )    
        getStoreData = json.dumps(que)
        return render(request, 'candidate/ATS/candidate_descriptive_exam.html',
                      {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def descriptive_exam_fill(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = Template_creation.objects.get(id=id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        mcqtem = DescriptiveExamTemplate.objects.get(template=template_obj)
        print("=========================", mcq_data)
        # mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        ans = mcq_data['ans']
        que = Descriptive.objects.get(id=int(mca_que_id))
        if ans == '':
            check_ans = 0
        else:
            check_ans = 1
        available_m = DescriptiveExamQuestionUnit.objects.get(question=Descriptive.objects.get(id=que.id),template=template_obj)
        models.Descriptive_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 company_id=Company.objects.get(id=job_obj.company_id.id),
                                                 question=Descriptive.objects.get(id=que.id),
                                                 job_id=job_obj,
                                                 template=template_obj, defaults={
                                                    'available_marks':available_m.question_mark,
                                                    'ans':ans,
                                                    'status': check_ans,
                                                    'time': mca_que_time}
                                                 )
        if mcq_data['last'] == True:
            data['url']=str(current_site.domain+'/candidate/descriptive_result/'+str(id)+'/'+str(job_id))
            data['last']=True

        else:
            print("==================================================")
            data['last'] = False
        data["status"] = True
    else:
        data["status"]= False
    return JsonResponse(data)


def descriptive_result(request, id, job_id):
    
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = Template_creation.objects.get(id=id)
    get_result = models.Descriptive_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)

    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:

            ans_que+=1
        elif i.status == -1:

            ans_que+=1
        elif i.status == 0:

            no_ans_que+=1
        total_que+=1

    getresult,created = models.Descriptive_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':total_que, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10,
                                          })

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    print("=============================================================")
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    notify.send(request.user, recipient=request.user, verb="Manual",
                            description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/descriptive_end_exam.html',{'get_result':getresult,'job_id':job_id})


def end_descriptive(template_id, job_id,loginuser_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = Template_creation.objects.get(id=template_id)
    get_result = models.Descriptive_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)

    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:

            ans_que+=1
        elif i.status == -1:

            ans_que+=1
        elif i.status == 0:

            no_ans_que+=1
        total_que+=1

    getresult,created = models.Descriptive_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':total_que, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10,
                                          })

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    print("=============================================================")
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})

# Image exam


def image_exam(request, id, job_id):
    # 1=right
    # -1=Wrong
    # 0=skip
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    if stage_status.status == 1:
        job_obj = JobCreation.objects.get(id=job_id)
        mcqtem = ImageExamTemplate.objects.get(template=Template_creation.objects.get(id=id))
        if not mcqtem.exam_type == 'custom':
            questions = ImageQuestion.objects.filter(company_id=User.objects.get(id=mcqtem.company_id.id),subject=mcqtem.subject.id)
            basic_questions = list(questions.filter(question_level__level_name='basic'))
            intermediate_questions =list( questions.filter(question_level__level_name='intermediate'))
            advanced_questions =list( questions.filter(question_level__level_name='advance'))
            random.shuffle(basic_questions)
            random.shuffle(intermediate_questions)
            random.shuffle(advanced_questions)
            basic_questions = random.sample(basic_questions,int(mcqtem.basic_questions_count))
            intermediate_questions = random.sample(intermediate_questions,int( mcqtem.intermediate_questions_count))
            advanced_questions = random.sample(advanced_questions,int(mcqtem.advanced_questions_count))
            if models.RandomImageExam.objects.filter(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id)).exists():
                delete_question=models.RandomImageExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                delete_question.question.clear()
                for i in basic_questions:
                    delete_question.question.add(i)
                for i in intermediate_questions:
                    delete_question.question.add(i)
                for i in advanced_questions:
                    delete_question.question.add(i)
            else:
                add_random=models.RandomImageExam.objects.create(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                for i in basic_questions:
                    add_random.question.add(i)
                for i in intermediate_questions:
                    add_random.question.add(i)
                for i in advanced_questions:
                    add_random.question.add(i)
        # imagepaper = ImageQuestionPaper.objects.get(exam_template=mcqtem)
        que = []
        count = 0
        if not mcqtem.question_wise_time:
            time=mcqtem.duration.split(':')
            timer_obj = models.ExamTimeStatus.objects.filter(candidate_id=request.user, template=mcqtem.template,
                                                             job_id=job_obj)
            if timer_obj.exists():
                timer_obj = timer_obj.get(candidate_id=request.user, template=mcqtem.template, job_id=job_obj)
                start_time = timer_obj.start_time
            else:
                # timer_obj = models.ExamTimeStatus.objects.create(candidate_id=request.user, template=mcqtem.template,
                #                                                  job_id=job_obj,
                #                                                  start_time=datetime.datetime.now(timezone.utc))
                # start_time = datetime.datetime.now(timezone.utc)
                start_time = datetime.datetime.now(timezone.utc)
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.now(timezone.utc)
                print(start_time)
                duration=datetime.datetime.strptime(str(mcqtem.duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
                schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
                print('end image===========================',schedule_end_mcq)
                getjob=Scheduler.get_jobs()
                for job in getjob:
                    if job.id==str(id)+str(job_id)+str(request.user.id):
                        Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
                Scheduler.add_job(
                                end_image,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )             
            current_date = datetime.datetime.now(timezone.utc)
            print(current_date)
            print(start_time)
            elapsed_time = current_date - start_time

            elapsed_seconds = int(elapsed_time.total_seconds())
            hours = int(elapsed_seconds / 3600) % 24
            minutes = int(elapsed_seconds / 60) % 60
            seconds = int(elapsed_seconds % 60)
            print("remaininsec", elapsed_seconds)
            elapsed_time = pad_time(hours) + ":" + pad_time(minutes) + ":" + pad_time(seconds)
            time = mcqtem.duration.split(':')
            # available_seconds = int(elapsed_seconds)
            available_seconds = ((int(time[0]) * 3600) + (int(time[1])*60)) - elapsed_seconds
            if mcqtem.exam_type == 'random':
                get_question = models.RandomImageExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=User.objects.get(id=job_obj.company_id.id))
                for l in get_question.question.all():
                    imageoption = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                    # options = [imageoption.file1.url if imageoption.file1 else None]
                    que.append({'dbid': l.id, 'id': count + 1,
                                'question': l.image_que_description,
                                'q_image':l.question_file.url,
                                'choice_no': ['a', 'b', 'c', 'd'],
                                'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                })
                    print(que)
                    count += 1
            else:
                print("=====================================")
                if mcqtem.marking_system=='question_wise':
                    get_times = ImageExamQuestionUnit.objects.filter(template_id=Template_creation.objects.get(id=id))
                    for get_time in get_times:
                        print("======================================s")
                        imageoption = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=get_time.question.id))
                        que.append({'dbid': get_time.question.id, 'id': count + 1,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'question': get_time.question.image_que_description,
                                    'q_image':get_time.question.question_file.url,
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                else:
                    for l in mcqtem.basic_questions.all():
                        print(l.id)
                        imageoption=ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                    for l in mcqtem.intermediate_questions.all():
                        print(l.id)
                        imageoption=ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage': [imageoption.file1.url if imageoption.file1 else None,
                                                    imageoption.file2.url if imageoption.file2 else None,
                                                    imageoption.file3.url if imageoption.file3 else None,
                                                    imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                    for l in mcqtem.advanced_questions.all():
                        print(l.id)
                        imageoption=ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None for imageoptions in imageoption]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
            count = 0
            print("\n\nque",que)
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/candidate_image_exam.html', {'time':available_seconds,'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
        elif mcqtem.question_wise_time:
            get_times = ImageExamQuestionUnit.objects.filter(template_id=Template_creation.objects.get(id=id))
            total_time=0
            for get_time in get_times:
                print("======================================s")
                time = get_time.question_time.split(':')
                available_seconds = int(time[0]) * 60 + int(time[1])
                imageoption = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=get_time.question.id))
                total_time += available_seconds
                que.append({'dbid': get_time.question.id, 'id': count + 1,
                            'time': available_seconds,
                            'choice_no': ['a', 'b', 'c', 'd'],
                            'question': get_time.question.image_que_description,
                            'q_image':get_time.question.question_file.url,
                            'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                            'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                            })
                count += 1
            count = 0
            print(total_time)
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end image===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            
            Scheduler.add_job(
                            end_image,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )    
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/candidate_image_exam_if_question.html',
                          {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def image_exam_fill(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        print(mcq_data)
        mcqtem = ImageExamTemplate.objects.get(template=template_obj)
        print("=========================", mcq_data)
        mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        image_path=mcq_data['image_path']
        print('\n\nimage_path', image_path)
        s2 = "media/"
        # image_path=image_path[image_path.index(s2) + len(s2):]
        que = ImageQuestion.objects.get(id=int(mca_que_id))
        que_ans = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=int(mca_que_id)))
        cat_mark=0

        if mcqtem.marking_system == 'question_wise':
            get_marks = ImageExamQuestionUnit.objects.get(question=ImageQuestion.objects.get(id=int(mca_que_id)),
                                                          template=template_obj)

            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                if mcq_ans == que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = get_marks.question_mark
                    else:
                        getmarks = get_marks.question_mark
                    check_ans = 1
                elif mcq_ans != que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = (get_marks.question_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        elif mcqtem.marking_system == 'category_wise':

            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                get_que_type = ImageQuestion.objects.get(id=int(mca_que_id))
                if get_que_type.question_level.level_name == 'basic':
                    cat_mark = int(mcqtem.basic_question_marks)
                elif get_que_type.question_level.level_name == 'intermediate':
                    cat_mark = int(mcqtem.intermediate_question_marks)
                elif get_que_type.question_level.level_name == 'advance':
                    cat_mark = int(mcqtem.advanced_question_marks)
                if mcq_ans == que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = cat_mark
                    else:
                        getmarks = cat_mark
                    check_ans = 1
                elif mcq_ans != que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = (cat_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        models.Image_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 company_id=Company.objects.get(id=job_obj.company_id.id),
                                                 question=ImageQuestion.objects.get(id=que.id),
                                                 job_id=JobCreation.objects.get(id=job_id),
                                                 template=template_obj, defaults={
                'ansfile' : image_path,
                'marks': getmarks,
                'status': check_ans,
                'time': mca_que_time}
                                                 )
        if mcq_data['last'] == True:
            data['url']=str(current_site.domain+'/candidate/image_result/'+str(id)+'/'+str(job_id))
            data['last']=True


        else:
            print("==================================================")
            data['last'] = False
        data["status"]= True
    else:
        data["status"]= False
    return JsonResponse(data)

import base64


def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    if not os.path.isfile(image_file):
        return None

    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
        print((str(encoded_string)[-1:-50:-1]))
    return 'data:image/%s;base64,%s' % (format, str(encoded_string)[2:-2:])


def image_result(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    get_result = models.Image_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)
    mcqtem = ImageExamTemplate.objects.get(company_id=job_obj.company_id, template=template_obj)
    obain_marks = 0
    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.image_que_description + """<img height="300px" width="300px" src=\""""+ image_as_base64(settings.MEDIA_ROOT[0:-7:] +i.question.question_file.url) +"""\"></div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/Image/".format(request.user.id, job_obj.id)
    getresult,created = models.Image_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'image_pdf':path +request.user.first_name+ "image.pdf"})

    pdfkit.from_string(a, output_path=path+request.user.first_name + "image.pdf")

    job_workflow = JobWorkflow.objects.get(job_id=job_obj)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    if job_workflow.withworkflow:
        main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = WorkflowStages.objects.get(workflow=main_workflow, template=template_obj)
        config_obj = WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)

        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=''
                next_stage=None
                action_required=''
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    current = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    current_stage=current.stage
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no+1).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no+1)
                    next_stage=new_stage_status.stage
                    print(next_stage)
                if not next_stage==None:
                    if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                    else:
                        action_required='Perform By Candidate'
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'current_stage':current_stage,'next_stage':next_stage,
                                                                'action_required':action_required,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'reject':True,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'On Hold by Company','update_at':datetime.datetime.now()})
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            stage_status.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            notify.send(request.user, recipient=request.user, verb="Manual",
                                    description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/company")

    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    
    return render(request, 'candidate/ATS/end_exam.html',{'get_result':getresult,'job_id':job_id})


def end_image(template_id, job_id,loginuser_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=template_id)
    user_obj = User.objects.get(id=loginuser_id)
    get_result = models.Image_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)
    mcqtem = ImageExamTemplate.objects.get(company_id=job_obj.company_id, template=template_obj)
    obain_marks = 0
    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.image_que_description + """<img height="300px" width="300px" src=\""""+ image_as_base64(settings.MEDIA_ROOT[0:-7:] +i.question.question_file.url) +"""\"></div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/Image/".format(loginuser_id, job_obj.id)
    getresult,created = models.Image_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'image_pdf':path +user_obj.first_name+ "image.pdf"})

    pdfkit.from_string(a, output_path=path+user_obj.first_name + "image.pdf")

    job_workflow = JobWorkflow.objects.get(job_id=job_obj)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if job_workflow.withworkflow:
        main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = WorkflowStages.objects.get(workflow=main_workflow, template=template_obj)
        config_obj = WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)

        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=''
                next_stage=None
                action_required=''
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    current = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    current_stage=current.stage
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no+1).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no+1)
                    next_stage=new_stage_status.stage
                if not next_stage==None:
                    if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                    else:
                        action_required='Perform By Candidate'
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'current_stage':current_stage,'next_stage':next_stage,
                                                                'action_required':action_required,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'reject':True,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'On Hold by Company','update_at':datetime.datetime.now()})
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            stage_status.save()

    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()

    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")

# audio

def pad_time(number):
    if number<10:
        return "0"+str(number)
    else:
        return str(number)


def audio_exam(request, id, job_id):
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    if stage_status.status == 1:
        job_obj = JobCreation.objects.get(id=job_id)
        mcqtem = AudioExamTemplate.objects.get(template=Template_creation.objects.get(id=id))
        mcqpaper = AudioQuestionPaper.objects.get(exam_template=mcqtem)
        timer_obj = models.ExamTimeStatus.objects.filter(candidate_id=request.user,template = mcqtem.template,job_id=job_obj)
        if timer_obj.exists():
            timer_obj = timer_obj.get(candidate_id=request.user,template = mcqtem.template,job_id=job_obj)
            start_time = timer_obj.start_time
        else:
            timer_obj = models.ExamTimeStatus.objects.create(candidate_id=request.user,template=mcqtem.template,job_id=job_obj,start_time=datetime.datetime.now(timezone.utc))
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            print(start_time)
            duration=datetime.datetime.strptime(str(mcqtem.total_exam_time), '%H:%M:%S').time()
            A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
            totalsecond = A.total_seconds()
            schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            Scheduler.add_job(
                            end_audio,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )                           
        current_date = datetime.datetime.now(timezone.utc)

        elapsed_time = current_date-start_time

        elapsed_seconds = int(elapsed_time.total_seconds())
        hours = int(elapsed_seconds / 3600 ) % 24
        minutes = int(elapsed_seconds / 60 ) % 60
        seconds = int(elapsed_seconds % 60)
        print("remaininsec",elapsed_seconds)
        elapsed_time = pad_time(hours)+":"+pad_time( minutes)+":" + pad_time(seconds)
        # time = mcqtem.total_exam_time.split(':')
        # # available_seconds = int(elapsed_seconds)
        # elapsed_time = (int(time[0]) * 60) + (int(time[1]))
        print("==========================================",elapsed_time)
        que = []
        count = 0
        print(mcqtem.audioquestions.all())
        for l in mcqtem.audioquestions.all():
            get_time = AudioExamQuestionUnit.objects.get(question=Audio.objects.get(id=int(l.id)),template=Template_creation.objects.get(id=id))
            que.append({'dbid': l.id, 'id': count + 1,
                        'time': get_time.question_time,
                        'question': l.paragraph_description
                        })
            count += 1
        count = 0
        getStoreData = json.dumps(que)
        return render(request, 'candidate/ATS/candidate_audio_video_exam_if_question.html',
                      {'getStoreData': getStoreData,'stage_id':stage_status.id, 'job_obj': job_obj, 'temp_id': mcqpaper.exam_template.template.id,"elapsed_time":elapsed_time,'total_exam_time':mcqtem.total_exam_time,"is_video":mcqtem.is_video})

    else:
        return HttpResponse(False)

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile


def audio_exam_fill(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    data = {}
    template_creation_obj = Template_creation.objects.get(id=id)
    audio_exam_template = AudioExamTemplate.objects.get(template=template_creation_obj)
    audio_question_paper = AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    current_site = get_current_site(request)
    if request.method == 'POST':
        attempt,updated = models.AudioExamAttempt.objects.update_or_create(candidate_id=request.user,company_id=audio_question_paper.company_id,audio_question_paper = audio_question_paper,job_id = job_obj)
        attempt.audio_question_attempts.remove()
        # all_blobs = request.POST.get("blobs")
        all_questions = request.POST.get("questions")
        all_questions = all_questions.split(",")
        for i in all_questions:
            audio_question = audio_question_paper.exam_question_units.get(question=Audio.objects.get(id=int(i)))
            answer = request.FILES.get(str(i) + "blob")

            if audio_question_paper.exam_template.is_video:
                file_extension = ".mkv"
            else:
                file_extension = ".wav"
            question_attempt = models.AudioExamQuestionAttemptUnit.objects.create(audio_question=audio_question)
            file_name_tag= str(question_attempt.id)+file_extension
            fs = FileSystemStorage() #defaults to   MEDIA_ROOT
            if answer == None:
                filename = None
            else:
                filename = fs.save("audio_exam_recordings/"+str(question_attempt.id)+file_extension, answer)
                file_url = fs.url(filename)

            question_attempt.answer.name = filename
            question_attempt.save()

            attempt.audio_question_attempts.add(question_attempt)
        attempt.save()
        data["status"] = True
    # else:
    #     data["status"] = False
    return JsonResponse(data)


def audio_result(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = Template_creation.objects.get(id=id)
    audio_exam_template = AudioExamTemplate.objects.get(template=template_obj)
    audio_question_paper = AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    current_site = get_current_site(request)
    attempt = models.AudioExamAttempt.objects.get(candidate_id=request.user,
                                                         company_id=audio_question_paper.company_id,
                                                         audio_question_paper=audio_question_paper, job_id=job_obj)
    print("==========================",attempt.audio_question_attempts.all())
    get_result = {'total_question':len(attempt.audio_question_attempts.all())}
    ans_count=0
    noans_count=0
    for result in attempt.audio_question_attempts.all():
        if result.answer:
            ans_count+=1
        else:
            noans_count+=1
    get_result['answered']=ans_count
    get_result['not_answered']=noans_count
    obain_time = 0
    total_que = 0
    ans_que = 0
    no_ans_que = 0
    for i in attempt.audio_question_attempts.all():
        if i.answer != '':
            ans_que += 1
        else :
            no_ans_que += 1
        total_que += 1

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    notify.send(request.user, recipient=request.user, verb="Manual",
                            description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/audio_end_exam.html', {'get_result': 'getresult','job_id':job_id})

def end_audio(template_id, job_id,loginuser_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = Template_creation.objects.get(id=template_id)
    audio_exam_template = AudioExamTemplate.objects.get(template=template_obj)
    audio_question_paper = AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    attempt = models.AudioExamAttempt.objects.get(candidate_id=user_obj,
                                                         company_id=audio_question_paper.company_id,
                                                         audio_question_paper=audio_question_paper, job_id=job_obj)
    print("==========================",attempt.audio_question_attempts.all())
    get_result = {'total_question':len(attempt.audio_question_attempts.all())}
    ans_count=0
    noans_count=0
    for result in attempt.audio_question_attempts.all():
        if result.answer:
            ans_count+=1
        else:
            noans_count+=1
    get_result['answered']=ans_count
    get_result['not_answered']=noans_count
    obain_time = 0
    total_que = 0
    ans_que = 0
    no_ans_que = 0
    for i in attempt.audio_question_attempts.all():
        if i.answer != '':
            ans_que += 1
        else :
            no_ans_que += 1
        total_que += 1

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})

def create_interview_link():
    link = get_random_string(length=20)
    if InterviewSchedule.objects.filter(interview_link=link).exists():
        return create_interview_link()
    else:
        return link


# def applied_job_detail(request, id,company_type):
#     if company_type=='company':
#         job_obj = JobCreation.objects.get(id=id)
#         current_stage==None
#         workflow = JobWorkflow.objects.get(job_id=job_obj)
#         candidate_obj = User.objects.get(id=request.user.id)
#         workflow_stages = WorkflowStages.objects.filter(workflow=workflow.workflow_id,display=True).order_by('sequence_number')
#         stages_status = CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
#                                                                     candidate_id=candidate_obj,
#                                                                     job_id=job_obj).order_by('sequence_number')

#         if request.method == 'POST':
            
#             if 'reschedule_interview' in request.POST:
#                 date_time = '<ul>'
#                 for (date,time) in zip_longest(request.POST.getlist('interview_date'),request.POST.getlist('interview_time'),fillvalue=None):
#                     date_time += """<li><b>""" + str(date) + ' ' + str(time) + """</b></li>"""
#                 date_time += '</ul>'
#                 date_time += """<p>""" + request.POST.get('reschedule_instruction') + """</p>"""
#                 interview_schedule_obj.reschedule_message = date_time
#                 interview_schedule_obj.is_accepted = False
#                 interview_schedule_obj.status = 0
#                 interview_schedule_obj.save()
#                 all_assign_users = CompanyAssignJob.objects.filter(job_id=job_obj)
#                 if not current_stage==None:
#                     for i in all_assign_users:
#                         if i.recruiter_type_internal:
#                             if i.recruiter_id.id != request.user.id:
#                                 notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Reschedule",
#                                                                                     description="Candidate requested for reschedule, please provide new timing.",image="/static/notifications/icon/company/Application_Review.png",
#                                                                                     target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
#                                                                                         job_obj.id))
#                 Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
#                                                                     'action_required':'Reschedule interview by Company','update_at':datetime.datetime.now()})
#             elif 'withdraw_candidate' in request.POST:
#                 CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
#                                                                 job_id=job_obj,
#                                                                 company_id=job_obj.company_id,
#                                                                 defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
#                 Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=job_obj.company_id,defaults={
#                                                                     'withdraw':True,'update_at':datetime.datetime.now()})
#                 current_site = get_current_site(request)
#                 header=request.is_secure() and "https" or "http"
#                 notify.send(request.user, recipient=request.user, verb="Withdraw",
#                                 description="You have withdrawn your application from Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
#                                 target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
#                                     job_obj.id)+"/company")
#             else:
#                 interview_schedule_id = request.POST.get('interview_schedule_data')
#                 interview_schedule_obj = InterviewSchedule.objects.get(id=interview_schedule_id)
#                 link = create_interview_link()
#                 interview_schedule_obj.is_accepted = True
#                 interview_schedule_obj.interview_link = link
#                 interview_schedule_obj.save()
#                 # Date Trigger
#                 Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
#                                                                     'action_required':'By Both','update_at':datetime.datetime.now()})
#                 time_zone = pytz.timezone("Asia/Calcutta")
#                 schedule_date=datetime.datetime.combine(datetime.datetime.strptime(str(interview_schedule_obj.date),'%Y-%m-%d').date(),datetime.datetime.strptime(str(interview_schedule_obj.time), '%H:%M:%S').time())
#                 schedule_activelink = schedule_date - datetime.timedelta(minutes=15)
#                 schedule_activelink = time_zone.localize(schedule_activelink)
#                 schedule_activelink = schedule_activelink.astimezone(pytz.utc)
#                 print(schedule_activelink)
#                 print("sdasdsadsa",datetime.datetime.now())
#                 all_assign_users = CompanyAssignJob.objects.filter(job_id=job_obj)
#                 if not current_stage==None:
#                     for i in all_assign_users:
#                         if i.recruiter_type_internal:
#                             if i.recruiter_id.id != request.user.id:
#                                 notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Confirmed",
#                                                                                     description="Candidate confirmed the InterView time.",image="/static/notifications/icon/company/Application_Review.png",
#                                                                                     target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
#                                                                                         job_obj.id))
#                 Scheduler.add_job(
#                                 activate_link,
#                                 trigger=DateTrigger(run_date=schedule_activelink),
#                                 args = [interview_schedule_obj],
#                                 misfire_grace_time=6000
#                                 # replace_existing=True
#                             )
#                 duration=datetime.datetime.strptime(str(interview_schedule_obj.interview_duration), '%H:%M').time()
#                 A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
#                 totalsecond = A.total_seconds()
#                 schedule_deactivelink = schedule_date + datetime.timedelta(seconds=totalsecond)
#                 schedule_deactivelink = time_zone.localize(schedule_deactivelink)
#                 schedule_deactivelink = schedule_deactivelink.astimezone(pytz.utc)
#                 print(schedule_deactivelink)
#                 Scheduler.add_job(
#                                 deactivate_link,
#                                 trigger=DateTrigger(run_date=schedule_deactivelink),
#                                 args = [interview_schedule_obj],
#                                 misfire_grace_time=6000
#                                 # replace_existing=True
#                             )
                
#         interview_schedule_data = None
#         job_offer_data = None
#         custom_round_data = None
#         stages_data = []
#         for stage in stages_status:
#             stage_dict = {'stage': stage, 'result': ''}
#             if stage.stage.name == 'Custom':
#                 custom_template = CustomTemplate.objects.filter(company_id=stage.company_id,template=stage.template)
#                 if custom_template.exists():
#                     custom_template = custom_template[0]
#                     custom_round_data = CustomResult.objects.filter(candidate_id=stage.candidate_id,company_id=stage.company_id,
#                                                 job_id=stage.job_id,custom_template=custom_template)
#                     custom_round_data = custom_round_data.first() if custom_round_data.exists() else None
#             if stage.stage.name == 'Interview':

#                 interview_schedule_obj = InterviewSchedule.objects.filter(candidate_id=candidate_obj,
#                                                                                 job_id=job_obj,
#                                                         company_id=stage.company_id,
#                                                         template=stage.template,
#                                                         job_stages_id=stage)
#                 print('\n\nin Interview',interview_schedule_obj)
#                 if interview_schedule_obj.exists():
#                     interview_schedule_data = interview_schedule_obj[0]

#             if stage.stage.name == 'Job Offer':
#                 print('\n\nin Job Offer')
#                 job_offer_obj = JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
#                                                                                 company_id=stage.company_id,
#                                                                                 job_stages_id=stage)
#                 if job_offer_obj.exists():
#                     job_offer_data = job_offer_obj[0]

#             if stage.status == 2 or stage.status == -1 or stage.status == 3:
#                 if stage.stage.name == 'JCR':
#                     jcr_result = models.JcrRatio.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
#                                                 template=stage.template)
#                     stage_dict['result'] = jcr_result

#                 if stage.stage.name == 'Prerequisites':
#                     prerequisites_result = models.PreRequisitesFill.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
#                                                 template=stage.template)
#                     stage_dict['result'] = prerequisites_result

#                 if stage.stage.name == 'MCQ Test':
#                     if not stage.reject_by_candidate:
#                         mcq_test_result = models.Mcq_Exam_result.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
#                                                     template=stage.template)
#                         print('\n\n \nmcq_test_result', mcq_test_result)
#                         stage_dict['result'] = mcq_test_result
#                     else:
#                         stage_dict['result'] = None

#                 if stage.stage.name == 'Descriptive Test':
#                     if not stage.reject_by_candidate:
#                         descriptive_result = models.Descriptive_Exam_result.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
#                                                     template=stage.template)
#                         stage_dict['result'] = descriptive_result
#                     else:
#                         stage_dict['result'] = None


#                 if stage.stage.name == 'Image Test':
#                     if not stage.reject_by_candidate:
#                         image_result = models.Image_Exam_result.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
#                                                     template=stage.template)
#                         stage_dict['result'] = image_result
#                     else:
#                         stage_dict['result'] = None

#             stages_data.append(stage_dict)

#         print('stages_data>>>>>>>>>>>>>>>>>', stages_data)
#         chat_internal =CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,company_id=job_obj.company_id)

#         candidate_job_status = None
#         if CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
#             candidate_job_status = CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)

#         candidate_apply_details = None
#         if AppliedCandidate.objects.filter(candidate=candidate_obj,company_id=job_obj.company_id).exists():
#             candidate_apply_details = AppliedCandidate.objects.get(candidate_id=candidate_obj, job_id=job_obj)
#         return render(request, 'candidate/ATS/applied-candidates-details.html',
#                   {'workflow_stages': workflow_stages, 'job_obj': job_obj,'stages_status':stages_status,'candidate_apply_details':candidate_apply_details,
#                    'stages_data':stages_data,'interview_schedule_data':interview_schedule_data,
#                    'job_offer_data':job_offer_data,'chat_internal':chat_internal,'custom_round_data':custom_round_data,
#                    'candidate_job_status':candidate_job_status})
#     if company_type=='agency':
        job_obj = AgencyModels.JobCreation.objects.get(id=id)
        current_stage=None
        workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
        candidate_obj = User.objects.get(id=request.user.id)
        workflow_stages = AgencyModels.WorkflowStages.objects.filter(workflow=workflow.workflow_id,display=True).order_by('sequence_number')
        stages_status = AgencyModels.CandidateJobStagesStatus.objects.filter(agency_id=job_obj.agency_id,
                                                                    candidate_id=candidate_obj,
                                                                    job_id=job_obj).order_by('sequence_number')

        if request.method == 'POST':
            
            if 'reschedule_interview' in request.POST:
                date_time = '<ul>'
                for (date,time) in zip_longest(request.POST.getlist('interview_date'),request.POST.getlist('interview_time'),fillvalue=None):
                    date_time += """<li><b>""" + str(date) + ' ' + str(time) + """</b></li>"""
                date_time += '</ul>'
                date_time += """<p>""" + request.POST.get('reschedule_instruction') + """</p>"""
                interview_schedule_obj.reschedule_message = date_time
                interview_schedule_obj.is_accepted = False
                interview_schedule_obj.status = 0
                interview_schedule_obj.save()
                all_assign_users = AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj)
                if not current_stage==None:
                    for i in all_assign_users:
                        if i.recruiter_type_internal:
                            if i.recruiter_id.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Reschedule",
                                                                                    description="Candidate requested for reschedule, please provide new timing.",image="/static/notifications/icon/company/Application_Review.png",
                                                                                    target_url=header+"://"+current_site.domain+"/agency/agency_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                        job_obj.id))
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
                #                                                     'action_required':'Reschedule interview by Company','update_at':datetime.datetime.now()})
            elif 'withdraw_candidate' in request.POST:
                AgencyModels.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                agency_id=job_obj.agency_id,
                                                                defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=job_obj.company_id,defaults={
                #                                                     'withdraw':True,'update_at':datetime.datetime.now()})
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                notify.send(request.user, recipient=request.user, verb="Withdraw",
                                description="You have withdrawn your application from Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/agency")
            else:
                interview_schedule_id = request.POST.get('interview_schedule_data')
                interview_schedule_obj = AgencyModels.InterviewSchedule.objects.get(id=interview_schedule_id)
                link = create_interview_link()
                interview_schedule_obj.is_accepted = True
                interview_schedule_obj.interview_link = link
                interview_schedule_obj.save()
                # Date Trigger
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
                #                                                     'action_required':'By Both','update_at':datetime.datetime.now()})
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.combine(datetime.datetime.strptime(str(interview_schedule_obj.date),'%Y-%m-%d').date(),datetime.datetime.strptime(str(interview_schedule_obj.time), '%H:%M:%S').time())
                schedule_activelink = schedule_date - datetime.timedelta(minutes=15)
                schedule_activelink = time_zone.localize(schedule_activelink)
                schedule_activelink = schedule_activelink.astimezone(pytz.utc)
                print(schedule_activelink)
                print("sdasdsadsa",datetime.datetime.now())
                all_assign_users = AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj)
                if not current_stage==None:
                    for i in all_assign_users:
                        if i.recruiter_type_internal:
                            if i.recruiter_id.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Confirmed",
                                                                                    description="Candidate confirmed the InterView time.",image="/static/notifications/icon/company/Application_Review.png",
                                                                                    target_url=header+"://"+current_site.domain+"/agency/agency_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                        job_obj.id))
                Scheduler.add_job(
                                activate_link,
                                trigger=DateTrigger(run_date=schedule_activelink),
                                args = [interview_schedule_obj],
                                misfire_grace_time=6000
                                # replace_existing=True
                            )
                duration=datetime.datetime.strptime(str(interview_schedule_obj.interview_duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_deactivelink = schedule_date + datetime.timedelta(seconds=totalsecond)
                schedule_deactivelink = time_zone.localize(schedule_deactivelink)
                schedule_deactivelink = schedule_deactivelink.astimezone(pytz.utc)
                print(schedule_deactivelink)
                Scheduler.add_job(
                                deactivate_link,
                                trigger=DateTrigger(run_date=schedule_deactivelink),
                                args = [interview_schedule_obj],
                                misfire_grace_time=6000
                                # replace_existing=True
                            )
                
        interview_schedule_data = None
        job_offer_data = None
        custom_round_data = None
        stages_data = []
        for stage in stages_status:
            stage_dict = {'stage': stage, 'result': ''}
            if stage.stage.name == 'Custom':
                custom_template = AgencyModels.CustomTemplate.objects.filter(agency_id=stage.agency_id,template=stage.template)
                if custom_template.exists():
                    custom_template = custom_template[0]
                    custom_round_data = AgencyModels.CustomResult.objects.filter(candidate_id=stage.candidate_id,agency_id=stage.agency_id,
                                                job_id=stage.job_id,custom_template=custom_template)
                    custom_round_data = custom_round_data.first() if custom_round_data.exists() else None
            if stage.stage.name == 'Interview':

                interview_schedule_obj = AgencyModels.InterviewSchedule.objects.filter(candidate_id=candidate_obj,
                                                                                job_id=job_obj,
                                                        agency_id=stage.agency_id,
                                                        template=stage.template,
                                                        job_stages_id=stage)
                print('\n\nin Interview',interview_schedule_obj)
                if interview_schedule_obj.exists():
                    interview_schedule_data = interview_schedule_obj[0]

            if stage.stage.name == 'Job Offer':
                print('\n\nin Job Offer')
                job_offer_obj = AgencyModels.JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
                                                                                agency_id=stage.agency_id,
                                                                                job_stages_id=stage)
                if job_offer_obj.exists():
                    job_offer_data = job_offer_obj[0]

            if stage.status == 2 or stage.status == -1 or stage.status == 3:
                if stage.stage.name == 'JCR':
                    jcr_result = models.JcrRatio.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                template=stage.template)
                    stage_dict['result'] = jcr_result

                if stage.stage.name == 'Prerequisites':
                    prerequisites_result = models.Agency_PreRequisitesFill.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                template=stage.template)
                    stage_dict['result'] = prerequisites_result

                if stage.stage.name == 'MCQ Test':
                    if not stage.reject_by_candidate:
                        mcq_test_result = models.Agency_Mcq_Exam_result.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        print('\n\n \nmcq_test_result', mcq_test_result)
                        stage_dict['result'] = mcq_test_result
                    else:
                        stage_dict['result'] = None

                if stage.stage.name == 'Descriptive Test':
                    if not stage.reject_by_candidate:
                        descriptive_result = models.AgencyDescriptive_Exam_result.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        stage_dict['result'] = descriptive_result
                    else:
                        stage_dict['result'] = None


                if stage.stage.name == 'Image Test':
                    if not stage.reject_by_candidate:
                        image_result = models.AgencyImage_Exam_result.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        stage_dict['result'] = image_result
                    else:
                        stage_dict['result'] = None

            stages_data.append(stage_dict)

        print('stages_data>>>>>>>>>>>>>>>>>', stages_data)
        chat_internal =AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,agency_id=job_obj.agency_id)

        candidate_job_status = None
        if AgencyModels.CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
            candidate_job_status = AgencyModels.CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)

        candidate_apply_details = None
        if AgencyModels.AppliedCandidate.objects.filter(candidate=candidate_obj,agency_id=job_obj.agency_id).exists():
            candidate_apply_details = AgencyModels.AppliedCandidate.objects.get(candidate_id=candidate_obj, job_id=job_obj)
        return render(request, 'candidate/ATS/agency_applied-candidates-details.html',
                    {'workflow_stages': workflow_stages, 'job_obj': job_obj,'stages_status':stages_status,'candidate_apply_details':candidate_apply_details,
                    'stages_data':stages_data,'interview_schedule_data':interview_schedule_data,
                    'job_offer_data':job_offer_data,'chat_internal':chat_internal,'custom_round_data':custom_round_data,
                    'candidate_job_status':candidate_job_status})

def activate_link(interview_schedule_obj):
    interview_schedule_obj.interview_start_button_status=True
    interview_schedule_obj.save()
    notify.send(interview_schedule_obj.candidate_id, recipient=interview_schedule_obj.candidate_id, verb="Interview",
                            description="Your Live interview session is about to start in 15 min",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                interview_schedule_obj.job_id.id)+"/company")
    all_assign_users = models.CompanyAssignJob.objects.filter(job_id=interview_schedule_obj.job_id)
    for i in all_assign_users:
        if i.recruiter_type_internal:
            if i.recruiter_id.id != request.user.id:
                notify.send(interview_schedule_obj.candidate_id, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview",
                                                                    description="Your Live interview session is about to start in 15 min",image="/static/notifications/icon/company/Application_Review.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(interview_schedule_obj.candidate_id.id)+"/" + str(
                                                                        interview_schedule_obj.job_id.id))
    print("activaaaaaaaaaate callllllledd")

def deactivate_link(interview_schedule_obj):
    interview_schedule_obj.interview_start_button_status=False
    interview_schedule_obj.save()
    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")


def candidate_negotiate_offer(request,id):
    stage_status = CandidateJobStagesStatus.objects.get(id=id)
    if not stage_status.status == -1:
        if request.method == 'POST':
            if 'accept_offer' in request.POST:
                old_offer = OfferNegotiation.objects.get(id=request.POST.get('negotiation_id'))
                old_offer.action_performed = True
                old_offer.action_name = 'Accepted'
                old_offer.save()

                stage_status = CandidateJobStagesStatus.objects.get(id=id)
                job_offer_obj = JobOffer.objects.get(job_stages_id=stage_status)
                job_offer_obj.is_accepted = True
                job_offer_obj.save()
                stage_status.status = 2
                stage_status.save()
            elif 'reject_offer' in request.POST:
                stage_status = CandidateJobStagesStatus.objects.get(id=id)
                job_offer_obj = JobOffer.objects.get(job_stages_id=stage_status)
                last_negotiation_obj = job_offer_obj.negotiations.filter(action_performed=False)
                if last_negotiation_obj.exists():
                    last_negotiation = last_negotiation_obj[0]
                    last_negotiation.action_performed = True
                    last_negotiation.action_name = 'Rejected By Candidate'
                    last_negotiation.save()
                job_offer_obj.is_accepted = False
                job_offer_obj.rejected_by_candidate = True
                job_offer_obj.save()
                stage_status.status = -1
                stage_status.save()
                return redirect('candidate:applied_job_detail', stage_status.job_id)
            else:
                old_offer = OfferNegotiation.objects.get(id=request.POST.get('negotiation_id'))
                negotiation_obj = OfferNegotiation.objects.create(designation=request.POST.get('designation'),
                                                                         annual_ctc=request.POST.get('negotiate_salary'),
                                                                         notice_period=request.POST.get('notice_period'),
                                                                         joining_date=request.POST.get('join_date'),
                                                                         other_details=request.POST.get('other_details'),
                                                                         from_company=False)
                stage_status = CandidateJobStagesStatus.objects.get(id=id)
                job_offer_obj = JobOffer.objects.get(job_stages_id=stage_status)
                job_offer_obj.negotiations.add(negotiation_obj)

                old_offer.action_performed = True
                old_offer.action_name = 'Negotiated'
                old_offer.save()
                Tracker.objects.update_or_create(job_id=stage_status.job_id,candidate_id=stage_status.candidate_id,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Negotiation By Company/Candidate','update_at':datetime.datetime.now()})
        stage_status = CandidateJobStagesStatus.objects.get(id=id)
        job_offer_obj = JobOffer.objects.get(job_stages_id=stage_status)

        return render(request, 'candidate/ATS/candidate_negotiate_offer.html', {'job_offer_obj':job_offer_obj,'negotiations':job_offer_obj.negotiations.all().order_by('-id')})
    else:
        return HttpResponse(False)


def list_of_agency_company(request):
    if models.candidate_job_apply_detail.objects.filter(candidate_id=request.user).exists():
        context={}
        context['company_list']=InternalCandidateBasicDetails.objects.filter(email=request.user.email,withdraw_by_Candidate=False)
        context['agency_list'] = AgencyModels.InternalCandidateBasicDetail.objects.filter(email=request.user.email,withdraw_by_Candidate=False)
        getcompany_list=InternalCandidateBasicDetails.objects.filter(email=request.user.email,withdraw_by_Candidate=False).values_list('company_id')
        getagency_list=AgencyModels.InternalCandidateBasicDetail.objects.filter(email=request.user.email,withdraw_by_Candidate=False).values_list('agency_id')
        context['chat_internal_company'] = Employee.objects.filter(company_id__in=getcompany_list)
        context['chat_internal_agency'] = AgencyModels.InternalUserProfile.objects.filter(agency_id__in=getagency_list)
        return render(request,'candidate/ATS/listocompany-agency.html',context)
    else:
        return redirect('candidate:basic_detail')

def company_profile(request,id):
    if id:
        profile = CompanyProfile.objects.get(company_id=Company.objects.get(id=id))
        if not profile:
            return redirect('company:add_edit_profile')
        else:
            profile = CompanyProfile.objects.get(company_id=Company.objects.get(id=id))
            get_internalcandidate = InternalCandidateBasicDetails.objects.filter(
                company_id=Company.objects.get(id=id))
            completed_job = JobCreation.objects.filter(
                company_id=Company.objects.get(id=id))
            chat_internal = Employee.objects.filter(company_id=Company.objects.get(id=id))
        return render(request, 'candidate/ATS/company-profile.html', {'get_profile': profile,'completed_job':len(completed_job),'get_internalcandidate':len(get_internalcandidate),'chat_internal':chat_internal})
    else:
        return render(request, 'accounts/404.html')


def custom_round(request,id):
    stage_obj = CandidateJobStagesStatus.objects.get(id=id)
    if stage_obj.status == 1:
        custom_round_obj = CustomTemplate.objects.filter(company_id=stage_obj.company_id,
                                                                template=stage_obj.template)
        if custom_round_obj.exists():
            custom_round_data = custom_round_obj[0]
            if request.method == 'POST':
                description = request.POST.get('description')
                file_by_candidate = request.FILES.get('response_file')
                print('file by cand', file_by_candidate)
                custom_result, created = CustomResult.objects.update_or_create(
                    candidate_id=stage_obj.candidate_id,
                    company_id=stage_obj.company_id, job_id=stage_obj.job_id,
                    custom_template=custom_round_data,
                    defaults={
                       'submitted_file_by_candidate':file_by_candidate, 'description_by_candidate': description,
                    })
                stage_obj.status = 2
                stage_obj.save()
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                notify.send(request.user, recipient=request.user, verb="Manual",
                                        description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                            job_obj.id)+"/company")
                return redirect('candidate:applied_job_detail', stage_obj.job_id.id)
            return render(request, "candidate/ATS/custom_round_exam.html", {'custom_round_data': custom_round_data})
    else:
        return HttpResponse(False)


def withdraw_candidate(request,user_type,id):
    if user_type=='Company':
        if InternalCandidateBasicDetails.objects.filter(candidate_id=request.user,company_id=Company.objects.get(id=id)).exists():
            InternalCandidateBasicDetails.objects.filter(candidate_id=request.user,company_id=Company.objects.get(id=id)).update(withdraw_by_Candidate=True)
    if user_type=='Agency':
        if InternalCandidateBasicDetail.objects.filter(candidate_id=request.user,agency_id=AgencyModels.Agency.objects.get(id=id)).exists():
            InternalCandidateBasicDetail.objects.filter(candidate_id=request.user,agency_id=AgencyModels.Agency.objects.get(id=id)).update(withdraw_by_Candidate=True)
    return redirect('candidate:list_of_agency_company')


def refresh_detect(request,id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('UTF-8'))
        stage_obj = CandidateJobStagesStatus.objects.filter(id=id)
       
        if stage_obj.exists():
            stage = stage_obj[0]
            if not stage.stage.name == 'Prerequisites':
                scheduler_id = str(stage.template.id)+str(stage.job_id.id)+str(stage.candidate_id.id)
                Scheduler.remove_job(scheduler_id)
            stage.reject_by_candidate = True
            stage.status = -1
            stage.save()
        return HttpResponse(True)


def applicant_create_account(request,applicant_id):
    get_applicant=None
    context={}
    if User.objects.filter(id=applicant_id,is_candidate=True,is_active=False).exists():
        get_applicant=User.objects.get(id=applicant_id,is_candidate=True,is_active=False)
        context['fname']=get_applicant.first_name
        context['lname']=get_applicant.last_name
        context['email']=get_applicant.email
        context['applicant_id']=get_applicant.id
    if request.method == 'POST':
        if get_applicant:
            get_applicant.set_password(request.POST.get('password'))
            get_applicant.save()
            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            # print('domain----===========',current_site.domain)
            html_content = render_to_string('accounts/acc_active_email.html', {'user': get_applicant,
                                                                                'name': get_applicant.first_name + ' ' + get_applicant.last_name,
                                                                                'email': get_applicant.email,
                                                                                'domain': current_site.domain,
                                                                                'uid': urlsafe_base64_encode(
                                                                                    force_bytes(get_applicant.pk)),
                                                                                'token': account_activation_token.make_token(
                                                                                    get_applicant), })
            to_email = get_applicant.email
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return activate_account_confirmation(request, get_applicant.first_name + ' ' + get_applicant.last_name, get_applicant.email)

    return render(request,'candidate/ATS/applicant_create_account.html',context)












def agency_mcq_exam(request, id, job_id):
    # 1=right
    # -1=Wrong
    # 0=skip
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
         
    if stage_status.status == 1:
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        mcqtem = AgencyModels.ExamTemplate.objects.get(template=AgencyModels.Template_creation.objects.get(id=id))


        if not mcqtem.exam_type == 'custom':
            questions = AgencyModels.mcq_Question.objects.filter(agency_id=mcqtem.agency_id,mcq_subject=mcqtem.subject.id)
            basic_questions = list(questions.filter(question_level__level_name='basic'))
            intermediate_questions =list( questions.filter(question_level__level_name='intermediate'))
            advanced_questions =list( questions.filter(question_level__level_name='advance'))
            random.shuffle(basic_questions)
            random.shuffle(intermediate_questions)
            random.shuffle(advanced_questions)
            basic_questions = random.sample(basic_questions,int(mcqtem.basic_questions_count))
            intermediate_questions = random.sample(intermediate_questions,int( mcqtem.intermediate_questions_count))
            advanced_questions = random.sample(advanced_questions,int(mcqtem.advanced_questions_count))
            if models.RandomMCQExam.objects.filter(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id).exists():
                delete_question=models.RandomMCQExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                delete_question.question.clear()
                for i in basic_questions:
                    delete_question.question.add(i)
                for i in intermediate_questions:
                    delete_question.question.add(i)
                for i in advanced_questions:
                    delete_question.question.add(i)
            else:
                add_random=models.RandomMCQExam.objects.create(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                for i in basic_questions:
                    add_random.question.add(i)
                for i in intermediate_questions:
                    add_random.question.add(i)
                for i in advanced_questions:
                    add_random.question.add(i)
        # mcqpaper = QuestionPaper.objects.get(exam_template=ExamTemplate.objects.get(template=Template_creation.objects.get(id=id)))
        que = []
        count = 0
        if not mcqtem.question_wise_time:
            time=mcqtem.duration.split(':')
            timer_obj = models.Agency_ExamTimeStatus.objects.filter(candidate_id=request.user, template=mcqtem.template,
                                                             job_id=job_obj)
            if timer_obj.exists():
                timer_obj = timer_obj.get(candidate_id=request.user, template=mcqtem.template, job_id=job_obj)
                start_time = timer_obj.start_time
            else:
                timer_obj = models.Agency_ExamTimeStatus.objects.create(candidate_id=request.user, template=mcqtem.template,
                                                                 job_id=job_obj,
                                                                 start_time=datetime.datetime.now(timezone.utc))
                start_time = datetime.datetime.now(timezone.utc)
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.now(timezone.utc)
                print(start_time)
                duration=datetime.datetime.strptime(str(mcqtem.duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
                schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
                print('end mcq===========================',schedule_end_mcq)
                getjob=Scheduler.get_jobs()
                for job in getjob:
                    if job.id==str(id)+str(job_id)+str(request.user.id):
                        print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                        Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
                Scheduler.add_job(
                                end_mcq,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )                                         

            current_date = datetime.datetime.now(timezone.utc)
            elapsed_time = current_date - start_time

            elapsed_seconds = int(elapsed_time.total_seconds())
            hours = int(elapsed_seconds / 3600) % 24
            minutes = int(elapsed_seconds / 60) % 60
            seconds = int(elapsed_seconds % 60)
            print("remaininsec", elapsed_seconds)
            elapsed_time = pad_time(hours) + ":" + pad_time(minutes) + ":" + pad_time(seconds)
            time = mcqtem.duration.split(':')
            # available_seconds = int(elapsed_seconds)
            available_seconds = ((int(time[0]) * 3600) + (int(time[1])*60))-elapsed_seconds
            if mcqtem.exam_type=='random':
                get_question=models.RandomMCQExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                for l in get_question.question.all():
                    # get_time = ExamQuestionUnit.objects.get(question=mcq_Question.objects.get(id=int(l.id)))
                    que.append({'dbid': l.id, 'id': count + 1,
                                'choice_no': ['a', 'b', 'c', 'd'],
                                'question': l.question_description,
                                'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                })
                    count += 1
            else:
                if mcqtem.marking_system=='question_wise':
                    get_times = AgencyModels.ExamQuestionUnit.objects.filter(template_id=AgencyModels.Template_creation.objects.get(id=id))
                    for get_time in get_times:
                        que.append({'dbid': get_time.question.id, 'id': count + 1,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'question': get_time.question.question_description,
                                    'choices': [get_time.question.option_a, get_time.question.option_b, get_time.question.option_c, get_time.question.option_d]
                                    })
                        count += 1
                else:
                    print('question_wise====================question_wise',mcqtem)
                    for l in mcqtem.basic_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
                    for l in mcqtem.intermediate_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
                    for l in mcqtem.advanced_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
            count = 0
            print(que)
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/agency/candidate_mcq_exam.html', {'time':available_seconds,'elapsed_time':elapsed_time,'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
        elif mcqtem.question_wise_time:
            get_times = AgencyModels.ExamQuestionUnit.objects.filter(template_id=AgencyModels.Template_creation.objects.get(id=id))
            total_time=0
            for get_time in get_times:
                print(get_time.question_time)
                time = get_time.question_time.split(':')
                available_seconds = int(time[0]) * 60 + int(time[1])
                total_time += available_seconds
                que.append({'dbid': get_time.question.id, 'id': count + 1,
                            'time': available_seconds,
                            'choice_no': ['a', 'b', 'c', 'd'],
                            'question': get_time.question.question_description,
                            'choices': [get_time.question.option_a, get_time.question.option_b, get_time.question.option_c, get_time.question.option_d]
                            })
                count += 1
            count = 0
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            Scheduler.add_job(
                            agency_end_mcq,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )    
            getStoreData = json.dumps(que)
            print(total_time)
            return render(request, 'candidate/ATS/agency/candidate_mcq_exam_if_question.html',
                          {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def agency_mcq_exam_fill(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        mcqtem = AgencyModels.ExamTemplate.objects.get(template=template_obj)
        # models.ExamTimeStatus.objects.update_or_create(candidate_id=request.user, template=mcqtem.template,
        #                                      job_id=job_obj,defaults={
        #                                      'start_time':datetime.datetime.now(timezone.utc)})
        print("=========================", mcq_data)
        mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        que = AgencyModels.mcq_Question.objects.get(id=int(mca_que_id))
        cat_mark=0
        if mcqtem.marking_system == 'question_wise':
            get_marks = AgencyModels.ExamQuestionUnit.objects.get(question=AgencyModels.mcq_Question.objects.get(id=int(mca_que_id)),
                                                     template=template_obj)
            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                if mcq_ans == que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = get_marks.question_mark
                    else:
                        getmarks = get_marks.question_mark
                    check_ans = 1
                elif mcq_ans != que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = (get_marks.question_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        elif mcqtem.marking_system == 'category_wise':
            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                get_que_type = AgencyModels.mcq_Question.objects.get(id=int(mca_que_id))
                if get_que_type.question_level.level_name == 'basic':
                    cat_mark = int(mcqtem.basic_question_marks)
                elif get_que_type.question_level.level_name == 'intermediate':
                    cat_mark = int(mcqtem.intermediate_question_marks)
                elif get_que_type.question_level.level_name == 'advance':
                    cat_mark = int(mcqtem.advanced_question_marks)
                print(mcq_ans,"=======================",que.correct_option)
                if mcq_ans == que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = cat_mark
                    else:
                        getmarks = cat_mark
                    check_ans = 1
                elif mcq_ans != que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = (cat_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        models.Agency_Mcq_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 agency_id=job_obj.agency_id,
                                                 question=AgencyModels.mcq_Question.objects.get(id=que.id),
                                                 job_id=job_obj,
                                                 template=template_obj, defaults={
                'marks': getmarks,
                'status': check_ans,
                'time': mca_que_time}
                                                 )
        if mcq_data['last']:
            data['url']=str(current_site.domain+'/candidate/agency_mcq_result/'+str(id)+'/'+str(job_id))
            data['last']=True
        else:
            print("==================================================")
            data['last'] = False
        data["status"]= True
    else:
        data["status"]= False
    return JsonResponse(data)


def agency_mcq_result(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    get_result = models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)
    get_time=models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj).last()
    mcqtem = AgencyModels.ExamTemplate.objects.get(agency_id=job_obj.agency_id,template=template_obj)
    # total_time = datetime.datetime.strptime(mcqtem.duration+':00', '%H:%M:%S')
    # last_time = datetime.datetime.strptime(get_time.time, '%H:%M:%S')
    obain_time = 10
    obain_marks = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            # obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.question_description + """</div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/MCQ/".format(request.user.id, job_obj.id)
    getresult,created = models.Agency_Mcq_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'mcq_pdf':path +request.user.first_name+ "mcq.pdf"})
    # pdfkit.from_string(a, output_path=path +request.user.first_name+ "mcq.pdf", configuration=config)



    # move to next stage process

    # onthego change
    job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_stage = ''
    currentcompleted=False
    next_stage = None
    action_required=''
    reject=False
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if job_workflow.withworkflow:
        main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = AgencyModels.WorkflowStages.objects.get(workflow=main_workflow,template=template_obj)
        config_obj = AgencyModels.WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)
        current_stage=stage_status.stage
        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                currentcompleted=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
                
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                reject=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                action_required='Company'
                stage_status.save()
            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            action_required='Company'
            stage_status.save()

        if not reject:
            new_sequence_no = stage_status.sequence_number + 1
            if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                        sequence_number=new_sequence_no).exists():
                new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                next_stage=new_stage_status.stage
    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    
    if not next_stage==None and action_required=='':
        if next_stage.name=='Interview' :
            action_required='Company/Agency'
        else:
            action_required='Candidate'
    if current_stage!='':
        if current_stage.name=='Job Offer':
            action_required='Offer Letter Generation By Company'
        # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
        #                                                             'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
        #                                                             'action_required':action_required,'update_at':datetime.datetime.now()})
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/agency/end_exam.html',{'get_result': getresult, "job_id": job_obj.id})

def agency_start_mcq(template_id, job_id):
    print("activaaaaaaaaaate callllllledd")

def agency_end_mcq(template_id, job_id,loginuser_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    get_result = models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)
    get_time=models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj).last()
    mcqtem = AgencyModels.ExamTemplate.objects.get(agency_id=job_obj.agency_id,template=template_obj)
    # total_time = datetime.datetime.strptime(mcqtem.duration+':00', '%H:%M:%S')
    # last_time = datetime.datetime.strptime(get_time.time, '%H:%M:%S')
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    obain_time = 10
    obain_marks = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            # obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.question_description + """</div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/MCQ/".format(loginuser_id, job_obj.id)
    getresult,created = models.Agency_Mcq_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'mcq_pdf':path +user_obj.first_name+ "mcq.pdf"})
    pdfkit.from_string(a, output_path=path +user_obj.first_name+ "mcq.pdf", configuration=config)



    # move to next stage process

    # onthego change
    job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_stage = ''
    currentcompleted=False
    next_stage = None
    action_required=''
    reject=False
    if job_workflow.withworkflow:
        main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = AgencyModels.WorkflowStages.objects.get(workflow=main_workflow,template=template_obj)
        config_obj = AgencyModels.WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)
        current_stage=stage_status.stage
        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                currentcompleted=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                reject=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                action_required='Company'
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            action_required='Company'
            stage_status.save()
            
        if not reject:
            new_sequence_no = stage_status.sequence_number + 1
            if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                        sequence_number=new_sequence_no).exists():
                new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                next_stage=new_stage_status.stage
    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    
    if not next_stage==None and action_required=='':
        if next_stage.name=='Interview' :
            action_required='Company/Agency'
        else:
            action_required='Candidate'
    if current_stage!='':
        if current_stage.name=='Job Offer':
            action_required='Offer Letter Generation By Company'
        # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
        #                                                             'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
        #                                                             'action_required':action_required,'update_at':datetime.datetime.now()})
    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")

# Image exam


def image_exam(request, id, job_id):
    # 1=right
    # -1=Wrong
    # 0=skip
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    if stage_status.status == 1:
        job_obj = JobCreation.objects.get(id=job_id)
        mcqtem = ImageExamTemplate.objects.get(template=Template_creation.objects.get(id=id))
        if not mcqtem.exam_type == 'custom':
            questions = ImageQuestion.objects.filter(company_id=User.objects.get(id=mcqtem.company_id.id),subject=mcqtem.subject.id)
            basic_questions = list(questions.filter(question_level__level_name='basic'))
            intermediate_questions =list( questions.filter(question_level__level_name='intermediate'))
            advanced_questions =list( questions.filter(question_level__level_name='advance'))
            random.shuffle(basic_questions)
            random.shuffle(intermediate_questions)
            random.shuffle(advanced_questions)
            basic_questions = random.sample(basic_questions,int(mcqtem.basic_questions_count))
            intermediate_questions = random.sample(intermediate_questions,int( mcqtem.intermediate_questions_count))
            advanced_questions = random.sample(advanced_questions,int(mcqtem.advanced_questions_count))
            if models.RandomImageExam.objects.filter(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id)).exists():
                delete_question=models.RandomImageExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                delete_question.question.clear()
                for i in basic_questions:
                    delete_question.question.add(i)
                for i in intermediate_questions:
                    delete_question.question.add(i)
                for i in advanced_questions:
                    delete_question.question.add(i)
            else:
                add_random=models.RandomImageExam.objects.create(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=Company.objects.get(id=job_obj.company_id.id))
                for i in basic_questions:
                    add_random.question.add(i)
                for i in intermediate_questions:
                    add_random.question.add(i)
                for i in advanced_questions:
                    add_random.question.add(i)
        # imagepaper = ImageQuestionPaper.objects.get(exam_template=mcqtem)
        que = []
        count = 0
        if not mcqtem.question_wise_time:
            time=mcqtem.duration.split(':')
            timer_obj = models.ExamTimeStatus.objects.filter(candidate_id=request.user, template=mcqtem.template,
                                                             job_id=job_obj)
            if timer_obj.exists():
                timer_obj = timer_obj.get(candidate_id=request.user, template=mcqtem.template, job_id=job_obj)
                start_time = timer_obj.start_time
            else:
                # timer_obj = models.ExamTimeStatus.objects.create(candidate_id=request.user, template=mcqtem.template,
                #                                                  job_id=job_obj,
                #                                                  start_time=datetime.datetime.now(timezone.utc))
                # start_time = datetime.datetime.now(timezone.utc)
                start_time = datetime.datetime.now(timezone.utc)
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.now(timezone.utc)
                print(start_time)
                duration=datetime.datetime.strptime(str(mcqtem.duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
                schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
                print('end image===========================',schedule_end_mcq)
                getjob=Scheduler.get_jobs()
                for job in getjob:
                    if job.id==str(id)+str(job_id)+str(request.user.id):
                        Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
                Scheduler.add_job(
                                end_image,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )             
            current_date = datetime.datetime.now(timezone.utc)
            print(current_date)
            print(start_time)
            elapsed_time = current_date - start_time

            elapsed_seconds = int(elapsed_time.total_seconds())
            hours = int(elapsed_seconds / 3600) % 24
            minutes = int(elapsed_seconds / 60) % 60
            seconds = int(elapsed_seconds % 60)
            print("remaininsec", elapsed_seconds)
            elapsed_time = pad_time(hours) + ":" + pad_time(minutes) + ":" + pad_time(seconds)
            time = mcqtem.duration.split(':')
            # available_seconds = int(elapsed_seconds)
            available_seconds = ((int(time[0]) * 3600) + (int(time[1])*60)) - elapsed_seconds
            if mcqtem.exam_type == 'random':
                get_question = models.RandomImageExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,company_id=User.objects.get(id=job_obj.company_id.id))
                for l in get_question.question.all():
                    imageoption = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                    # options = [imageoption.file1.url if imageoption.file1 else None]
                    que.append({'dbid': l.id, 'id': count + 1,
                                'question': l.image_que_description,
                                'q_image':l.question_file.url,
                                'choice_no': ['a', 'b', 'c', 'd'],
                                'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                })
                    print(que)
                    count += 1
            else:
                print("=====================================")
                if mcqtem.marking_system=='question_wise':
                    get_times = ImageExamQuestionUnit.objects.filter(template_id=Template_creation.objects.get(id=id))
                    for get_time in get_times:
                        print("======================================s")
                        imageoption = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=get_time.question.id))
                        que.append({'dbid': get_time.question.id, 'id': count + 1,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'question': get_time.question.image_que_description,
                                    'q_image':get_time.question.question_file.url,
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                else:
                    for l in mcqtem.basic_questions.all():
                        print(l.id)
                        imageoption=ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                    for l in mcqtem.intermediate_questions.all():
                        print(l.id)
                        imageoption=ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage': [imageoption.file1.url if imageoption.file1 else None,
                                                    imageoption.file2.url if imageoption.file2 else None,
                                                    imageoption.file3.url if imageoption.file3 else None,
                                                    imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                    for l in mcqtem.advanced_questions.all():
                        print(l.id)
                        imageoption=ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None for imageoptions in imageoption]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
            count = 0
            print("\n\nque",que)
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/candidate_image_exam.html', {'time':available_seconds,'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
        elif mcqtem.question_wise_time:
            get_times = ImageExamQuestionUnit.objects.filter(template_id=Template_creation.objects.get(id=id))
            total_time=0
            for get_time in get_times:
                print("======================================s")
                time = get_time.question_time.split(':')
                available_seconds = int(time[0]) * 60 + int(time[1])
                imageoption = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=get_time.question.id))
                total_time += available_seconds
                que.append({'dbid': get_time.question.id, 'id': count + 1,
                            'time': available_seconds,
                            'choice_no': ['a', 'b', 'c', 'd'],
                            'question': get_time.question.image_que_description,
                            'q_image':get_time.question.question_file.url,
                            'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                            'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                            })
                count += 1
            count = 0
            print(total_time)
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end image===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            
            Scheduler.add_job(
                            end_image,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )    
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/candidate_image_exam_if_question.html',
                          {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def image_exam_fill(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        print(mcq_data)
        mcqtem = ImageExamTemplate.objects.get(template=template_obj)
        print("=========================", mcq_data)
        mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        image_path=mcq_data['image_path']
        print('\n\nimage_path', image_path)
        s2 = "media/"
        # image_path=image_path[image_path.index(s2) + len(s2):]
        que = ImageQuestion.objects.get(id=int(mca_que_id))
        que_ans = ImageOption.objects.get(question_id=ImageQuestion.objects.get(id=int(mca_que_id)))
        cat_mark=0

        if mcqtem.marking_system == 'question_wise':
            get_marks = ImageExamQuestionUnit.objects.get(question=ImageQuestion.objects.get(id=int(mca_que_id)),
                                                          template=template_obj)

            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                if mcq_ans == que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = get_marks.question_mark
                    else:
                        getmarks = get_marks.question_mark
                    check_ans = 1
                elif mcq_ans != que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = (get_marks.question_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        elif mcqtem.marking_system == 'category_wise':

            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                get_que_type = ImageQuestion.objects.get(id=int(mca_que_id))
                if get_que_type.question_level.level_name == 'basic':
                    cat_mark = int(mcqtem.basic_question_marks)
                elif get_que_type.question_level.level_name == 'intermediate':
                    cat_mark = int(mcqtem.intermediate_question_marks)
                elif get_que_type.question_level.level_name == 'advance':
                    cat_mark = int(mcqtem.advanced_question_marks)
                if mcq_ans == que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = cat_mark
                    else:
                        getmarks = cat_mark
                    check_ans = 1
                elif mcq_ans != que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = (cat_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        models.Image_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 company_id=Company.objects.get(id=job_obj.company_id.id),
                                                 question=ImageQuestion.objects.get(id=que.id),
                                                 job_id=JobCreation.objects.get(id=job_id),
                                                 template=template_obj, defaults={
                'ansfile' : image_path,
                'marks': getmarks,
                'status': check_ans,
                'time': mca_que_time}
                                                 )
        if mcq_data['last'] == True:
            data['url']=str(current_site.domain+'/candidate/image_result/'+str(id)+'/'+str(job_id))
            data['last']=True


        else:
            print("==================================================")
            data['last'] = False
        data["status"]= True
    else:
        data["status"]= False
    return JsonResponse(data)


def image_result(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    get_result = models.Image_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)
    mcqtem = ImageExamTemplate.objects.get(company_id=job_obj.company_id, template=template_obj)
    obain_marks = 0
    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.image_que_description + """<img height="300px" width="300px" src=\""""+ image_as_base64(settings.MEDIA_ROOT[0:-7:] +i.question.question_file.url) +"""\"></div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/Image/".format(request.user.id, job_obj.id)
    getresult,created = models.Image_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'image_pdf':path +request.user.first_name+ "image.pdf"})

    # pdfkit.from_string(a, output_path=path+request.user.first_name + "image.pdf")

    job_workflow = JobWorkflow.objects.get(job_id=job_obj)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    if job_workflow.withworkflow:
        main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = WorkflowStages.objects.get(workflow=main_workflow, template=template_obj)
        config_obj = WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)

        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=''
                next_stage=None
                action_required=''
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    current = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    current_stage=current.stage
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no+1).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no+1)
                    next_stage=new_stage_status.stage
                    print(next_stage)
                if not next_stage==None:
                    if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                    else:
                        action_required='Perform By Candidate'
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'current_stage':current_stage,'next_stage':next_stage,
                                                                'action_required':action_required,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'reject':True,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'On Hold by Company','update_at':datetime.datetime.now()})
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            stage_status.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            notify.send(request.user, recipient=request.user, verb="Manual",
                                    description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/company")

    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    
    return render(request, 'candidate/ATS/end_exam.html',{'get_result':getresult,'job_id':job_id})


def end_image(template_id, job_id,loginuser_id):
    job_obj = JobCreation.objects.get(id=job_id)
    template_obj = Template_creation.objects.get(id=template_id)
    user_obj = User.objects.get(id=loginuser_id)
    get_result = models.Image_Exam.objects.filter(candidate_id=user_obj,
                                                company_id=Company.objects.get(id=job_obj.company_id.id),
                                                job_id=job_obj,
                                                template=template_obj)
    mcqtem = ImageExamTemplate.objects.get(company_id=job_obj.company_id, template=template_obj)
    obain_marks = 0
    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.image_que_description + """<img height="300px" width="300px" src=\""""+ image_as_base64(settings.MEDIA_ROOT[0:-7:] +i.question.question_file.url) +"""\"></div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/Image/".format(loginuser_id, job_obj.id)
    getresult,created = models.Image_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          company_id=Company.objects.get(id=job_obj.company_id.id),
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'image_pdf':path +user_obj.first_name+ "image.pdf"})

    pdfkit.from_string(a, output_path=path+user_obj.first_name + "image.pdf")

    job_workflow = JobWorkflow.objects.get(job_id=job_obj)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if job_workflow.withworkflow:
        main_workflow = Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = WorkflowStages.objects.get(workflow=main_workflow, template=template_obj)
        config_obj = WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)

        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=''
                next_stage=None
                action_required=''
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    current = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    current_stage=current.stage
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no+1).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no+1)
                    next_stage=new_stage_status.stage
                if not next_stage==None:
                    if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                    else:
                        action_required='Perform By Candidate'
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'current_stage':current_stage,'next_stage':next_stage,
                                                                'action_required':action_required,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'reject':True,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'On Hold by Company','update_at':datetime.datetime.now()})
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            stage_status.save()

    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()

    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")

# audio

def pad_time(number):
    if number<10:
        return "0"+str(number)
    else:
        return str(number)


def audio_exam(request, id, job_id):
    template_obj = Template_creation.objects.get(id=id)
    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    if stage_status.status == 1:
        job_obj = JobCreation.objects.get(id=job_id)
        mcqtem = AudioExamTemplate.objects.get(template=Template_creation.objects.get(id=id))
        mcqpaper = AudioQuestionPaper.objects.get(exam_template=mcqtem)
        timer_obj = models.ExamTimeStatus.objects.filter(candidate_id=request.user,template = mcqtem.template,job_id=job_obj)
        if timer_obj.exists():
            timer_obj = timer_obj.get(candidate_id=request.user,template = mcqtem.template,job_id=job_obj)
            start_time = timer_obj.start_time
        else:
            timer_obj = models.ExamTimeStatus.objects.create(candidate_id=request.user,template=mcqtem.template,job_id=job_obj,start_time=datetime.datetime.now(timezone.utc))
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            print(start_time)
            duration=datetime.datetime.strptime(str(mcqtem.total_exam_time), '%H:%M:%S').time()
            A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
            totalsecond = A.total_seconds()
            schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            Scheduler.add_job(
                            end_audio,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )                           
        current_date = datetime.datetime.now(timezone.utc)

        elapsed_time = current_date-start_time

        elapsed_seconds = int(elapsed_time.total_seconds())
        hours = int(elapsed_seconds / 3600 ) % 24
        minutes = int(elapsed_seconds / 60 ) % 60
        seconds = int(elapsed_seconds % 60)
        print("remaininsec",elapsed_seconds)
        elapsed_time = pad_time(hours)+":"+pad_time( minutes)+":" + pad_time(seconds)
        # time = mcqtem.total_exam_time.split(':')
        # # available_seconds = int(elapsed_seconds)
        # elapsed_time = (int(time[0]) * 60) + (int(time[1]))
        print("==========================================",elapsed_time)
        que = []
        count = 0
        print(mcqtem.audioquestions.all())
        for l in mcqtem.audioquestions.all():
            get_time = AudioExamQuestionUnit.objects.get(question=Audio.objects.get(id=int(l.id)),template=Template_creation.objects.get(id=id))
            que.append({'dbid': l.id, 'id': count + 1,
                        'time': get_time.question_time,
                        'question': l.paragraph_description
                        })
            count += 1
        count = 0
        getStoreData = json.dumps(que)
        return render(request, 'candidate/ATS/candidate_audio_video_exam_if_question.html',
                      {'getStoreData': getStoreData,'stage_id':stage_status.id, 'job_obj': job_obj, 'temp_id': mcqpaper.exam_template.template.id,"elapsed_time":elapsed_time,'total_exam_time':mcqtem.total_exam_time,"is_video":mcqtem.is_video})

    else:
        return HttpResponse(False)

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile


def audio_exam_fill(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    data = {}
    template_creation_obj = Template_creation.objects.get(id=id)
    audio_exam_template = AudioExamTemplate.objects.get(template=template_creation_obj)
    audio_question_paper = AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    current_site = get_current_site(request)
    if request.method == 'POST':
        attempt,updated = models.AudioExamAttempt.objects.update_or_create(candidate_id=request.user,company_id=audio_question_paper.company_id,audio_question_paper = audio_question_paper,job_id = job_obj)
        attempt.audio_question_attempts.remove()
        # all_blobs = request.POST.get("blobs")
        all_questions = request.POST.get("questions")
        all_questions = all_questions.split(",")
        for i in all_questions:
            audio_question = audio_question_paper.exam_question_units.get(question=Audio.objects.get(id=int(i)))
            answer = request.FILES.get(str(i) + "blob")

            if audio_question_paper.exam_template.is_video:
                file_extension = ".mkv"
            else:
                file_extension = ".wav"
            question_attempt = models.AudioExamQuestionAttemptUnit.objects.create(audio_question=audio_question)
            file_name_tag= str(question_attempt.id)+file_extension
            fs = FileSystemStorage() #defaults to   MEDIA_ROOT
            if answer == None:
                filename = None
            else:
                filename = fs.save("audio_exam_recordings/"+str(question_attempt.id)+file_extension, answer)
                file_url = fs.url(filename)

            question_attempt.answer.name = filename
            question_attempt.save()

            attempt.audio_question_attempts.add(question_attempt)
        attempt.save()
        data["status"] = True
    # else:
    #     data["status"] = False
    return JsonResponse(data)


def audio_result(request, id, job_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = Template_creation.objects.get(id=id)
    audio_exam_template = AudioExamTemplate.objects.get(template=template_obj)
    audio_question_paper = AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    current_site = get_current_site(request)
    attempt = models.AudioExamAttempt.objects.get(candidate_id=request.user,
                                                         company_id=audio_question_paper.company_id,
                                                         audio_question_paper=audio_question_paper, job_id=job_obj)
    print("==========================",attempt.audio_question_attempts.all())
    get_result = {'total_question':len(attempt.audio_question_attempts.all())}
    ans_count=0
    noans_count=0
    for result in attempt.audio_question_attempts.all():
        if result.answer:
            ans_count+=1
        else:
            noans_count+=1
    get_result['answered']=ans_count
    get_result['not_answered']=noans_count
    obain_time = 0
    total_que = 0
    ans_que = 0
    no_ans_que = 0
    for i in attempt.audio_question_attempts.all():
        if i.answer != '':
            ans_que += 1
        else :
            no_ans_que += 1
        total_que += 1

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    notify.send(request.user, recipient=request.user, verb="Manual",
                            description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/audio_end_exam.html', {'get_result': 'getresult','job_id':job_id})

def end_audio(template_id, job_id,loginuser_id):
    job_obj = JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = Template_creation.objects.get(id=template_id)
    audio_exam_template = AudioExamTemplate.objects.get(template=template_obj)
    audio_question_paper = AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    attempt = models.AudioExamAttempt.objects.get(candidate_id=user_obj,
                                                         company_id=audio_question_paper.company_id,
                                                         audio_question_paper=audio_question_paper, job_id=job_obj)
    print("==========================",attempt.audio_question_attempts.all())
    get_result = {'total_question':len(attempt.audio_question_attempts.all())}
    ans_count=0
    noans_count=0
    for result in attempt.audio_question_attempts.all():
        if result.answer:
            ans_count+=1
        else:
            noans_count+=1
    get_result['answered']=ans_count
    get_result['not_answered']=noans_count
    obain_time = 0
    total_que = 0
    ans_que = 0
    no_ans_que = 0
    for i in attempt.audio_question_attempts.all():
        if i.answer != '':
            ans_que += 1
        else :
            no_ans_que += 1
        total_que += 1

    stage_status = CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Assessment by Company','update_at':datetime.datetime.now()})

def create_interview_link():
    link = get_random_string(length=20)
    if InterviewSchedule.objects.filter(interview_link=link).exists():
        return create_interview_link()
    else:
        return link


def applied_job_detail(request, id,company_type):
    if models.candidate_job_apply_detail.objects.filter(candidate_id=request.user).exists():
        if company_type=='company':
            current_stage=None
            job_obj = JobCreation.objects.get(id=id)
            workflow = JobWorkflow.objects.get(job_id=job_obj)
            candidate_obj = User.objects.get(id=request.user.id)
            workflow_stages = WorkflowStages.objects.filter(workflow=workflow.workflow_id,display=True).order_by('sequence_number')
            stages_status = CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                                        candidate_id=candidate_obj,
                                                                        job_id=job_obj).order_by('sequence_number')

            if request.method == 'POST':
                
                if 'reschedule_interview' in request.POST:
                    interview_schedule_id = request.POST.get('interview_schedule_data')
                    interview_schedule_obj = InterviewSchedule.objects.get(id=interview_schedule_id)
                    date_time = '<ul>'
                    for (date,time) in zip_longest(request.POST.getlist('interview_date'),request.POST.getlist('interview_time'),fillvalue=None):
                        date_time += """<li><b>""" + str(date) + ' ' + str(time) + """</b></li>"""
                    date_time += '</ul>'
                    date_time += """<p>""" + request.POST.get('reschedule_instruction') + """</p>"""
                    interview_schedule_obj.reschedule_message = date_time
                    interview_schedule_obj.is_accepted = False
                    interview_schedule_obj.status = 0
                    interview_schedule_obj.save()
                    all_assign_users = CompanyAssignJob.objects.filter(job_id=job_obj)
                    if not current_stage==None:
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Reschedule",
                                                                                        description="Candidate requested for reschedule, please provide new timing.",image="/static/notifications/icon/company/Application_Review.png",
                                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                            job_obj.id))
                    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
                                                                        'action_required':'Reschedule interview by Company','update_at':datetime.datetime.now()})
                elif 'withdraw_candidate' in request.POST:
                    CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                    job_id=job_obj,
                                                                    company_id=job_obj.company_id,
                                                                    defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
                    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=job_obj.company_id,defaults={
                                                                        'withdraw':True,'update_at':datetime.datetime.now()})
                    current_site = get_current_site(request)
                    header=request.is_secure() and "https" or "http"
                    notify.send(request.user, recipient=request.user, verb="Withdraw",
                                    description="You have withdrawn your application from Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/company")
                else:
                    interview_schedule_id = request.POST.get('interview_schedule_data')
                    interview_schedule_obj = InterviewSchedule.objects.get(id=interview_schedule_id)
                    link = create_interview_link()
                    interview_schedule_obj.is_accepted = True
                    interview_schedule_obj.interview_link = link
                    interview_schedule_obj.save()
                    # Date Trigger
                    Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
                                                                        'action_required':'By Both','update_at':datetime.datetime.now()})
                    time_zone = pytz.timezone("Asia/Calcutta")
                    schedule_date=datetime.datetime.combine(datetime.datetime.strptime(str(interview_schedule_obj.date),'%Y-%m-%d').date(),datetime.datetime.strptime(str(interview_schedule_obj.time), '%H:%M:%S').time())
                    schedule_activelink = schedule_date - datetime.timedelta(minutes=15)
                    schedule_activelink = time_zone.localize(schedule_activelink)
                    schedule_activelink = schedule_activelink.astimezone(pytz.utc)
                    print(schedule_activelink)
                    print("sdasdsadsa",datetime.datetime.now())
                    all_assign_users = CompanyAssignJob.objects.filter(job_id=job_obj)
                    if not current_stage==None:
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Confirmed",
                                                                                        description="Candidate confirmed the InterView time.",image="/static/notifications/icon/company/Application_Review.png",
                                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                            job_obj.id))
                    Scheduler.add_job(
                                    activate_link,
                                    trigger=DateTrigger(run_date=schedule_activelink),
                                    args = [interview_schedule_obj],
                                    misfire_grace_time=6000
                                    # replace_existing=True
                                )
                    duration=datetime.datetime.strptime(str(interview_schedule_obj.interview_duration), '%H:%M').time()
                    A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                    totalsecond = A.total_seconds()
                    schedule_deactivelink = schedule_date + datetime.timedelta(seconds=totalsecond)
                    schedule_deactivelink = time_zone.localize(schedule_deactivelink)
                    schedule_deactivelink = schedule_deactivelink.astimezone(pytz.utc)
                    print(schedule_deactivelink)
                    Scheduler.add_job(
                                    deactivate_link,
                                    trigger=DateTrigger(run_date=schedule_deactivelink),
                                    args = [interview_schedule_obj],
                                    misfire_grace_time=6000
                                    # replace_existing=True
                                )
                    
            interview_schedule_data = None
            job_offer_data = None
            custom_round_data = None
            stages_data = []
            for stage in stages_status:
                stage_dict = {'stage': stage, 'result': ''}
                if stage.stage.name == 'Custom':
                    custom_template = CustomTemplate.objects.filter(company_id=stage.company_id,template=stage.template)
                    if custom_template.exists():
                        custom_template = custom_template[0]
                        custom_round_data = CustomResult.objects.filter(candidate_id=stage.candidate_id,company_id=stage.company_id,
                                                    job_id=stage.job_id,custom_template=custom_template)
                        custom_round_data = custom_round_data.first() if custom_round_data.exists() else None
                if stage.stage.name == 'Interview':

                    interview_schedule_obj = InterviewSchedule.objects.filter(candidate_id=candidate_obj,
                                                                                    job_id=job_obj,
                                                            company_id=stage.company_id,
                                                            template=stage.template,
                                                            job_stages_id=stage)
                    print('\n\nin Interview',interview_schedule_obj)
                    if interview_schedule_obj.exists():
                        interview_schedule_data = interview_schedule_obj[0]

                if stage.stage.name == 'Job Offer':
                    print('\n\nin Job Offer')
                    job_offer_obj = JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
                                                                                    company_id=stage.company_id,
                                                                                    job_stages_id=stage)
                    if job_offer_obj.exists():
                        job_offer_data = job_offer_obj[0]

                if stage.status == 2 or stage.status == -1 or stage.status == 3:
                    if stage.stage.name == 'JCR':
                        jcr_result = models.JcrRatio.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        stage_dict['result'] = jcr_result

                    if stage.stage.name == 'Prerequisites':
                        prerequisites_result = models.PreRequisitesFill.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        stage_dict['result'] = prerequisites_result

                    if stage.stage.name == 'MCQ Test':
                        if not stage.reject_by_candidate:
                            mcq_test_result = models.Mcq_Exam_result.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                        template=stage.template)
                            print('\n\n \nmcq_test_result', mcq_test_result)
                            stage_dict['result'] = mcq_test_result
                        else:
                            stage_dict['result'] = None

                    if stage.stage.name == 'Descriptive Test':
                        if not stage.reject_by_candidate:
                            descriptive_result = models.Descriptive_Exam_result.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                        template=stage.template)
                            stage_dict['result'] = descriptive_result
                        else:
                            stage_dict['result'] = None


                    if stage.stage.name == 'Image Test':
                        if not stage.reject_by_candidate:
                            image_result = models.Image_Exam_result.objects.get(company_id=stage.company_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                        template=stage.template)
                            stage_dict['result'] = image_result
                        else:
                            stage_dict['result'] = None

                stages_data.append(stage_dict)

            print('stages_data>>>>>>>>>>>>>>>>>', stages_data)
            chat_internal =CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,company_id=job_obj.company_id)

            candidate_job_status = None
            if CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
                candidate_job_status = CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)

            candidate_apply_details = None
            if AppliedCandidate.objects.filter(candidate=candidate_obj,company_id=job_obj.company_id).exists():
                candidate_apply_details = AppliedCandidate.objects.get(candidate_id=candidate_obj, job_id=job_obj)
            return render(request, 'candidate/ATS/applied-candidates-details.html',
                    {'workflow_stages': workflow_stages, 'job_obj': job_obj,'stages_status':stages_status,'candidate_apply_details':candidate_apply_details,
                    'stages_data':stages_data,'interview_schedule_data':interview_schedule_data,
                    'job_offer_data':job_offer_data,'chat_internal':chat_internal,'custom_round_data':custom_round_data,
                    'candidate_job_status':candidate_job_status})
        if company_type=='agency':
            job_obj = AgencyModels.JobCreation.objects.get(id=id)
            current_stage=None
            workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
            candidate_obj = User.objects.get(id=request.user.id)
            workflow_stages = AgencyModels.WorkflowStages.objects.filter(workflow=workflow.workflow_id,display=True).order_by('sequence_number')
            stages_status = AgencyModels.CandidateJobStagesStatus.objects.filter(agency_id=job_obj.agency_id,
                                                                        candidate_id=candidate_obj,
                                                                        job_id=job_obj).order_by('sequence_number')

            if request.method == 'POST':
                
                if 'reschedule_interview' in request.POST:
                    interview_schedule_id = request.POST.get('interview_schedule_data')
                    interview_schedule_obj = AgencyModels.InterviewSchedule.objects.get(id=int(interview_schedule_id))
                    date_time = '<ul>'
                    for (date,time) in zip_longest(request.POST.getlist('interview_date'),request.POST.getlist('interview_time'),fillvalue=None):
                        date_time += """<li><b>""" + str(date) + ' ' + str(time) + """</b></li>"""
                    date_time += '</ul>'
                    date_time += """<p>""" + request.POST.get('reschedule_instruction') + """</p>"""
                    interview_schedule_obj.reschedule_message = date_time
                    interview_schedule_obj.is_accepted = False
                    interview_schedule_obj.status = 0
                    interview_schedule_obj.save()
                    all_assign_users = AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj)
                    if not current_stage==None:
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Reschedule",
                                                                                        description="Candidate requested for reschedule, please provide new timing.",image="/static/notifications/icon/company/Application_Review.png",
                                                                                        target_url=header+"://"+current_site.domain+"/agency/agency_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                            job_obj.id))
                    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
                    #                                                     'action_required':'Reschedule interview by Company','update_at':datetime.datetime.now()})
                elif 'withdraw_candidate' in request.POST:
                    AgencyModels.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                    job_id=job_obj,
                                                                    agency_id=job_obj.agency_id,
                                                                    defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
                    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=job_obj.company_id,defaults={
                    #                                                     'withdraw':True,'update_at':datetime.datetime.now()})
                    current_site = get_current_site(request)
                    header=request.is_secure() and "https" or "http"
                    notify.send(request.user, recipient=request.user, verb="Withdraw",
                                    description="You have withdrawn your application from Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/agency")
                else:
                    interview_schedule_id = request.POST.get('interview_schedule_data')
                    interview_schedule_obj = AgencyModels.InterviewSchedule.objects.get(id=interview_schedule_id)
                    link = create_interview_link()
                    interview_schedule_obj.is_accepted = True
                    interview_schedule_obj.interview_link = link
                    interview_schedule_obj.save()
                    # Date Trigger
                    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=interview_schedule_obj.company_id,defaults={
                    #                                                     'action_required':'By Both','update_at':datetime.datetime.now()})
                    time_zone = pytz.timezone("Asia/Calcutta")
                    schedule_date=datetime.datetime.combine(datetime.datetime.strptime(str(interview_schedule_obj.date),'%Y-%m-%d').date(),datetime.datetime.strptime(str(interview_schedule_obj.time), '%H:%M:%S').time())
                    schedule_activelink = schedule_date - datetime.timedelta(minutes=15)
                    schedule_activelink = time_zone.localize(schedule_activelink)
                    schedule_activelink = schedule_activelink.astimezone(pytz.utc)
                    print(schedule_activelink)
                    print("sdasdsadsa",datetime.datetime.now())
                    all_assign_users = AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj)
                    if not current_stage==None:
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview Confirmed",
                                                                                        description="Candidate confirmed the InterView time.",image="/static/notifications/icon/company/Application_Review.png",
                                                                                        target_url=header+"://"+current_site.domain+"/agency/agency_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                            job_obj.id))
                    Scheduler.add_job(
                                    activate_link,
                                    trigger=DateTrigger(run_date=schedule_activelink),
                                    args = [interview_schedule_obj],
                                    misfire_grace_time=6000
                                    # replace_existing=True
                                )
                    duration=datetime.datetime.strptime(str(interview_schedule_obj.interview_duration), '%H:%M').time()
                    A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                    totalsecond = A.total_seconds()
                    schedule_deactivelink = schedule_date + datetime.timedelta(seconds=totalsecond)
                    schedule_deactivelink = time_zone.localize(schedule_deactivelink)
                    schedule_deactivelink = schedule_deactivelink.astimezone(pytz.utc)
                    print(schedule_deactivelink)
                    Scheduler.add_job(
                                    deactivate_link,
                                    trigger=DateTrigger(run_date=schedule_deactivelink),
                                    args = [interview_schedule_obj],
                                    misfire_grace_time=6000
                                    # replace_existing=True
                                )
                    
            interview_schedule_data = None
            job_offer_data = None
            custom_round_data = None
            stages_data = []
            for stage in stages_status:
                stage_dict = {'stage': stage, 'result': ''}
                if stage.stage.name == 'Custom':
                    custom_template = AgencyModels.CustomTemplate.objects.filter(agency_id=stage.agency_id,template=stage.template)
                    if custom_template.exists():
                        custom_template = custom_template[0]
                        custom_round_data = AgencyModels.CustomResult.objects.filter(candidate_id=stage.candidate_id,agency_id=stage.agency_id,
                                                    job_id=stage.job_id,custom_template=custom_template)
                        custom_round_data = custom_round_data.first() if custom_round_data.exists() else None
                if stage.stage.name == 'Interview':

                    interview_schedule_obj = AgencyModels.InterviewSchedule.objects.filter(candidate_id=candidate_obj,
                                                                                    job_id=job_obj,
                                                            agency_id=stage.agency_id,
                                                            template=stage.template,
                                                            job_stages_id=stage)
                    print('\n\nin Interview',interview_schedule_obj)
                    if interview_schedule_obj.exists():
                        interview_schedule_data = interview_schedule_obj[0]

                if stage.stage.name == 'Job Offer':
                    print('\n\nin Job Offer')
                    job_offer_obj = AgencyModels.JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
                                                                                    agency_id=stage.agency_id,
                                                                                    job_stages_id=stage)
                    if job_offer_obj.exists():
                        job_offer_data = job_offer_obj[0]

                if stage.status == 2 or stage.status == -1 or stage.status == 3:
                    if stage.stage.name == 'JCR':
                        jcr_result = models.JcrRatio.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        stage_dict['result'] = jcr_result

                    if stage.stage.name == 'Prerequisites':
                        prerequisites_result = models.Agency_PreRequisitesFill.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                    template=stage.template)
                        stage_dict['result'] = prerequisites_result

                    if stage.stage.name == 'MCQ Test':
                        if not stage.reject_by_candidate:
                            mcq_test_result = models.Agency_Mcq_Exam_result.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                        template=stage.template)
                            print('\n\n \nmcq_test_result', mcq_test_result)
                            stage_dict['result'] = mcq_test_result
                        else:
                            stage_dict['result'] = None

                    if stage.stage.name == 'Descriptive Test':
                        if not stage.reject_by_candidate:
                            descriptive_result = models.AgencyDescriptive_Exam_result.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                        template=stage.template)
                            stage_dict['result'] = descriptive_result
                        else:
                            stage_dict['result'] = None


                    if stage.stage.name == 'Image Test':
                        if not stage.reject_by_candidate:
                            image_result = models.Agency_Image_Exam_result.objects.get(agency_id=stage.agency_id,candidate_id=stage.candidate_id,job_id=job_obj,
                                                        template=stage.template)
                            stage_dict['result'] = image_result
                        else:
                            stage_dict['result'] = None

                stages_data.append(stage_dict)

            print('stages_data>>>>>>>>>>>>>>>>>', stages_data)
            chat_internal =AgencyModels.AgencyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,agency_id=job_obj.agency_id)

            candidate_job_status = None
            if AgencyModels.CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
                candidate_job_status = AgencyModels.CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)

            candidate_apply_details = None
            if AgencyModels.AppliedCandidate.objects.filter(candidate=candidate_obj,agency_id=job_obj.agency_id).exists():
                candidate_apply_details = AgencyModels.AppliedCandidate.objects.get(candidate_id=candidate_obj, job_id=job_obj)
            return render(request, 'candidate/ATS/agency_applied-candidates-details.html',
                        {'workflow_stages': workflow_stages, 'job_obj': job_obj,'stages_status':stages_status,'candidate_apply_details':candidate_apply_details,
                        'stages_data':stages_data,'interview_schedule_data':interview_schedule_data,
                        'job_offer_data':job_offer_data,'chat_internal':chat_internal,'custom_round_data':custom_round_data,
                        'candidate_job_status':candidate_job_status})
    else:
        return redirect('candidate:basic_detail')
def activate_link(interview_schedule_obj):
    interview_schedule_obj.interview_start_button_status=True
    interview_schedule_obj.save()
    notify.send(interview_schedule_obj.candidate_id, recipient=interview_schedule_obj.candidate_id, verb="Interview",
                            description="Your Live interview session is about to start in 15 min",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                interview_schedule_obj.job_id.id)+"/agency")
    all_assign_users = models.CompanyAssignJob.objects.filter(job_id=interview_schedule_obj.job_id)
    for i in all_assign_users:
        if i.recruiter_type_internal:
            if i.recruiter_id.id != request.user.id:
                notify.send(interview_schedule_obj.candidate_id, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview",
                                                                    description="Your Live interview session is about to start in 15 min",image="/static/notifications/icon/company/Application_Review.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(interview_schedule_obj.candidate_id.id)+"/" + str(
                                                                        interview_schedule_obj.job_id.id))
    print("activaaaaaaaaaate callllllledd")

def deactivate_link(interview_schedule_obj):
    interview_schedule_obj.interview_start_button_status=False
    interview_schedule_obj.save()
    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")


def agency_candidate_negotiate_offer(request,id):
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(id=id)
    if not stage_status.status == -1:
        if request.method == 'POST':
            if 'accept_offer' in request.POST:
                old_offer = AgencyModels.OfferNegotiation.objects.get(id=request.POST.get('negotiation_id'))
                old_offer.action_performed = True
                old_offer.action_name = 'Accepted'
                old_offer.save()

                stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(id=id)
                job_offer_obj = AgencyModels.JobOffer.objects.get(job_stages_id=stage_status)
                job_offer_obj.is_accepted = True
                job_offer_obj.save()
                stage_status.status = 2
                stage_status.save()
            elif 'reject_offer' in request.POST:
                stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(id=id)
                job_offer_obj = AgencyModels.JobOffer.objects.get(job_stages_id=stage_status)
                last_negotiation_obj = job_offer_obj.negotiations.filter(action_performed=False)
                if last_negotiation_obj.exists():
                    last_negotiation = last_negotiation_obj[0]
                    last_negotiation.action_performed = True
                    last_negotiation.action_name = 'Rejected By Candidate'
                    last_negotiation.save()
                job_offer_obj.is_accepted = False
                job_offer_obj.rejected_by_candidate = True
                job_offer_obj.save()
                stage_status.status = -1
                stage_status.save()
                return redirect('candidate:applied_job_detail', stage_status.job_id)
            else:
                old_offer = AgencyModels.OfferNegotiation.objects.get(id=request.POST.get('negotiation_id'))
                negotiation_obj = AgencyModels.OfferNegotiation.objects.create(designation=request.POST.get('designation'),
                                                                         annual_ctc=request.POST.get('negotiate_salary'),
                                                                         notice_period=request.POST.get('notice_period'),
                                                                         joining_date=request.POST.get('join_date'),
                                                                         other_details=request.POST.get('other_details'),
                                                                         from_company=False)
                stage_status = CandidateJobStagesStatus.objects.get(id=id)
                job_offer_obj = AgencyModels.JobOffer.objects.get(job_stages_id=stage_status)
                job_offer_obj.negotiations.add(negotiation_obj)

                old_offer.action_performed = True
                old_offer.action_name = 'Negotiated'
                old_offer.save()
                Tracker.objects.update_or_create(job_id=stage_status.job_id,candidate_id=stage_status.candidate_id,company_id=stage_status.company_id,defaults={
                                                                'action_required':'Negotiation By Company/Candidate','update_at':datetime.datetime.now()})
        stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(id=id)
        job_offer_obj = AgencyModels.JobOffer.objects.get(job_stages_id=stage_status)

        return render(request, 'candidate/ATS/agency/candidate_negotiate_offer.html', {'job_offer_obj':job_offer_obj,'negotiations':job_offer_obj.negotiations.all().order_by('-id')})
    else:
        return HttpResponse(False)


def list_of_agency_company(request):
    context={}
    context['company_list']=InternalCandidateBasicDetails.objects.filter(email=request.user.email,withdraw_by_Candidate=False)
    context['agency_list'] = AgencyModels.InternalCandidateBasicDetail.objects.filter(email=request.user.email,withdraw_by_Candidate=False)
    getcompany_list=InternalCandidateBasicDetails.objects.filter(email=request.user.email,withdraw_by_Candidate=False).values_list('company_id')
    getagency_list=AgencyModels.InternalCandidateBasicDetail.objects.filter(email=request.user.email,withdraw_by_Candidate=False).values_list('agency_id')
    context['chat_internal_company'] = Employee.objects.filter(company_id__in=getcompany_list)
    context['chat_internal_agency'] = AgencyModels.InternalUserProfile.objects.filter(agency_id__in=getagency_list)
    return render(request,'candidate/ATS/listocompany-agency.html',context)


def company_profile(request,id):
    if id:
        profile = CompanyProfile.objects.get(company_id=Company.objects.get(id=id))
        if not profile:
            return redirect('company:add_edit_profile')
        else:
            profile = CompanyProfile.objects.get(company_id=Company.objects.get(id=id))
            get_internalcandidate = InternalCandidateBasicDetails.objects.filter(
                company_id=Company.objects.get(id=id))
            completed_job = JobCreation.objects.filter(
                company_id=Company.objects.get(id=id))
            chat_internal = Employee.objects.filter(company_id=Company.objects.get(id=id))
        return render(request, 'candidate/ATS/company-profile.html', {'get_profile': profile,'completed_job':len(completed_job),'get_internalcandidate':len(get_internalcandidate),'chat_internal':chat_internal})
    else:
        return render(request, 'accounts/404.html')


def custom_round(request,id):
    stage_obj = CandidateJobStagesStatus.objects.get(id=id)
    if stage_obj.status == 1:
        custom_round_obj = CustomTemplate.objects.filter(company_id=stage_obj.company_id,
                                                                template=stage_obj.template)
        if custom_round_obj.exists():
            custom_round_data = custom_round_obj[0]
            if request.method == 'POST':
                description = request.POST.get('description')
                file_by_candidate = request.FILES.get('response_file')
                print('file by cand', file_by_candidate)
                custom_result, created = CustomResult.objects.update_or_create(
                    candidate_id=stage_obj.candidate_id,
                    company_id=stage_obj.company_id, job_id=stage_obj.job_id,
                    custom_template=custom_round_data,
                    defaults={
                       'submitted_file_by_candidate':file_by_candidate, 'description_by_candidate': description,
                    })
                stage_obj.status = 2
                stage_obj.save()
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                notify.send(request.user, recipient=request.user, verb="Manual",
                                        description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                            job_obj.id)+"/company")
                return redirect('candidate:applied_job_detail', stage_obj.job_id.id)
            return render(request, "candidate/ATS/custom_round_exam.html", {'custom_round_data': custom_round_data})
    else:
        return HttpResponse(False)


def withdraw_candidate(request,user_type,id):
    if user_type=='Company':
        if InternalCandidateBasicDetails.objects.filter(candidate_id=request.user,company_id=Company.objects.get(id=id)).exists():
            InternalCandidateBasicDetails.objects.filter(candidate_id=request.user,company_id=Company.objects.get(id=id)).update(withdraw_by_Candidate=True)
    if user_type=='Agency':
        if InternalCandidateBasicDetail.objects.filter(candidate_id=request.user,agency_id=AgencyModels.Agency.objects.get(id=id)).exists():
            InternalCandidateBasicDetail.objects.filter(candidate_id=request.user,agency_id=AgencyModels.Agency.objects.get(id=id)).update(withdraw_by_Candidate=True)
    return redirect('candidate:list_of_agency_company')


def refresh_detect(request,id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('UTF-8'))
        stage_obj = CandidateJobStagesStatus.objects.filter(id=id)
       
        if stage_obj.exists():
            stage = stage_obj[0]
            if not stage.stage.name == 'Prerequisites':
                scheduler_id = str(stage.template.id)+str(stage.job_id.id)+str(stage.candidate_id.id)
                Scheduler.remove_job(scheduler_id)
            stage.reject_by_candidate = True
            stage.status = -1
            stage.save()
        return HttpResponse(True)


def applicant_create_account(request,applicant_id):
    get_applicant=None
    context={}
    if User.objects.filter(id=applicant_id,is_candidate=True,is_active=False).exists():
        get_applicant=User.objects.get(id=applicant_id,is_candidate=True,is_active=False)
        context['fname']=get_applicant.first_name
        context['lname']=get_applicant.last_name
        context['email']=get_applicant.email
        context['applicant_id']=get_applicant.id
    if request.method == 'POST':
        if get_applicant:
            get_applicant.set_password(request.POST.get('password'))
            get_applicant.save()
            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            # print('domain----===========',current_site.domain)
            html_content = render_to_string('accounts/acc_active_email.html', {'user': get_applicant,
                                                                                'name': get_applicant.first_name + ' ' + get_applicant.last_name,
                                                                                'email': get_applicant.email,
                                                                                'domain': current_site.domain,
                                                                                'uid': urlsafe_base64_encode(
                                                                                    force_bytes(get_applicant.pk)),
                                                                                'token': account_activation_token.make_token(
                                                                                    get_applicant), })
            to_email = get_applicant.email
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return activate_account_confirmation(request, get_applicant.first_name + ' ' + get_applicant.last_name, get_applicant.email)

    return render(request,'candidate/ATS/applicant_create_account.html',context)












def agency_mcq_exam(request, id, job_id):
    # 1=right
    # -1=Wrong
    # 0=skip
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
         
    if stage_status.status == 1:
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        mcqtem = AgencyModels.ExamTemplate.objects.get(template=AgencyModels.Template_creation.objects.get(id=id))


        if not mcqtem.exam_type == 'custom':
            questions = AgencyModels.mcq_Question.objects.filter(agency_id=mcqtem.agency_id,mcq_subject=mcqtem.subject.id)
            basic_questions = list(questions.filter(question_level__level_name='basic'))
            intermediate_questions =list( questions.filter(question_level__level_name='intermediate'))
            advanced_questions =list( questions.filter(question_level__level_name='advance'))
            random.shuffle(basic_questions)
            random.shuffle(intermediate_questions)
            random.shuffle(advanced_questions)
            basic_questions = random.sample(basic_questions,int(mcqtem.basic_questions_count))
            intermediate_questions = random.sample(intermediate_questions,int( mcqtem.intermediate_questions_count))
            advanced_questions = random.sample(advanced_questions,int(mcqtem.advanced_questions_count))
            if models.AgencyRandomMCQExam.objects.filter(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id).exists():
                delete_question=models.AgencyRandomMCQExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                delete_question.question.clear()
                for i in basic_questions:
                    delete_question.question.add(i)
                for i in intermediate_questions:
                    delete_question.question.add(i)
                for i in advanced_questions:
                    delete_question.question.add(i)
            else:
                add_random=models.AgencyRandomMCQExam.objects.create(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                for i in basic_questions:
                    add_random.question.add(i)
                for i in intermediate_questions:
                    add_random.question.add(i)
                for i in advanced_questions:
                    add_random.question.add(i)
        # mcqpaper = QuestionPaper.objects.get(exam_template=ExamTemplate.objects.get(template=Template_creation.objects.get(id=id)))
        que = []
        count = 0
        if not mcqtem.question_wise_time:
            time=mcqtem.duration.split(':')
            timer_obj = models.Agency_ExamTimeStatus.objects.filter(candidate_id=request.user, template=mcqtem.template,
                                                             job_id=job_obj)
            if timer_obj.exists():
                timer_obj = timer_obj.get(candidate_id=request.user, template=mcqtem.template, job_id=job_obj)
                start_time = timer_obj.start_time
            else:
                timer_obj = models.Agency_ExamTimeStatus.objects.create(candidate_id=request.user, template=mcqtem.template,
                                                                 job_id=job_obj,
                                                                 start_time=datetime.datetime.now(timezone.utc))
                start_time = datetime.datetime.now(timezone.utc)
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.now(timezone.utc)
                print(start_time)
                duration=datetime.datetime.strptime(str(mcqtem.duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
                schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
                print('end mcq===========================',schedule_end_mcq)
                getjob=Scheduler.get_jobs()
                for job in getjob:
                    if job.id==str(id)+str(job_id)+str(request.user.id):
                        print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                        Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
                Scheduler.add_job(
                                end_mcq,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )                                         

            current_date = datetime.datetime.now(timezone.utc)
            elapsed_time = current_date - start_time

            elapsed_seconds = int(elapsed_time.total_seconds())
            hours = int(elapsed_seconds / 3600) % 24
            minutes = int(elapsed_seconds / 60) % 60
            seconds = int(elapsed_seconds % 60)
            print("remaininsec", elapsed_seconds)
            elapsed_time = pad_time(hours) + ":" + pad_time(minutes) + ":" + pad_time(seconds)
            time = mcqtem.duration.split(':')
            # available_seconds = int(elapsed_seconds)
            available_seconds = ((int(time[0]) * 3600) + (int(time[1])*60))-elapsed_seconds
            if mcqtem.exam_type=='random':
                get_question=models.AgencyRandomMCQExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                for l in get_question.question.all():
                    # get_time = ExamQuestionUnit.objects.get(question=mcq_Question.objects.get(id=int(l.id)))
                    que.append({'dbid': l.id, 'id': count + 1,
                                'choice_no': ['a', 'b', 'c', 'd'],
                                'question': l.question_description,
                                'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                })
                    count += 1
            else:
                if mcqtem.marking_system=='question_wise':
                    get_times = AgencyModels.ExamQuestionUnit.objects.filter(template_id=AgencyModels.Template_creation.objects.get(id=id))
                    for get_time in get_times:
                        que.append({'dbid': get_time.question.id, 'id': count + 1,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'question': get_time.question.question_description,
                                    'choices': [get_time.question.option_a, get_time.question.option_b, get_time.question.option_c, get_time.question.option_d]
                                    })
                        count += 1
                else:
                    print('question_wise====================question_wise',mcqtem)
                    for l in mcqtem.basic_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
                    for l in mcqtem.intermediate_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
                    for l in mcqtem.advanced_questions.all():
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.question_description,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [l.option_a, l.option_b, l.option_c, l.option_d]
                                    })
                        count += 1
            count = 0
            print(que)
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/agency/candidate_mcq_exam.html', {'time':available_seconds,'elapsed_time':elapsed_time,'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
        elif mcqtem.question_wise_time:
            get_times = AgencyModels.ExamQuestionUnit.objects.filter(template_id=AgencyModels.Template_creation.objects.get(id=id))
            total_time=0
            for get_time in get_times:
                print(get_time.question_time)
                time = get_time.question_time.split(':')
                available_seconds = int(time[0]) * 60 + int(time[1])
                total_time += available_seconds
                que.append({'dbid': get_time.question.id, 'id': count + 1,
                            'time': available_seconds,
                            'choice_no': ['a', 'b', 'c', 'd'],
                            'question': get_time.question.question_description,
                            'choices': [get_time.question.option_a, get_time.question.option_b, get_time.question.option_c, get_time.question.option_d]
                            })
                count += 1
            count = 0
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            Scheduler.add_job(
                            agency_end_mcq,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )    
            getStoreData = json.dumps(que)
            print(total_time)
            return render(request, 'candidate/ATS/agency/candidate_mcq_exam_if_question.html',
                          {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def agency_mcq_exam_fill(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        mcqtem = AgencyModels.ExamTemplate.objects.get(template=template_obj)
        # models.ExamTimeStatus.objects.update_or_create(candidate_id=request.user, template=mcqtem.template,
        #                                      job_id=job_obj,defaults={
        #                                      'start_time':datetime.datetime.now(timezone.utc)})
        print("=========================", mcq_data)
        mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        que = AgencyModels.mcq_Question.objects.get(id=int(mca_que_id))
        cat_mark=0
        if mcqtem.marking_system == 'question_wise':
            get_marks = AgencyModels.ExamQuestionUnit.objects.get(question=AgencyModels.mcq_Question.objects.get(id=int(mca_que_id)),
                                                     template=template_obj)
            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                if mcq_ans == que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = get_marks.question_mark
                    else:
                        getmarks = get_marks.question_mark
                    check_ans = 1
                elif mcq_ans != que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = (get_marks.question_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        elif mcqtem.marking_system == 'category_wise':
            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                get_que_type = AgencyModels.mcq_Question.objects.get(id=int(mca_que_id))
                if get_que_type.question_level.level_name == 'basic':
                    cat_mark = int(mcqtem.basic_question_marks)
                elif get_que_type.question_level.level_name == 'intermediate':
                    cat_mark = int(mcqtem.intermediate_question_marks)
                elif get_que_type.question_level.level_name == 'advance':
                    cat_mark = int(mcqtem.advanced_question_marks)
                print(mcq_ans,"=======================",que.correct_option)
                if mcq_ans == que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = cat_mark
                    else:
                        getmarks = cat_mark
                    check_ans = 1
                elif mcq_ans != que.correct_option:
                    if mcqtem.allow_negative_marking:
                        getmarks = (cat_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        models.Agency_Mcq_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 agency_id=job_obj.agency_id,
                                                 question=AgencyModels.mcq_Question.objects.get(id=que.id),
                                                 job_id=job_obj,
                                                 template=template_obj, defaults={
                'marks': getmarks,
                'status': check_ans,
                'time': mca_que_time}
                                                 )
        if mcq_data['last']:
            data['url']=str(current_site.domain+'/candidate/agency_mcq_result/'+str(id)+'/'+str(job_id))
            data['last']=True
        else:
            print("==================================================")
            data['last'] = False
        data["status"]= True
    else:
        data["status"]= False
    return JsonResponse(data)


def agency_mcq_result(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    get_result = models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)
    get_time=models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj).last()
    mcqtem = AgencyModels.ExamTemplate.objects.get(agency_id=job_obj.agency_id,template=template_obj)
    # total_time = datetime.datetime.strptime(mcqtem.duration+':00', '%H:%M:%S')
    # last_time = datetime.datetime.strptime(get_time.time, '%H:%M:%S')
    obain_time = 10
    obain_marks = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            # obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.question_description + """</div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/MCQ/".format(request.user.id, job_obj.id)
    getresult,created = models.Agency_Mcq_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'mcq_pdf':path +request.user.first_name+ "mcq.pdf"})
    # pdfkit.from_string(a, output_path=path +request.user.first_name+ "mcq.pdf", configuration=config)



    # move to next stage process

    # onthego change
    job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_stage = ''
    currentcompleted=False
    next_stage = None
    action_required=''
    reject=False
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if job_workflow.withworkflow:
        main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = AgencyModels.WorkflowStages.objects.get(workflow=main_workflow,template=template_obj)
        config_obj = AgencyModels.WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)
        current_stage=stage_status.stage
        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                currentcompleted=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
                
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                reject=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                action_required='Company'
                stage_status.save()
            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            action_required='Company'
            stage_status.save()

        if not reject:
            new_sequence_no = stage_status.sequence_number + 1
            if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                        sequence_number=new_sequence_no).exists():
                new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                next_stage=new_stage_status.stage
    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    
    if not next_stage==None and action_required=='':
        if next_stage.name=='Interview' :
            action_required='Company/Agency'
        else:
            action_required='Candidate'
    if current_stage!='':
        if current_stage.name=='Job Offer':
            action_required='Offer Letter Generation By Company'
        # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
        #                                                             'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
        #                                                             'action_required':action_required,'update_at':datetime.datetime.now()})
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/agency/end_exam.html',{'get_result': getresult, "job_id": job_obj.id})

def agency_start_mcq(template_id, job_id):
    print("activaaaaaaaaaate callllllledd")

def agency_end_mcq(template_id, job_id,loginuser_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    get_result = models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)
    get_time=models.Agency_Mcq_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj).last()
    mcqtem = AgencyModels.ExamTemplate.objects.get(agency_id=job_obj.agency_id,template=template_obj)
    # total_time = datetime.datetime.strptime(mcqtem.duration+':00', '%H:%M:%S')
    # last_time = datetime.datetime.strptime(get_time.time, '%H:%M:%S')
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    obain_time = 10
    obain_marks = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            # obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.question_description + """</div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/MCQ/".format(loginuser_id, job_obj.id)
    getresult,created = models.Agency_Mcq_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'mcq_pdf':path +user_obj.first_name+ "mcq.pdf"})
    pdfkit.from_string(a, output_path=path +user_obj.first_name+ "mcq.pdf", configuration=config)



    # move to next stage process

    # onthego change
    job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_stage = ''
    currentcompleted=False
    next_stage = None
    action_required=''
    reject=False
    if job_workflow.withworkflow:
        main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = AgencyModels.WorkflowStages.objects.get(workflow=main_workflow,template=template_obj)
        config_obj = AgencyModels.WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)
        current_stage=stage_status.stage
        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                currentcompleted=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                reject=True
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=i), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                action_required='Company'
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            action_required='Company'
            stage_status.save()
            
        if not reject:
            new_sequence_no = stage_status.sequence_number + 1
            if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                        sequence_number=new_sequence_no).exists():
                new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                next_stage=new_stage_status.stage
    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    
    if not next_stage==None and action_required=='':
        if next_stage.name=='Interview' :
            action_required='Company/Agency'
        else:
            action_required='Candidate'
    if current_stage!='':
        if current_stage.name=='Job Offer':
            action_required='Offer Letter Generation By Company'
        # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
        #                                                             'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,'reject':reject,
        #                                                             'action_required':action_required,'update_at':datetime.datetime.now()})
    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")

# agency image=============================

def agency_image_exam(request, id, job_id):
    # 1=right
    # -1=Wrong
    # 0=skip
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    if stage_status.status == 1:
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        mcqtem = AgencyModels.ImageExamTemplate.objects.get(template=AgencyModels.Template_creation.objects.get(id=id))
        if not mcqtem.exam_type == 'custom':
            questions = AgencyModels.ImageQuestion.objects.filter(agency_id=mcqtem.agency_id,subject=mcqtem.subject.id)
            basic_questions = list(questions.filter(question_level__level_name='basic'))
            intermediate_questions =list( questions.filter(question_level__level_name='intermediate'))
            advanced_questions =list( questions.filter(question_level__level_name='advance'))
            random.shuffle(basic_questions)
            random.shuffle(intermediate_questions)
            random.shuffle(advanced_questions)
            basic_questions = random.sample(basic_questions,int(mcqtem.basic_questions_count))
            intermediate_questions = random.sample(intermediate_questions,int( mcqtem.intermediate_questions_count))
            advanced_questions = random.sample(advanced_questions,int(mcqtem.advanced_questions_count))
            if models.RandomImageExam.objects.filter(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id).exists():
                delete_question=models.RandomImageExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                delete_question.question.clear()
                for i in basic_questions:
                    delete_question.question.add(i)
                for i in intermediate_questions:
                    delete_question.question.add(i)
                for i in advanced_questions:
                    delete_question.question.add(i)
            else:
                add_random=models.RandomImageExam.objects.create(candidate_id=User.objects.get(id=request.user.id),template=AgencyModels.Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                for i in basic_questions:
                    add_random.question.add(i)
                for i in intermediate_questions:
                    add_random.question.add(i)
                for i in advanced_questions:
                    add_random.question.add(i)
        # imagepaper = ImageQuestionPaper.objects.get(exam_template=mcqtem)
        que = []
        count = 0
        if not mcqtem.question_wise_time:
            time=mcqtem.duration.split(':')
            timer_obj = models.Agency_ExamTimeStatus.objects.filter(candidate_id=request.user, template=mcqtem.template,
                                                             job_id=job_obj)
            if timer_obj.exists():
                timer_obj = timer_obj.get(candidate_id=request.user, template=mcqtem.template, job_id=job_obj)
                start_time = timer_obj.start_time
            else:
                # timer_obj = models.ExamTimeStatus.objects.create(candidate_id=request.user, template=mcqtem.template,
                #                                                  job_id=job_obj,
                #                                                  start_time=datetime.datetime.now(timezone.utc))
                # start_time = datetime.datetime.now(timezone.utc)
                start_time = datetime.datetime.now(timezone.utc)
                time_zone = pytz.timezone("Asia/Calcutta")
                schedule_date=datetime.datetime.now(timezone.utc)
                print(start_time)
                duration=datetime.datetime.strptime(str(mcqtem.duration), '%H:%M').time()
                A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
                totalsecond = A.total_seconds()
                schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
                schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
                print('end image===========================',schedule_end_mcq)
                getjob=Scheduler.get_jobs()
                for job in getjob:
                    if job.id==str(id)+str(job_id)+str(request.user.id):
                        Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
                Scheduler.add_job(
                                end_image,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )             
            current_date = datetime.datetime.now(timezone.utc)
            print(current_date)
            print(start_time)
            elapsed_time = current_date - start_time

            elapsed_seconds = int(elapsed_time.total_seconds())
            hours = int(elapsed_seconds / 3600) % 24
            minutes = int(elapsed_seconds / 60) % 60
            seconds = int(elapsed_seconds % 60)
            print("remaininsec", elapsed_seconds)
            elapsed_time = pad_time(hours) + ":" + pad_time(minutes) + ":" + pad_time(seconds)
            time = mcqtem.duration.split(':')
            # available_seconds = int(elapsed_seconds)
            available_seconds = ((int(time[0]) * 3600) + (int(time[1])*60)) - elapsed_seconds
            if mcqtem.exam_type == 'random':
                get_question = models.RandomImageExam.objects.get(candidate_id=User.objects.get(id=request.user.id),template=Template_creation.objects.get(id=id),job_id=job_obj,agency_id=job_obj.agency_id)
                for l in get_question.question.all():
                    imageoption = AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=l.id))
                    # options = [imageoption.file1.url if imageoption.file1 else None]
                    que.append({'dbid': l.id, 'id': count + 1,
                                'question': l.image_que_description,
                                'q_image':l.question_file.url,
                                'choice_no': ['a', 'b', 'c', 'd'],
                                'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                })
                    print(que)
                    count += 1
            else:
                print("=====================================")
                if mcqtem.marking_system=='question_wise':
                    get_times = AgencyModels.ImageExamQuestionUnit.objects.filter(template_id=AgencyModels.Template_creation.objects.get(id=id))
                    for get_time in get_times:
                        print("======================================s")
                        imageoption = AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=get_time.question.id).id)
                        que.append({'dbid': get_time.question.id, 'id': count + 1,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'question': get_time.question.image_que_description,
                                    'q_image':get_time.question.question_file.url,
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                else:
                    for l in mcqtem.basic_questions.all():
                        print(l.id)
                        imageoption=AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                    for l in mcqtem.intermediate_questions.all():
                        print(l.id)
                        imageoption=AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage': [imageoption.file1.url if imageoption.file1 else None,
                                                    imageoption.file2.url if imageoption.file2 else None,
                                                    imageoption.file3.url if imageoption.file3 else None,
                                                    imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
                    for l in mcqtem.advanced_questions.all():
                        print(l.id)
                        imageoption=AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=l.id))
                        # options = [imageoption.file1.url if imageoption.file1 else None for imageoptions in imageoption]
                        que.append({'dbid': l.id, 'id': count + 1,
                                    'question': l.image_que_description,
                                    'q_image':l.question_file.url if l.question_file else None,
                                    'choice_no': ['a', 'b', 'c', 'd'],
                                    'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                                    'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                                    })
                        count += 1
            count = 0
            print("\n\nque",que)
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/agency/candidate_image_exam.html', {'time':available_seconds,'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
        elif mcqtem.question_wise_time:
            get_times = AgencyModels.ImageExamQuestionUnit.objects.filter(template_id=AgencyModels.Template_creation.objects.get(id=id))
            total_time=0
            for get_time in get_times:
                print("======================================s")
                time = get_time.question_time.split(':')
                available_seconds = int(time[0]) * 60 + int(time[1])
                imageoption = AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=get_time.question.id))
                total_time += available_seconds
                que.append({'dbid': get_time.question.id, 'id': count + 1,
                            'time': available_seconds,
                            'choice_no': ['a', 'b', 'c', 'd'],
                            'question': get_time.question.image_que_description,
                            'q_image':get_time.question.question_file.url,
                            'choices': [imageoption.option1,imageoption.option2,imageoption.option3,imageoption.option4],
                            'choicesimage':[imageoption.file1.url if imageoption.file1 else None,imageoption.file2.url if imageoption.file2 else None,imageoption.file3.url if imageoption.file3 else None,imageoption.file4.url if imageoption.file4 else None]
                            })
                count += 1
            count = 0
            print(total_time)
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end image===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            
            Scheduler.add_job(
                            agency_end_image,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )    
            getStoreData = json.dumps(que)
            return render(request, 'candidate/ATS/agency/candidate_image_exam_if_question.html',
                          {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def agency_image_exam_fill(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        print(mcq_data)
        mcqtem = AgencyModels.ImageExamTemplate.objects.get(template=template_obj)
        print("=========================", mcq_data)
        mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        image_path=mcq_data['image_path']
        print('\n\nimage_path', image_path)
        s2 = "media/"
        # image_path=image_path[image_path.index(s2) + len(s2):]
        que = AgencyModels.ImageQuestion.objects.get(id=int(mca_que_id))
        que_ans = AgencyModels.ImageOption.objects.get(question_id=AgencyModels.ImageQuestion.objects.get(id=int(mca_que_id)))
        cat_mark=0

        if mcqtem.marking_system == 'question_wise':
            get_marks = AgencyModels.ImageExamQuestionUnit.objects.get(question=AgencyModels.ImageQuestion.objects.get(id=int(mca_que_id)),
                                                          template=template_obj)

            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                if mcq_ans == que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = get_marks.question_mark
                    else:
                        getmarks = get_marks.question_mark
                    check_ans = 1
                elif mcq_ans != que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = (get_marks.question_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        elif mcqtem.marking_system == 'category_wise':

            if mcq_ans == '':
                if mcqtem.allow_negative_marking:
                    getmarks = 0
                else:
                    getmarks = 0
                check_ans = 0
            else:
                get_que_type = AgencyModels.ImageQuestion.objects.get(id=int(mca_que_id))
                if get_que_type.question_level.level_name == 'basic':
                    cat_mark = int(mcqtem.basic_question_marks)
                elif get_que_type.question_level.level_name == 'intermediate':
                    cat_mark = int(mcqtem.intermediate_question_marks)
                elif get_que_type.question_level.level_name == 'advance':
                    cat_mark = int(mcqtem.advanced_question_marks)
                if mcq_ans == que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = cat_mark
                    else:
                        getmarks = cat_mark
                    check_ans = 1
                elif mcq_ans != que_ans.answer:
                    if mcqtem.allow_negative_marking:
                        getmarks = (cat_mark * mcqtem.negative_mark_percent)/100
                    else:
                        getmarks = 0
                    check_ans = -1
        models.Agency_Image_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 agency_id=job_obj.agency_id,
                                                 question=AgencyModels.ImageQuestion.objects.get(id=que.id),
                                                 job_id=AgencyModels.JobCreation.objects.get(id=job_id),
                                                 template=template_obj, defaults={
                'ansfile' : image_path,
                'marks': getmarks,
                'status': check_ans,
                'time': mca_que_time}
                                                 )
        if mcq_data['last'] == True:
            data['url']=str(current_site.domain+'/candidate/agency_image_result/'+str(id)+'/'+str(job_id))
            data['last']=True


        else:
            print("==================================================")
            data['last'] = False
        data["status"]= True
    else:
        data["status"]= False
    return JsonResponse(data)

import base64


def agency_image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    if not os.path.isfile(image_file):
        return None

    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
        print((str(encoded_string)[-1:-50:-1]))
    return 'data:image/%s;base64,%s' % (format, str(encoded_string)[2:-2:])


def agency_image_result(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    user_obj = User.objects.get(id=request.user.id)
    get_result = models.Agency_Image_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)
    mcqtem = AgencyModels.ImageExamTemplate.objects.get(agency_id=job_obj.agency_id, template=template_obj)
    obain_marks = 0
    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.image_que_description + """<img height="300px" width="300px" src=\""""+ agency_image_as_base64(settings.MEDIA_ROOT[0:-7:] +i.question.question_file.url) +"""\"></div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/Image/".format(request.user.id, job_obj.id)
    getresult,created = models.Agency_Image_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'image_pdf':path +request.user.first_name+ "image.pdf"})

    # pdfkit.from_string(a, output_path=path+request.user.first_name + "image.pdf")

    job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    if job_workflow.withworkflow:
        main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = AgencyModels.WorkflowStages.objects.get(workflow=main_workflow, template=template_obj)
        config_obj = AgencyModels.WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)

        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=''
                next_stage=None
                action_required=''
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    current = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    current_stage=current.stage
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no+1).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no+1)
                    next_stage=new_stage_status.stage
                    print(next_stage)
                if not next_stage==None:
                    if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                    else:
                        action_required='Perform By Candidate'
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                #                                                 'current_stage':current_stage,'next_stage':next_stage,
                #                                                 'action_required':action_required,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                #                                                 'reject':True,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                #                                                 'action_required':'On Hold by Company','update_at':datetime.datetime.now()})
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            stage_status.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            notify.send(request.user, recipient=request.user, verb="Manual",
                                    description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/agency")

    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    
    return render(request, 'candidate/ATS/agency/end_exam.html',{'get_result':getresult,'job_id':job_id})


def agency_end_image(template_id, job_id,loginuser_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    user_obj = User.objects.get(id=loginuser_id)
    get_result = models.Agency_Image_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)
    mcqtem = AgencyModels.ImageExamTemplate.objects.get(agency_id=job_obj.agency_id, template=template_obj)
    obain_marks = 0
    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:
            obain_marks = obain_marks + i.marks
            ans_que+=1
        elif i.status == -1:
            obain_marks = obain_marks - i.marks
            ans_que+=1
        elif i.status == 0:
            obain_marks = obain_marks - i.marks
            no_ans_que+=1
        total_que+=1
    a = """<div style="background: #fff;">
        <div style="padding: 10px 15px;">

            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                <thead>
                  <tr style="border-bottom: 1px solid #324670;">
                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+mcqtem.exam_name+"""</th>
                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>"""+str(obain_marks)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>"""+str(ans_que)+"""</span></td>
                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>"""+str(no_ans_que)+"""</span></td>
                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min"""+str(obain_time)+"""</span></td>
                  </tr>
                </tbody>
            </table>
            <div>
    """
    for i in get_result:
        a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                        <div style="width: 100%;display: flex;color: #031b4e;">
                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-1</div>
                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.image_que_description + """<img height="300px" width="300px" src=\""""+ agency_image_as_base64(settings.MEDIA_ROOT[0:-7:] +i.question.question_file.url) +"""\"></div>
                        </div>
                        <div style="width: 100%;display: flex;color: #031b4e;">														
                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                            """
        if i.status == 1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Correct</div>"""
        elif i.status == -1:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Incorrect</div>"""
        elif i.status == 0:
            a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""
        a += """</div>
                    </div>

                    <div style="float: left;width: 7%;">"""
        if i.status == 1:
            a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
        elif i.status == -1:
            a += """<div style="text-align: center;color: #ff5353;">-""" + str(i.marks) + """</div>"""
        elif i.status == 0:
            a += """<div style="text-align: center;color: #ff5353;">""" + str(i.marks) + """</div>"""
        a += """</div>
                </div>"""
    a += """</div>
        </div>									
        </div>"""
    path = settings.MEDIA_ROOT + "{}/{}/Stages/Image/".format(loginuser_id, job_obj.id)
    getresult,created = models.Agency_Image_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':mcqtem.total_question, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10, 'obain_marks':obain_marks,
                                          'image_pdf':path +user_obj.first_name+ "image.pdf"})

    # pdfkit.from_string(a, output_path=path+user_obj.first_name + "image.pdf")

    job_workflow = AgencyModels.JobWorkflow.objects.get(job_id=job_obj)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if job_workflow.withworkflow:
        main_workflow = AgencyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
        workflow_stage = AgencyModels.WorkflowStages.objects.get(workflow=main_workflow, template=template_obj)
        config_obj = AgencyModels.WorkflowConfiguration.objects.get(workflow_stage=workflow_stage)

        if config_obj.is_automation:
            if int(obain_marks) >= int(config_obj.shortlist):
                flag = True
                stage_status.status = 2
                stage_status.action_performed = True
                stage_status.assessment_done = True
                current_stage=''
                next_stage=None
                action_required=''
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    current = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    current_stage=current.stage
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no+1).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no+1)
                    next_stage=new_stage_status.stage
                if not next_stage==None:
                    if next_stage.name=='Interview' :
                            action_required='Company/Agency'
                    else:
                        action_required='Perform By Candidate'
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                #                                                 'current_stage':current_stage,'next_stage':next_stage,
                #                                                 'action_required':action_required,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Application Shortlisted",
                            description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(obain_marks) <= int(config_obj.reject):
                flag = False
                stage_status.status = -1
                stage_status.action_performed = True
                stage_status.assessment_done = True
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                #                                                 'reject':True,'update_at':datetime.datetime.now()})
                stage_status.save()
                notify.send(request.user, recipient=User.objects.get(id=request.user.id), verb="Application Rejected",
                            description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
            elif int(config_obj.shortlist) > int(obain_marks) > int(config_obj.reject):
                flag = False
                stage_status.status = 3
                stage_status.action_performed = False
                stage_status.assessment_done = True
                # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
                #                                                 'action_required':'On Hold by Company','update_at':datetime.datetime.now()})
                stage_status.save()

            if flag:
                new_sequence_no = stage_status.sequence_number + 1
                if AgencyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=user_obj,
                                                           sequence_number=new_sequence_no).exists():
                    new_stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=user_obj,
                                                                            sequence_number=new_sequence_no)
                    new_stage_status.status = 1
                    new_stage_status.save()
                    notify.send(request.user, recipient=User.objects.get(email=email), verb="Interview Round",
                            description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/agency")
        else:
            stage_status.status = 2
            stage_status.action_performed = False
            stage_status.assessment_done = True
            stage_status.save()

    if job_workflow.onthego:
        stage_status.status = 2
        stage_status.action_performed = False
        stage_status.assessment_done = True
        stage_status.save()

    print("DEACTIVATE CAAAAAAAALEEEEEDEDEDEDEDE")


# Descriptive exam=====================================================
def agency_descriptive_exam(request, id, job_id):
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    total_time=0
    if stage_status.status == 1:
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        mcqtem = AgencyModels.DescriptiveExamTemplate.objects.get(template=AgencyModels.Template_creation.objects.get(id=id))
        mcqpaper = AgencyModels.DescriptiveQuestionPaper.objects.get(exam_template=mcqtem)
        que = []
        count = 0
        for l in mcqtem.descriptivequestions.all():
            get_time = AgencyModels.DescriptiveExamQuestionUnit.objects.get(question=AgencyModels.Descriptive.objects.get(id=int(l.id)),template=AgencyModels.Template_creation.objects.get(id=id))
            print(get_time.question_time)
            time = get_time.question_time.split(':')
            available_seconds = int(time[0]) * 60 + int(time[1])
            total_time += available_seconds
            que.append({'dbid': l.id, 'id': count + 1,
                        'time': available_seconds,
                        'question': l.paragraph_description
                        })
            count += 1
        count = 0
        start_time = datetime.datetime.now(timezone.utc)
        time_zone = pytz.timezone("Asia/Calcutta")
        schedule_date=datetime.datetime.now(timezone.utc)
        schedule_end_mcq = start_time + datetime.timedelta(seconds=total_time)
        schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
        print('end mcq===========================',schedule_end_mcq)
        getjob=Scheduler.get_jobs()
        for job in getjob:
            if job.id==str(id)+str(job_id)+str(request.user.id):
                print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
        Scheduler.add_job(
                        agency_end_descriptive,
                        trigger=DateTrigger(run_date=schedule_end_mcq),
                        args = [id,job_id,request.user.id],
                        misfire_grace_time=6000,
                        id=str(id)+str(job_id)+str(request.user.id)
                        # replace_existing=True
                    )    
        getStoreData = json.dumps(que)
        return render(request, 'candidate/ATS/agency/candidate_descriptive_exam.html',
                      {'getStoreData': getStoreData, 'job_obj': job_obj, 'temp_id': id,'stage_id':stage_status.id})
    else:
        return HttpResponse(False)


def agency_descriptive_exam_fill(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    data = {}
    current_site = get_current_site(request)
    if request.method == 'POST':
        mcq_data = json.loads(request.body.decode('UTF-8'))
        mcqtem = AgencyModels.DescriptiveExamTemplate.objects.get(template=template_obj)
        print("=========================", mcq_data)
        # mcq_ans = mcq_data['mcq_ans']
        mca_que_id = mcq_data['que_id']
        mca_que_time = mcq_data['que_time']
        ans = mcq_data['ans']
        que = AgencyModels.Descriptive.objects.get(id=int(mca_que_id))
        if ans == '':
            check_ans = 0
        else:
            check_ans = 1
        available_m = AgencyModels.DescriptiveExamQuestionUnit.objects.get(question=AgencyModels.Descriptive.objects.get(id=que.id),template=template_obj)
        models.AgencyDescriptive_Exam.objects.update_or_create(candidate_id=user_obj,
                                                 agency_id=job_obj.agency_id,
                                                 question=AgencyModels.Descriptive.objects.get(id=que.id),
                                                 job_id=job_obj,
                                                 template=template_obj, defaults={
                                                    'available_marks':available_m.question_mark,
                                                    'ans':ans,
                                                    'status': check_ans,
                                                    'time': mca_que_time}
                                                 )
        if mcq_data['last'] == True:
            data['url']=str(current_site.domain+'/candidate/descriptive_result/'+str(id)+'/'+str(job_id))
            data['last']=True

        else:
            print("==================================================")
            data['last'] = False
        data["status"] = True
    else:
        data["status"]= False
    return JsonResponse(data)


def agency_descriptive_result(request, id, job_id):
    
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    get_result = models.AgencyDescriptive_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)

    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:

            ans_que+=1
        elif i.status == -1:

            ans_que+=1
        elif i.status == 0:

            no_ans_que+=1
        total_que+=1

    getresult,created = models.AgencyDescriptive_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':total_que, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10,
                                          })

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    print("=============================================================")
    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
    #                                                             'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    notify.send(request.user, recipient=request.user, verb="Manual",
                            description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id))
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/agency/descriptive_end_exam.html',{'get_result':getresult,'job_id':job_id})


def agency_end_descriptive(template_id, job_id,loginuser_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    get_result = models.AgencyDescriptive_Exam.objects.filter(candidate_id=user_obj,
                                                agency_id=job_obj.agency_id,
                                                job_id=job_obj,
                                                template=template_obj)

    obain_time = 0
    total_que=0
    ans_que=0
    no_ans_que=0
    for i in get_result:

        if i.status == 1:

            ans_que+=1
        elif i.status == -1:

            ans_que+=1
        elif i.status == 0:

            no_ans_que+=1
        total_que+=1

    getresult,created = models.AgencyDescriptive_Exam_result.objects.update_or_create(candidate_id=user_obj,
                                          agency_id=job_obj.agency_id,
                                          job_id=job_obj,
                                          template=template_obj, defaults={
                                          'total_question':total_que, 'answered':ans_que,
                                          'not_answered':no_ans_que, 'obain_time':10,
                                          })

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    print("=============================================================")
    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
    #                                                             'action_required':'Assessment by Company','update_at':datetime.datetime.now()})


# Audio exam====================================agency


def agency_pad_time(number):
    if number<10:
        return "0"+str(number)
    else:
        return str(number)


def agency_audio_exam(request, id, job_id):
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user,
                                                        job_id__id=job_id)
    if stage_status.status == 1:
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        mcqtem = AgencyModels.AudioExamTemplate.objects.get(template=AgencyModels.Template_creation.objects.get(id=id))
        mcqpaper = AgencyModels.AudioQuestionPaper.objects.get(exam_template=mcqtem)
        timer_obj = models.Agency_ExamTimeStatus.objects.filter(candidate_id=request.user,template = mcqtem.template,job_id=job_obj)
        if timer_obj.exists():
            timer_obj = timer_obj.get(candidate_id=request.user,template = mcqtem.template,job_id=job_obj)
            start_time = timer_obj.start_time
        else:
            timer_obj = models.Agency_ExamTimeStatus.objects.create(candidate_id=request.user,template=mcqtem.template,job_id=job_obj,start_time=datetime.datetime.now(timezone.utc))
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            print(start_time)
            duration=datetime.datetime.strptime(str(mcqtem.total_exam_time), '%H:%M:%S').time()
            A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
            totalsecond = A.total_seconds()
            schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            Scheduler.add_job(
                            end_audio,
                            trigger=DateTrigger(run_date=schedule_end_mcq),
                            args = [id,job_id,request.user.id],
                            misfire_grace_time=6000,
                            id=str(id)+str(job_id)+str(request.user.id)
                            # replace_existing=True
                        )                           
        current_date = datetime.datetime.now(timezone.utc)

        elapsed_time = current_date-start_time

        elapsed_seconds = int(elapsed_time.total_seconds())
        hours = int(elapsed_seconds / 3600 ) % 24
        minutes = int(elapsed_seconds / 60 ) % 60
        seconds = int(elapsed_seconds % 60)
        print("remaininsec",elapsed_seconds)
        elapsed_time = agency_pad_time(hours)+":"+agency_pad_time( minutes)+":" + agency_pad_time(seconds)
        # time = mcqtem.total_exam_time.split(':')
        # # available_seconds = int(elapsed_seconds)
        # elapsed_time = (int(time[0]) * 60) + (int(time[1]))
        print("==========================================",elapsed_time)
        que = []
        count = 0
        print(mcqtem.audioquestions.all())
        for l in mcqtem.audioquestions.all():
            get_time = AgencyModels.AudioExamQuestionUnit.objects.get(question=AgencyModels.Audio.objects.get(id=int(l.id)),template=AgencyModels.Template_creation.objects.get(id=id))
            que.append({'dbid': l.id, 'id': count + 1,
                        'time': get_time.question_time,
                        'question': l.paragraph_description
                        })
            count += 1
        count = 0
        getStoreData = json.dumps(que)
        return render(request, 'candidate/ATS/agency/candidate_audio_video_exam_if_question.html',
                      {'getStoreData': getStoreData,'stage_id':stage_status.id, 'job_obj': job_obj, 'temp_id': mcqpaper.exam_template.template.id,"elapsed_time":elapsed_time,'total_exam_time':mcqtem.total_exam_time,"is_video":mcqtem.is_video})

    else:
        return HttpResponse(False)

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile


def agency_audio_exam_fill(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    data = {}
    template_creation_obj = AgencyModels.Template_creation.objects.get(id=id)
    audio_exam_template = AgencyModels.AudioExamTemplate.objects.get(template=template_creation_obj)
    audio_question_paper = AgencyModels.AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    current_site = get_current_site(request)
    if request.method == 'POST':
        attempt,updated = models.AgencyAudioExamAttempt.objects.update_or_create(candidate_id=request.user,agency_id=audio_question_paper.agency_id,audio_question_paper = audio_question_paper,job_id = job_obj)
        attempt.audio_question_attempts.remove()
        # all_blobs = request.POST.get("blobs")
        all_questions = request.POST.get("questions")
        all_questions = all_questions.split(",")
        for i in all_questions:
            audio_question = audio_question_paper.exam_question_units.get(question=AgencyModels.Audio.objects.get(id=int(i)))
            answer = request.FILES.get(str(i) + "blob")

            if audio_question_paper.exam_template.is_video:
                file_extension = ".mkv"
            else:
                file_extension = ".wav"
            question_attempt = models.AgencyAudioExamQuestionAttemptUnit.objects.create(audio_question=audio_question)
            file_name_tag= str(question_attempt.id)+file_extension
            fs = FileSystemStorage() #defaults to   MEDIA_ROOT
            if answer == None:
                filename = None
            else:
                filename = fs.save("audio_exam_recordings/"+str(question_attempt.id)+file_extension, answer)
                file_url = fs.url(filename)

            question_attempt.answer.name = filename
            question_attempt.save()

            attempt.audio_question_attempts.add(question_attempt)
        attempt.save()
        data["status"] = True
    # else:
    #     data["status"] = False
    return JsonResponse(data)


def agency_audio_result(request, id, job_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=request.user.id)
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    audio_exam_template = AgencyModels.AudioExamTemplate.objects.get(template=template_obj)
    audio_question_paper = AgencyModels.AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    current_site = get_current_site(request)
    attempt = models.AgencyAudioExamAttempt.objects.get(candidate_id=request.user,
                                                         agency_id=audio_question_paper.agency_id,
                                                         audio_question_paper=audio_question_paper, job_id=job_obj)
    print("==========================",attempt.audio_question_attempts.all())
    get_result = {'total_question':len(attempt.audio_question_attempts.all())}
    ans_count=0
    noans_count=0
    for result in attempt.audio_question_attempts.all():
        if result.answer:
            ans_count+=1
        else:
            noans_count+=1
    get_result['answered']=ans_count
    get_result['not_answered']=noans_count
    obain_time = 0
    total_que = 0
    ans_que = 0
    no_ans_que = 0
    for i in attempt.audio_question_attempts.all():
        if i.answer != '':
            ans_que += 1
        else :
            no_ans_que += 1
        total_que += 1

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
    #                                                             'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    notify.send(request.user, recipient=request.user, verb="Manual",
                            description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id))
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id==str(id)+str(job_id)+str(request.user.id):
            print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
            Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
    return render(request, 'candidate/ATS/agency/audio_end_exam.html', {'get_result': 'getresult','job_id':job_id})

def agency_end_audio(template_id, job_id,loginuser_id):
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    audio_exam_template = AgencyModels.AudioExamTemplate.objects.get(template=template_obj)
    audio_question_paper = AgencyModels.AudioQuestionPaper.objects.get(exam_template=audio_exam_template)
    attempt = models.AgencyAudioExamAttempt.objects.get(candidate_id=user_obj,
                                                         agency_id=audio_question_paper.agency_id,
                                                         audio_question_paper=audio_question_paper, job_id=job_obj)
    print("==========================",attempt.audio_question_attempts.all())
    get_result = {'total_question':len(attempt.audio_question_attempts.all())}
    ans_count=0
    noans_count=0
    for result in attempt.audio_question_attempts.all():
        if result.answer:
            ans_count+=1
        else:
            noans_count+=1
    get_result['answered']=ans_count
    get_result['not_answered']=noans_count
    obain_time = 0
    total_que = 0
    ans_que = 0
    no_ans_que = 0
    for i in attempt.audio_question_attempts.all():
        if i.answer != '':
            ans_que += 1
        else :
            no_ans_que += 1
        total_que += 1

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.action_performed = False
    stage_status.assessment_done = False
    stage_status.save()
    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
    #                                                             'action_required':'Assessment by Company','update_at':datetime.datetime.now()})


# coding exam==========================================agency

import requests


def agency_coding_test(request,id, job_id):
    template_obj = AgencyModels.Template_creation.objects.get(id=id)
    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=request.user, job_id__id=job_id)
    if stage_status.status == 1:
        exam_obj = AgencyModels.CodingExamConfiguration.objects.get(template_id=template_obj)

        no_of_questions = int(exam_obj.total_question)
        question_obj = AgencyModels.CodingExamQuestions.objects.filter(coding_exam_config_id=exam_obj)
        questions = []
        for que in question_obj:
            dict = {'id':que.id,'title':que.question_id.coding_que_title,'description':que.question_id.coding_que_description}
            questions.append(dict)
        question_no_iterator = [i for i in range(no_of_questions)]
        time = exam_obj.total_time.split(':')
        if models.Agency_ExamTimeStatus.objects.filter(candidate_id=request.user,template=template_obj,job_id__id=job_id).exists():
            start_time = models.Agency_ExamTimeStatus.objects.get(candidate_id=request.user,template=template_obj,job_id__id=job_id).start_time
            current_time = datetime.datetime.now(timezone.utc)

            diff = current_time - start_time
            seconds = int(diff.total_seconds())

            total_hour_in_second = int(time[0]) * 3600
            total_min_in_second = int(time[1]) * 60
            total_available_seconds = (total_hour_in_second + total_min_in_second) - seconds
            available_minutes = int(total_available_seconds/60)
            available_seconds = int(total_available_seconds % 60)
        else:
            available_minutes = int(time[0]) * 60 + int(time[1])
            available_seconds = 0
            models.Agency_ExamTimeStatus.objects.create(candidate_id=request.user,template=template_obj,
                                                 job_id=AgencyModels.JobCreation.objects.get(id=job_id),start_time=datetime.datetime.now(timezone.utc))
            start_time = datetime.datetime.now(timezone.utc)
            time_zone = pytz.timezone("Asia/Calcutta")
            schedule_date=datetime.datetime.now(timezone.utc)
            duration=datetime.datetime.strptime(str(exam_obj.total_time), '%H:%M').time()
            A= datetime.timedelta(hours = duration.hour,minutes = duration.minute)
            totalsecond = A.total_seconds()
            schedule_end_mcq = start_time + datetime.timedelta(seconds=totalsecond)
            schedule_end_mcq = schedule_end_mcq.astimezone(pytz.utc)
            print('end mcq===========================',schedule_end_mcq)
            getjob=Scheduler.get_jobs()
            for job in getjob:
                if job.id==str(id)+str(job_id)+str(request.user.id):
                    print(job.id,'=====',str(id)+str(job_id)+str(request.user.id))
                    Scheduler.remove_job(str(id)+str(job_id)+str(request.user.id))
            if exam_obj.technology == 'backend':
                Scheduler.add_job(
                                agency_end_backend_coding,
                                trigger=DateTrigger(run_date=schedule_end_mcq),
                                args = [id,job_id,request.user.id],
                                misfire_grace_time=6000,
                                id=str(id)+str(job_id)+str(request.user.id)
                                # replace_existing=True
                            )   
            else:
                Scheduler.add_job(
                        agency_end_frontend_coding,
                        trigger=DateTrigger(run_date=schedule_end_mcq),
                        args = [id,job_id,request.user.id],
                        misfire_grace_time=6000,
                        id=str(id)+str(job_id)+str(request.user.id)
                        # replace_existing=True
                    )                              
        if request.method == 'POST':
            language = exam_obj.coding_subject_id.api_subject_id.name
            data = json.loads(request.body.decode('UTF-8'))
            url = 'https://glot.io/api/run/'+ language +'/latest'
            payload = json.dumps(data)
            print("payload",payload)
            headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8',
                       'Authorization': 'Token 6f18027a-2ea7-40cf-8b7b-4b91b49fda0a','contentType ':'application/json'}
            r = requests.post(url, data=payload, headers=headers)
            return HttpResponse(r)
        if exam_obj.technology == 'backend':
            language = exam_obj.coding_subject_id.api_subject_id.name
            return render(request, 'candidate/ATS/agency/back_end_editor.html', {'id': id, 'job_id': job_id,
                                                                          'available_minutes':available_minutes,
                                                                          'available_seconds':available_seconds,
                                                                          'language': language,
                                                                          'stage_id':stage_status.id,
                                                                          'no_of_questions': no_of_questions,
                                                                          'question_no_iterator': question_no_iterator,
                                                                          'coding_questions': json.dumps(questions)})
        else:
            return render(request, 'candidate/ATS/agency/frontend_editor.html', {'id': id, 'job_id': job_id,
                                                                          'available_minutes': available_minutes,
                                                                          'available_seconds': available_seconds,
                                                                          'stage_id':stage_status.id,
                                                                          'no_of_questions': no_of_questions,
                                                                          'question_no_iterator': question_no_iterator,
                                                                          'coding_questions': json.dumps(questions)})
    else:
        return HttpResponse(False)


def agency_preview(request):
    return render(request,'candidate/ATS/agency/preview.html')


def agency_save_front_end_code(request,template_id,job_id):
    if request.method == 'POST':
        user_obj = User.objects.get(id=request.user.id)
        template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        data = json.loads(request.body.decode('UTF-8'))

        question_not_attempted_count = 0
        total_question = 0
        print("\n\n================",data)
        for (que_id, html, css, js) in zip_longest(data['que_list'], data['html_codes'],
                                                              data['css_codes'], data['js_codes'],fillvalue=None):
            print('\n\n\ndata>>>>>>>>>>', que_id,'\n\n\n',html,'\n\n\n',css,'\n\n\n',js,'\n============================')
            coding_exam_que = AgencyModels.CodingExamQuestions.objects.get(id=que_id)
            if html and css and js == '':
                question_not_attempted_count += 1
            models.AgencyCodingFrontEndExamFill.objects.update_or_create(candidate_id=user_obj,agency_id=template_obj.agency_id,
                                                            template=template_obj,job_id=job_obj,
                                                            exam_question_id=coding_exam_que,
                                                            defaults={'html_code':html,'css_code':css,'js_code':js})
            total_question += 1

        models.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=user_obj, agency_id=template_obj.agency_id,
                                                           template=template_obj, job_id=job_obj,
                                                           defaults={'total_question': total_question,
                                                                     'answered': total_question - question_not_attempted_count})

        stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                            job_id=job_obj)
        stage_status.status = 2
        stage_status.save()
        # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
        #                                                         'action_required':'Assessment by Company','update_at':datetime.datetime.now()})
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"
        notify.send(request.user, recipient=request.user, verb="Manual",
                                description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+'/agency')
        getjob=Scheduler.get_jobs()
        for job in getjob:
            if job.id==str(template_id)+str(job_id)+str(request.user.id):
                print(job.id,'=====',str(template_id)+str(job_id)+str(request.user.id))
                Scheduler.remove_job(str(template_id)+str(job_id)+str(request.user.id))
        return HttpResponse(True)


def agency_save_code(request,template_id,job_id):
    if request.method == 'POST':
        user_obj = User.objects.get(id=request.user.id)
        template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
        job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
        data = json.loads(request.body.decode('UTF-8'))
        print("\n\ndata files ==>>", data['files'])
        question_not_attempted_count = 0
        total_question = 0
        for que in data['files']:
            coding_exam_que = AgencyModels.CodingExamQuestions.objects.get(id=que['que_id'])
            if que['content'] == 'The candidate did not attempt this question':
                question_not_attempted_count += 1
            models.AgencyCodingBackEndExamFill.objects.update_or_create(candidate_id=user_obj,agency_id=template_obj.agency_id,
                                                        template=template_obj,job_id=job_obj,
                                                        exam_question_id=coding_exam_que,defaults={'source_code':que['content']})
            total_question += 1
        models.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=user_obj,agency_id=template_obj.agency_id,
                                                        template=template_obj,job_id=job_obj,
                                                      defaults={'total_question':total_question,'answered':total_question-question_not_attempted_count})

        stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                            job_id=job_obj)
        stage_status.status = 2
        stage_status.save()
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"
        notify.send(request.user, recipient=request.user, verb="Manual",
                                description="Thank you for submitting your interview, please wait for results.",image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+'/agency')
        getjob=Scheduler.get_jobs()
        for job in getjob:
            if job.id==str(template_id)+str(job_id)+str(request.user.id):
                print(job.id,'=====',str(template_id)+str(job_id)+str(request.user.id))
                Scheduler.remove_job(str(template_id)+str(job_id)+str(request.user.id))
        return HttpResponse(True)
    return render(request, 'candidate/ATS/agency/back_end_editor.html')

def agency_end_backend_coding(template_id, job_id,loginuser_id):
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    question_not_attempted_count = 0
    total_question = 0
    models.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=user_obj,agency_id=template_obj.agency_id,
                                                    template=template_obj,job_id=job_obj,
                                                    defaults={'total_question':total_question,'answered':total_question-question_not_attempted_count})

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.save()

def agency_end_frontend_coding(template_id, job_id,loginuser_id):
    user_obj = User.objects.get(id=loginuser_id)
    template_obj = AgencyModels.Template_creation.objects.get(id=template_id)
    job_obj = AgencyModels.JobCreation.objects.get(id=job_id)
    question_not_attempted_count = 0
    total_question = 0
    models.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=user_obj, agency_id=template_obj.agency_id,
                                                        template=template_obj, job_id=job_obj,
                                                        defaults={'total_question': total_question,
                                                                    'answered': total_question - question_not_attempted_count})

    stage_status = AgencyModels.CandidateJobStagesStatus.objects.get(template=template_obj, candidate_id=user_obj,
                                                        job_id=job_obj)
    stage_status.status = 2
    stage_status.save()
    # Tracker.objects.update_or_create(job_id=job_obj,candidate_id=user_obj,company_id=stage_status.company_id,defaults={
    #                                                         'action_required':'Assessment by Company','update_at':datetime.datetime.now()})


def notification_list(request):
    return render(request,"candidate/ATS/notification_list.html")





@login_required(login_url="/")
def candidate_profile_settings(request):
    if request.user.is_candidate:
        context = {}
        if models.CandidateSEO.objects.filter(candidate_id=request.user.id).exists():
            context['seo'] = models.CandidateSEO.objects.filter(candidate_id=request.user.id)[0]
        current_user = models.CandidateProfile.objects.filter(candidate_id=request.user.id).first()
        get_all_profile = models.CandidateProfile.objects.filter(candidate_id=request.user.id)
        get_profile_list = [i.profile_id.id for i in get_all_profile]
        models.Profile.objects.filter(candidate_id=request.user.id).exclude(id__in=get_profile_list).delete()
        referral_list = models.ReferralDetails.objects.filter(referred_by=User.objects.get(id=request.user.id))
        count = 0
        profiles = models.Profile.objects.filter(candidate_id=request.user.id)
        profile_count = len(profiles)
        for i in profiles:
            if i.active == True:
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",i.id)
                request.session['active_profile_id'] = i.id
                context['active_profile_hide_fields'] = models.Candidate_Hide_Fields.objects.get(
                    candidate_id=request.user, profile_id=i)
                context['active_profile'] = i
                context['userdata'] = models.CandidateProfile.objects.get(candidate_id=request.user, profile_id=i)
                break
        for i in referral_list:
            if i.referred_to.is_active:
                count += 1
       
        context['profile'] = current_user
        context['get_all_profile'] = get_all_profile
        context['referral_list'] = referral_list
        context['count'] = count
        context['profiles'] = profiles
        context['profile_count'] = profile_count

        context['applied_job'] = AppliedCandidate.objects.filter(candidate=User.objects.get(id=request.user.id))
        print(request.user.id)
        context['applied_agency_job'] = AssociateCandidateAgency.objects.filter(candidate_id=User.objects.get(id=request.user.id))
        
        print('\\\\\\\\\\\\\\\\\\\\',context['applied_agency_job'])
    else:
        return redirect('accounts:user_logout')
    return render(request, 'candidate/ATS/candidate_profile_settings.html', context)


def verify_detail(request,applicantid):
    context={}
    context = {'notice_period': models.NoticePeriod.objects.all()}
    context['verifydetail']=AgencyModels.DailySubmission.objects.get(id=applicantid)
    if request.method=='POST':
        fname = request.POST.get('f-name')
        lname = request.POST.get('l-name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        # resume = request.FILES.get('resume')
        # if resume == None:
        #     if edit_internal_candidate:
        #         resume = edit_internal_candidate.resume
        contact = request.POST.get('contact-num')
        employee_id = request.POST.get('candidate_c_id')
        designation = request.POST.get('designation-input')
        notice = models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
        current_city = models.City.objects.get(id=request.POST.get('candidate_current_city'))
        ctc = request.POST.get('ctc-input')
        expectedctc = request.POST.get('expected-ctc')
        total_exper = request.POST.get('professional-experience-year') +'.'+ request.POST.get(
            'professional-experience-month')
        # source=CandidateModels.Source.objects.get(id=request.POST.get('source'))

        
        updatedetail= AgencyModels.DailySubmission.objects.get(id=applicantid)
        updatedetail.email=email
        updatedetail.first_name = fname
        updatedetail.last_name = lname
        updatedetail.gender = gender
            # 'resume' : resume,
        updatedetail.contact = contact
        updatedetail.designation = designation
        updatedetail.notice = notice
        updatedetail.ctc = ctc
        updatedetail.current_city = current_city
            # 'secure_resume':secure_resume,
        updatedetail.expectedctc = expectedctc
        updatedetail.total_exper = total_exper
        updatedetail.update_at = datetime.datetime.now()
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                updatedetail.skills.add(main_skill_obj)
            else:
                main_skill_obj=models.Skill.objects.create(name=i)
                updatedetail.skills.add(main_skill_obj)
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                updatedetail.prefered_city.add(main_city_obj)
        updatedetail.verified=True
        updatedetail.save()
        internaldetailupdate=AgencyModels.InternalCandidateBasicDetail.objects.get(id=updatedetail.internal_candidate_id.id)
        internaldetailupdate.email=email
        internaldetailupdate.first_name = fname
        internaldetailupdate.last_name = lname
        internaldetailupdate.gender = gender
        # internaldetailupdate.resume = resume
        internaldetailupdate.contact = contact
        internaldetailupdate.designation = designation
        internaldetailupdate.notice = notice
        internaldetailupdate.ctc = ctc
        internaldetailupdate.current_city = current_city
        # internaldetailupdate.secure_resume = secure_resume
        internaldetailupdate.expectedctc = expectedctc
        internaldetailupdate.total_exper = total_exper
        internaldetailupdate.update_at = datetime.datetime.now()
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                internaldetailupdate.skills.add(main_skill_obj)
            else:
                main_skill_obj=models.Skill.objects.create(name=i)
                internaldetailupdate.skills.add(main_skill_obj)
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                internaldetailupdate.prefered_city.add(main_city_obj)
        internaldetailupdate.save()

    return render(request,'candidate/ATS/verify_detail.html',context)


def candidate_verify(request,applicantid):
    context={}
    context = {'notice_period': models.NoticePeriod.objects.all()}
    context['verifydetail']=DailySubmission.objects.get(id=applicantid)
    if request.method=='POST':
        fname = request.POST.get('f-name')
        lname = request.POST.get('l-name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        # resume = request.FILES.get('resume')
        # if resume == None:
        #     if edit_internal_candidate:
        #         resume = edit_internal_candidate.resume
        contact = request.POST.get('contact-num')
        employee_id = request.POST.get('candidate_c_id')
        designation = request.POST.get('designation-input')
        notice = models.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
        current_city = models.City.objects.get(id=request.POST.get('candidate_current_city'))
        ctc = request.POST.get('ctc-input')
        expectedctc = request.POST.get('expected-ctc')
        total_exper = request.POST.get('professional-experience-year') +'.'+ request.POST.get(
            'professional-experience-month')
        # source=CandidateModels.Source.objects.get(id=request.POST.get('source'))

        
        updatedetail= DailySubmission.objects.get(id=applicantid)
        updatedetail.email=email
        updatedetail.first_name = fname
        updatedetail.last_name = lname
        updatedetail.gender = gender
            # 'resume' : resume,
        updatedetail.contact = contact
        updatedetail.designation = designation
        updatedetail.notice = notice
        updatedetail.ctc = ctc
        updatedetail.current_city = current_city
            # 'secure_resume':secure_resume,
        updatedetail.expectedctc = expectedctc
        updatedetail.total_exper = total_exper
        updatedetail.update_at = datetime.datetime.now()
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                updatedetail.skills.add(main_skill_obj)
            else:
                main_skill_obj=models.Skill.objects.create(name=i)
                updatedetail.skills.add(main_skill_obj)
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                updatedetail.prefered_city.add(main_city_obj)
        updatedetail.verified=True
        updatedetail.applied=True
        updatedetail.save()
        internaldetailupdate=InternalCandidateBasicDetails.objects.get(id=updatedetail.internal_candidate_id_company.id)
        internaldetailupdate.email=email
        internaldetailupdate.first_name = fname
        internaldetailupdate.last_name = lname
        internaldetailupdate.gender = gender
        # internaldetailupdate.resume = resume
        internaldetailupdate.contact = contact
        internaldetailupdate.designation = designation
        internaldetailupdate.notice = notice
        internaldetailupdate.ctc = ctc
        internaldetailupdate.current_city = current_city
        # internaldetailupdate.secure_resume = secure_resume
        internaldetailupdate.expectedctc = expectedctc
        internaldetailupdate.total_exper = total_exper
        internaldetailupdate.update_at = datetime.datetime.now()
        for i in request.POST.getlist('professional_skills'):
            if i.isnumeric():
                main_skill_obj = models.Skill.objects.get(id=i)
                internaldetailupdate.skills.add(main_skill_obj)
            else:
                main_skill_obj=models.Skill.objects.create(name=i)
                internaldetailupdate.skills.add(main_skill_obj)
        for i in request.POST.getlist('candidate_search_city'):
            if i.isnumeric():
                main_city_obj = models.City.objects.get(id=i)
                internaldetailupdate.prefered_city.add(main_city_obj)
        internaldetailupdate.save()
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"  
        job_obj=JobCreation.objects.get(id=updatedetail.company_job_id.id)
        notify.send(request.user, recipient=User.objects.get(email=email.lower()), verb="Application",
                    description="You have succesfully applied for the Job "+str(job_obj.job_title)+".",image="/static/notifications/icon/company/Job_Create.png",
                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                        job_obj.id)+"/company")
        # fit_score(add_candidate,job_obj)
        # agencyid= models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
        AssociateCandidateInternal.objects.update_or_create(company_id=job_obj.company_id,job_id=job_obj,candidate_id=User.objects.get(email=email.lower()),defaults={
                'internal_candidate_id':InternalCandidateBasicDetails.objects.get(id=internaldetailupdate.id)
            })
        AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,dailysubmission=updatedetail,job_id=job_obj,candidate=User.objects.get(email=email.lower()),defaults={
        'user_id':User.objects.get(id=request.user.id),'submit_type':'Company'
        })
        workflow = JobWorkflow.objects.get(job_id=job_obj)
        currentcompleted=False
        current_stage=None
        next_stage = None
        next_stage_sequance=0
        # onthego change
        if workflow.withworkflow:
            print("==========================withworkflow================================")
            workflow_stages = WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
            if workflow.is_application_review:
                print("==========================is_application_review================================")
                print('\n\n is_application_review')
                for stage in workflow_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        sequence_number = stage.sequence_number
                    elif stage.sequence_number == 2:
                        print("==========================Application Review================================")
                        status = 1
                        stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                        current_stage = stage_list_obj
                        next_stage_sequance=stage.sequence_number+1
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                job_id=job_obj, stage=stage_list_obj,
                                                                sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                        sequence_number = stage.sequence_number + 1
                        status = 0
                    else:
                        status = 0
                        sequence_number = stage.sequence_number + 1
                        next_stage = stage.stage
                    CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                            candidate_id=User.objects.get(email=email.lower()),
                                                            job_id=job_obj, stage=stage.stage,
                                                            template=stage.template,
                                                            sequence_number=sequence_number,status=status,custom_stage_name=stage.stage_name)
            else:
                for stage in workflow_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        current_stage = stage.stage
                    elif stage.sequence_number == 2:
                        status = 1
                        next_stage = stage.stage
                        notify.send(request.user, recipient=User.objects.get(email=email.lower()), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                    else:
                        status = 0
                    CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                            candidate_id=User.objects.get(email=email.lower()),
                                                            job_id=job_obj, stage=stage.stage,
                                                            template=stage.template,
                                                            sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
        if workflow.onthego:
            print("==========================onthego================================")
            onthego_stages = OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

            if workflow.is_application_review:
                for stage in onthego_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        sequence_number = stage.sequence_number
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                        status = 1
                        sequence_number = stage.sequence_number + 1
                        stage_list_obj = models.Stage_list.objects.get(name="Application Review")
                        current_stage = stage_list_obj
                        next_stage_sequance=stage.sequence_number+1
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                job_id=job_obj, stage=stage_list_obj,
                                                                sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                    else:
                        status = 0
                        sequence_number = stage.sequence_number + 1
                        current_stage = stage_list_obj
                        CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                job_id=job_obj, stage=stage.stage,
                                                                template=stage.template,
                                                                sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)
            else:
                for stage in onthego_stages:
                    if stage.sequence_number == 1:
                        status = 2
                        current_stage = stage.stage
                    elif stage.sequence_number == 2:
                        status = 1
                        next_stage = stage.stage
                        notify.send(request.user, recipient=User.objects.get(email=email.lower()), verb="Interview Round",
                            description="Please start your interview round : "+stage.stage_name,image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_obj.id)+"/company")
                    else:
                        status = 0
                    CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                            candidate_id=User.objects.get(email=email.lower()),
                                                            job_id=job_obj, stage=stage.stage,
                                                            template=stage.template,
                                                            sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
        action_required=''
        if next_stage_sequance!=0:
            if CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                            candidate_id=User.objects.get(email=email.lower()),
                                                            job_id=job_obj,
                                                            sequence_number=next_stage_sequance).exists():
                next_stage=CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
                                                            candidate_id=User.objects.get(email=email.lower()),
                                                            job_id=job_obj,
                                                            sequence_number=next_stage_sequance).stage
        if not current_stage==None:
            if current_stage.name=='Interview':
                action_required = 'By Company/Agency'
            elif current_stage.name == 'Application Review':
                print('===========================onthe go action required')
                action_required='By Company'
            else:
                action_required='By Candidate'
        if current_stage!='':
            print("==========================Tracker================================")
            Tracker.objects.update_or_create(job_id=job_obj,candidate_id=User.objects.get(email=email.lower()),company_id=job_obj.company_id,defaults={
                                                    'current_stage':current_stage,'next_stage':next_stage,
                                                    'action_required':action_required,'update_at':datetime.datetime.now()})
        assign_job_internal = list(
            CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
                                            company_id=job_obj.company_id).values_list(
                'recruiter_id', flat=True))
        assign_job_internal.append(job_obj.job_owner.id)
        assign_job_internal.append(job_obj.contact_name.id)
        assign_job_internal = list(set(assign_job_internal))
        title = job_obj.job_title
        chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(email=email.lower()).id, title=title,candidate_id=User.objects.get(email=email.lower()))
        print(assign_job_internal)
        ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(email=email.lower()).id)
        for i in assign_job_internal:
            ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
        ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
        # Notification
        candidate=User.objects.get(email=email.lower())
        job_assign_recruiter = CompanyAssignJob.objects.filter(job_id=job_obj)
        description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
        to_email=[]
        to_email.append(job_obj.contact_name.email)
        to_email.append(job_obj.job_owner.email)
        if job_obj.contact_name.id != request.user.id:
            notify.send(User.objects.get(email=email.lower()), recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission",
                                                                        description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                            job_obj.id))
        if job_obj.job_owner.id != request.user.id:
            notify.send(User.objects.get(email=email.lower()), recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission",
                                                                        description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                            job_obj.id))
        all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        for i in all_assign_users:
            if i.recruiter_type_internal:
                to_email.append(i.recruiter_id.email)
                if i.recruiter_id.id != User.objects.get(email=email.lower()):
                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
                                                                        description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                            job_obj.id))
        all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        stage_detail=''
        if not current_stage==None:
            if current_stage.name == 'Interview':
                stage_detail='Interview'
                description="Please schedule time for interview with Candiate "+candidate.first_name +" "+candidate.last_name+" for Job "+job_obj.job_title
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        if i.recruiter_id.id != request.user.id:
                            notify.send(User.objects.get(email=email.lower()), recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview schedule",
                                                                                description=description,image="/static/notifications/icon/company/interview.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
            elif current_stage.name=='Application Review':
                stage_detail='Application Review'
                description="You have one application to review for the job "+job_obj.job_title
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        if i.recruiter_id.id != request.user.id:
                            notify.send(User.objects.get(email=email.lower()), recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
                                                                                description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
        to_email=list(set(to_email))
        mail_subject = "New Candidate submission"
        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"New candidate has been submitted by "+request.user.first_name+" "+request.user.last_name+" – <a href="+header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(job_obj.id)+" >Applicant profile link.</a> Please login to review"})
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
        msg.attach_alternative(html_content, "text/html")
        # try:
        msg.send()
    return render(request,'candidate/ATS/verify_detail.html',context)