import http
from django.contrib.auth.forms import PasswordResetForm
from bidcruit import settings
import re
from django.contrib.sites.shortcuts import get_current_site
import json
import base64
import random
from datetime import datetime
from django.contrib import messages
from dateutil.relativedelta import relativedelta
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from accounts.tokens import account_activation_token
from django.core.mail import EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
import pandas as pd
import candidate
from . import models
from candidate import models as CandidateModels
import pyotp
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from elasticsearch_dsl import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from .documents import CandidateDocument
from django.utils.crypto import get_random_string
# from candidate.views import fit_score
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from accounts.models import LoginDetail
from chat.models import Messages
from notifications.signals import notify
from chat import models as ChatModels
User = get_user_model()
from rest_apscheduler.scheduler import Scheduler
from  apscheduler.triggers.date import DateTrigger
# FOR ADVANCED SEARCH
# from company.forms import CandidateForm

from accounts.views import activate_account_confirmation
from itertools import zip_longest
from django.core.signing import Signer, TimestampSigner
from django.core import serializers
from agency import models as AgencyModels
from django.http import HttpResponseRedirect
import random
import string
from smtplib import SMTPException
from itertools import chain
import pdfkit
from .companyfilters import JobFilter,CandidateFilter

# permission
def check_permission(request):
    emp=models.Employee.objects.get(employee_id=request.user)
    role_data=models.RolePermissions.objects.get(role=emp.role,company_id=models.Company.objects.get(user_id=request.user))
    return role_data.permission.order_by('permissionsmodel_id')

def check_profile(companyid):
    if models.CompanyProfile.objects.filter(company_id=companyid).exists():
        return True
    else:
        return False

@login_required(login_url="/")
def index(request):
    context = {}
    return render(request, 'company/index.html', context)

@login_required(login_url="/")
def dashbord(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        jobwise=[]
        candidatewise=[]
        context['total_active_job']=models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user),close_job=False).count()
        context['connection_request']=AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user),is_accepted=False,is_rejected=False).count()
        context['job_invitation']=AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user),is_accepted=False,is_rejected=False).count()
        context['interview']=AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user),is_accepted=False,is_rejected=False).count()
        context['hire']=AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user),is_accepted=False,is_rejected=False).count()
        context['job_offer']=AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user),is_accepted=False,is_rejected=False).count()
        context['total_applicants']=models.AppliedCandidate.objects.filter(company_id=models.Company.objects.get(user_id=request.user)).count()
        job_list=models.Tracker.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('job_id')[:5]
        print(job_list)
        for i in job_list:
            jobdetail={'job_id':i.job_id.id,'job_title':i.job_id.job_title,'company':i.job_id.company_id.company_id.company_name,'remote_job':i.job_id.remote_job,
                        'exp':i.job_id.experience_year_max,'opening_date':i.job_id.publish_at,'job_type':i.job_id.job_type.name}
            count = models.AppliedCandidate.objects.filter(job_id=i.job_id).count()
            jobdetail['qpplicant']=count
            if i.job_id.salary_as_per_market:
                jobdetail['salary_range']='As per market' 
            else:
                jobdetail['salary_range']=i.job_id.min_salary+' LAP to ' +i.job_id.max_salary+' LAP'
            jobdetail['candidates']=[]
            jobwise_tracker = models.Tracker.objects.filter(job_id=i.job_id,company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id))).order_by('-update_at')
            for job in jobwise_tracker:
                if models.JobOffer.objects.filter(job_id=job.job_id,candidate_id=job.candidate_id,is_accepted=True).exists():
                    pass
                else:
                    jobdetail['candidates'].append({'candidatefname':job.candidate_id.first_name,'candidatelname':job.candidate_id.last_name,'current':job.current_stage,'candidateid':job.candidate_id.id,
                                                    'next':job.next_stage,'action':job.action_required,'currentcompleted':job.currentcompleted,'reject':job.reject,'withdraw':job.withdraw})
            jobwise.append(jobdetail)
        context['job_tracker']=jobwise
        for i in jobwise:
            print("====",i)
        
        context['job_opening']=models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),is_publish=True).order_by('-publish_at')[:5]
        context['latest_10_candidates']=models.InternalCandidateBasicDetails.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id))).order_by('-create_at')[:10]
        return render(request, 'company/ATS/dashbord.html', context)
    else:
        return redirect('company:add_edit_profile')

def all_countries(request):
    country_list = []
    countries = CandidateModels.Country.objects.all()
    for i in countries:
        country_dict = {'id': i.id, 'country_name': i.country_name}
        country_list.append(country_dict)
    return JsonResponse(country_list, safe=False)


def all_states(request, country_id):
    country = CandidateModels.Country.objects.get(id=int(country_id))
    data_dict = {'id': country.id, 'country_name': country.country_name}
    states = CandidateModels.State.objects.filter(country_code=int(country_id))
    state_list = []
    for i in states:
        state_dict = {'id': i.id, 'name': i.state_name}
        state_list.append(state_dict)
    data_dict['states'] = state_list
    return JsonResponse([data_dict], safe=False)


def all_cities(request, state_id):
    state = CandidateModels.State.objects.get(id=int(state_id))
    data_dict = {'id': state.id, 'state_name': state.state_name}
    cities = CandidateModels.City.objects.filter(state_code=int(state_id))
    city_list = []
    for i in cities:
        city_dict = {'id': i.id, 'name': i.city_name}
        city_list.append(city_dict)
    data_dict['cities'] = city_list
    return JsonResponse([data_dict], safe=False)


def ragister(request):
    alert = {}
    if not request.user.is_authenticated:
        if request.method == 'POST':
            companyname = request.POST.get('company_name')
            website = request.POST.get('website')
            email = request.POST.get('email')
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
            if User.objects.filter(email=request.POST['email'].lower()).exists():
                alert['message'] = "email already exists"
            else:
                usr = User.objects.create_company(email=email.lower(), company_name=companyname, website=website,
                                                  password=password, ip=ip, device_type=device_type,
                                                  browser_type=browser_type,
                                                  browser_version=browser_version, os_type=os_type,
                                                  os_version=os_version)
                try:
                    mail_subject = '"Activate your account" from Bidcruit'
                    current_site = get_current_site(request)
                    html_content = render_to_string('accounts/acc_active_email.html', {'user': usr,
                                                                                       'name': companyname,
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
                    company_create = models.Company.objects.create(company_id=User.objects.get(email=email.lower()))
                    company_create.user_id.add(User.objects.get(email=email.lower()))
                    company_create.save()
                    departmentcreate = models.Department.objects.create(name='Admin',system_generated = True, status=True, company_id=company_create,
                                                                        user_id=usr)
                    models.CandidateCategories.objects.create(category_name='Unassigned',company_id=models.Company.objects.get(user_id=User.objects.get(email=email.lower())),user_id=User.objects.get(email=email.lower()))
                    role_create = models.Role.objects.create(name='SuperAdmin',system_generated = True, status=True, company_id=company_create,
                                                             user_id=usr)
                    permissions = models.RolePermissions.objects.create(role=role_create,system_generated = True, company_id=company_create,
                                                                        user_id=usr)
                    get_permissionmodel=CandidateModels.PermissionsModel.objects.filter(is_company=True).values_list('id')
                    for per_id in CandidateModels.Permissions.objects.filter(permissionsmodel__in=get_permissionmodel):
                        permissions.permission.add(per_id)
                    models.Employee.objects.create(department=departmentcreate, role=role_create, employee_id=usr,
                                                   company_id=company_create, user_id=usr,unique_id=create_employee_id())

                    # coding question bank
                    api_subjects = CandidateModels.CodingApiSubjects.objects.filter(status=True)
                    for subject in api_subjects:
                        created_sub = models.CodingSubject.objects.create(company_id=company_create,api_subject_id=subject,type='backend')
                        models.CodingSubjectCategory.objects.create(company_id=company_create,subject_id=created_sub,category_name=subject.name)

                    front_sub = models.CodingSubject.objects.create(company_id=company_create,type='frontend')
                    models.CodingSubjectCategory.objects.create(company_id=company_create, subject_id=front_sub,
                                                                category_name='Html/css/js')
                except BadHeaderError:
                    ins = User.objects.get(email__exact=email).delete()
                    alert['message'] = "email not send"
                return activate_account_confirmation(request, companyname, email)
    else:
        if request.user.is_authenticated:
            if request.user.is_candidate:
                return redirect('candidate:home')
            if request.user.is_company:
                profile = models.CompanyProfile.objects.filter(company_id=request.user.id)
                if profile:
                    return redirect('company:company_profile')
                else:
                    return redirect('company:add_edit_profile')
    return render(request, 'company/companyregister.html', alert)


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
    return render(request, 'company/ATS/change-password.html', {
        'form': form
    })

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'company/company_login_email.html')
    else:
        return HttpResponse('Activation link is invalid!')


def generateOTP(request):
    totp = None
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, interval=300)
    one_time = totp.now()
    request.session['otp'] = one_time
    return one_time


def user_login_password(request):
    if request.method == 'POST':
        email = request.session['email']
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        user_id = User.objects.get(email=email.lower())
        request.session['user_id'] = user_id.id
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
        if user:
            if user.is_active:
                otp = generateOTP(request)
                LoginDetail.objects.create(user_id=User.objects.get(email=email.lower()), otp=otp, ip=ip,
                                           device_type=device_type, browser_type=browser_type,
                                           browser_version=browser_version, os_type=os_type,
                                           os_version=os_version)
                try:
                    mail_subject = 'OTP'
                    html_content = render_to_string('accounts/acc_otp_email.html', {'user': user,
                                                                                    'otp': otp})
                    to_email = email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except BadHeaderError:
                    print("email not send")
                return redirect('company:verify_otp')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'company/company_login.html')


def user_login_email(request):
    if request.method == 'POST':
        email = request.POST.get('emailaddress')
        request.session['email'] = email
        return redirect('company:user_login_password')
    return render(request, 'company/company_login_email.html')


def resend_otp(request):
    user = User.objects.get(id=request.session['user_id'])
    otp = generateOTP(request)
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
    LoginDetail.objects.create(company_id=User.objects.get(id=request.session['user_id']), otp=otp, ip=ip,
                               device_type=device_type, browser_type=browser_type,
                               browser_version=browser_version, os_type=os_type,
                               os_version=os_version)
    try:
        mail_subject = 'OTP'
        html_content = render_to_string('accounts/acc_otp_email.html', {'user': user,
                                                                        'otp': otp})
        to_email = user.email
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except BadHeaderError:
        print("email not send")
    return render(request, 'company/company_otp_verify.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        login_otp = LoginDetail.objects.filter(company_id=request.session['user_id']).order_by(
            '-create_at').first()
        if login_otp.otp == otp:
            user = User.objects.get(id=login_otp.company_id.id)
            login(request, user)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            chk_register_detail = models.User.objects.get(email=request.user.email)
            if ip != chk_register_detail.ip:
                mail_subject = 'Change Ip Notification'
                html_content = render_to_string('accounts/login_change_ip_email.html', {'user': user, })
                to_email = request.user.email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            return redirect('company:home')
        else:
            return HttpResponse(False)
    return render(request, 'company/company_otp_verify.html')


@login_required(login_url="/")
def user_logout(request):
    logout(request)
    return redirect('company:user_login_email')


def check_email_is_valid(request):
    email = request.POST.get("email")
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        user_obj = models.User.objects.filter(email=email.lower()).exists()
        if user_obj:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    else:
        return HttpResponse('Invalid')


def candidate_hire(request):
    if request.method == 'POST':
        print('hire_message', request.POST.get('hire_message'))
        candidate_id = User.objects.get(id=request.POST.get('candidate_id'))
        company_id = User.objects.get(id=request.user.id)
        active_profile = CandidateModels.Profile.objects.get(candidate_id=candidate_id, active=True)
        profile_id = CandidateModels.CandidateProfile.objects.get(candidate_id=candidate_id,
                                                                  profile_id=active_profile.id)

        models.CandidateHire.objects.create(title='None',
                                            message=request.POST.get('hire_message'),
                                            candidate_id=candidate_id, company_id=company_id, profile_id=active_profile)
        Messages.objects.create(description=request.POST.get('hire_message'), sender_name=company_id,
                                receiver_name=candidate_id)
        try:
            mail_subject = 'Company wants to Hire You'
            html_content = render_to_string('accounts/candidate_hire_email.html',
                                            {'message': request.POST.get('hire_message')})
            to_email = candidate_id.email
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return HttpResponse(True)
        except BadHeaderError:
            print("email not send")
            return HttpResponse(False)
    else:
        return HttpResponse('Invalid Request')

    # return render(request, 'company/candidate_hire.html',{'candidate_id':pk})


def company_login_direct(request):
    if request.method == 'POST':
        print('\n\ncalled company_login_email', request.POST.get('company_login_email'))
        print('\n\ncalled company_login_password', request.POST.get('company_login_password'))
    return HttpResponse(True)


def candidate_list_view(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        candidate_list = CandidateModels.CandidateProfile.objects.all().order_by('id')
        page = request.GET.get('page', 1)
        paginator = Paginator(candidate_list, 1)
        try:
            candidates = paginator.page(page)
        except PageNotAnInteger:
            candidates = paginator.page(1)
        except EmptyPage:
            candidates = paginator.page(paginator.num_pages)
        context['candidates']= candidates
        return render(request, 'company/candidate_list_view.html', context)
    else:
        return redirect('company:add_edit_profile')

def user_login_email_popup(request):
    data = json.loads(request.body.decode('UTF-8'))
    email = data['email']
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        user_obj = models.User.objects.filter(email=email.lower(), is_company=True).exists()
        if user_obj:
            print('\n\nuser_login_email_popup', data)
            request.session['company_email'] = data['email']
            request.session['login_type'] = data['type_name']
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    else:
        return HttpResponse(False)


def user_login_password_popup(request):
    data = json.loads(request.body.decode('UTF-8'))
    print('\n\nuser_login_password_popup', data)
    if request.method == 'POST':
        email = request.session['company_email']
        password = data['password']
        print("==================", email, password)
        user = authenticate(email=email, password=password)
        user_id = User.objects.get(email=email.lower())
        request.session['user_id'] = user_id.id
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
        if user:
            if user.is_active:
                otp = generateOTP(request)
                LoginDetail.objects.create(user_id=User.objects.get(email=email.lower()), otp=otp, ip=ip,
                                           device_type=device_type, browser_type=browser_type,
                                           browser_version=browser_version, os_type=os_type,
                                           os_version=os_version)
                try:
                    mail_subject = 'OTP'
                    html_content = render_to_string('accounts/acc_otp_email.html', {'user': user,
                                                                                    'otp': otp})
                    to_email = email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except BadHeaderError:
                    print("email not send")
                return HttpResponse(True)
            else:
                return HttpResponse("Your account is inactive.")
        else:
            print("Someone tried to login and failed.")
            return HttpResponse("Invalid login details given")
    else:
        return HttpResponse(False)


def user_login_verify_otp_popup(request):
    data = json.loads(request.body.decode('UTF-8'))
    if request.method == 'POST':
        otp = data['otp']
        login_otp = LoginDetail.objects.filter(user_id=request.session['user_id']).order_by(
            '-create_at').first()
        if login_otp.otp == otp:
            user = User.objects.get(id=login_otp.user_id.id)
            login(request, user)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            chk_register_detail = models.User.objects.get(email=request.user.email)
            print('----------=======', request.session['login_type'])
            if ip != chk_register_detail.ip:
                mail_subject = 'Change Ip Notification'
                html_content = render_to_string('accounts/login_change_ip_email.html', {'user': user, })
                to_email = request.user.email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            return HttpResponse(request.session['login_type'])
        else:
            return HttpResponse(False)
    else:
        return HttpResponse(False)


def candidate_preference_check(request):
    if request.user.is_company:
        if request.method == 'POST':
            company_id = User.objects.get(id=request.user.id)
            exclude_list = ['candidate_id', 'relocation_cities', 'id']
            print('-----------', request.POST.get('candidate_id'))
            candidate_id = User.objects.get(id=int(request.POST.get('candidate_id')))
            for i in CandidateModels.CandidateJobPreference._meta.get_fields():
                if i.name not in exclude_list:
                    print('\n\n', i.name)
                    print('', type(i.name))
                    if request.POST.get(i.name) == 'on':
                        models.CandidateSelectedPreference.objects.update_or_create(company_id=company_id,
                                                                                    candidate_id=candidate_id,
                                                                                    preference_name=i.name, defaults={
                                'is_selected': True, 'company_id': company_id, 'candidate_id': candidate_id,
                                'preference_name': i.name})
                    else:
                        models.CandidateSelectedPreference.objects.update_or_create(company_id=company_id,
                                                                                    candidate_id=candidate_id,
                                                                                    preference_name=i.name, defaults={
                                'is_selected': False, 'company_id': company_id, 'candidate_id': candidate_id,
                                'preference_name': i.name})
            # for i in CandidateModels.CandidateJobPreferenceOther.objects.filter(candidate_id=candidate_id):
            #     print('i',i)
            #     print('i',i.label)

            return HttpResponse(True)
    else:
        return HttpResponse(False)


def search(request):
    search_string = request.GET.get('candidate_search')
    search_city = request.GET.get('candidate_search_city')
    print(search_city)
    advanced_search_form = CandidateForm()
    users = []
    custom_queries = []
    print("search string", search_string)
    print("search city", search_city)

    if search_string:
        q = Q("multi_match", query=search_string, fields=['skills', 'job_titles'])
        print("search string appended")
        custom_queries.append(q)

    if search_city:
        city_name = CandidateModels.City.objects.get(id=int(search_city)).city_name
        q = Q("multi_match", query=city_name, fields=['current_city'])
        print("search city appended")
        custom_queries.append(q)
    if custom_queries:
        final_query = custom_queries[0]
        if len(custom_queries) >= 1:
            for i in range(1, len(custom_queries)):
                final_query = final_query & custom_queries[i]

        s = CandidateDocument.search().query(final_query).extra(size=10000)
        for hit in s:
            try:
                user = User.objects.get(email=hit.email)
                # for i in range(100):
                users.append(user.id)
            except:
                print("error")
    print(custom_queries)
    print(users)
    users = list(set(users))
    # if request.GET.get['getpage']==None:
    item = 10
    paginator = Paginator(users, item)
    # else:
    #     item=request.session['getpage']
    #     paginator = Paginator(users, int(item))
    page_number = request.GET.get("page", 1)
    try:
        candidate = paginator.page(page_number)

    except PageNotAnInteger:
        # If page parameter is not an integer, show first page.
        candidate = paginator.page(1)
    except EmptyPage:
        # If page parameter is out of range, show last existing page.
        candidate = paginator.page(paginator.num_pages)

    return render(request, 'company/search.html',
                  {'users': candidate, 'item': item, 'form': advanced_search_form, 'search_string': search_string,
                   'search_string_city': search_city})


def get_page_no(request):
    if request.method == 'POST':
        getpage = request.POST.get('item')
        request.session['getpage'] = getpage
        if request.session.get('data_set'):
            return redirect('company:advanced_search')
        return redirect('company:search_result')
    advanced_search_form = CandidateForm()
    return render(request, "company/candidatelistview.html", {'form': advanced_search_form})


def search_result(request):
    users = []
    try:
        search_string = request.session.get('search')
        print("search string is ------->", search_string)
        search_string_city = request.session.get('search_city')
        print("search string is ------->", search_string_city)
        print("search sting", search_string)
    except:
        pass
    if search_string != None or search_string_city != None:

        custom_queries = []
        if search_string != None:
            q = Q("multi_match", query=search_string, fields=['skills', 'job_titles'])
            print("search string appended")
            custom_queries.append(q)

        if search_string_city != None:
            city_name = CandidateModels.City.objects.get(id=int(search_string_city)).city_name
            q = Q("multi_match", query=city_name, fields=['current_city'])
            print("search city appended")
            custom_queries.append(q)

        final_query = custom_queries[0]
        if len(custom_queries) >= 1:
            for i in range(1, len(custom_queries)):
                final_query = final_query & custom_queries[i]

        page = request.GET.get('page', '1')
        s = CandidateDocument.search().query(final_query).extra(size=10000)
        for hit in s:
            try:
                user = User.objects.get(email=hit.email)
                users.append(user.id)
            except:
                pass
    users = list(set(users))
    if request.session['getpage'] == None:
        item = 20
        paginator = Paginator(users, item)
    else:
        item = request.session['getpage']
        paginator = Paginator(users, int(item))
    page_number = request.GET.get("page", 1)
    try:
        candidate = paginator.page(page_number)

    except PageNotAnInteger:
        # If page parameter is not an integer, show first page.
        candidate = paginator.page(1)
    except EmptyPage:
        # If page parameter is out of range, show last existing page.
        candidate = paginator.page(paginator.num_pages)
    if request.is_ajax():
        html = render_to_string('company/candidatelistview.html', {"users": candidate, 'search_string': search_string,
                                                                   'search_string_city': search_string_city})
        return HttpResponse(html)
    print('candidatecandidatecandidate---------', candidate)
    advanced_search_form = CandidateForm()
    return render(request, 'company/candidatelistview.html',
                  {"users": candidate, 'item': item, 'form': advanced_search_form, 'search_string': search_string,
                   'search_string_city': search_string_city})


def get_cities(request):
    # cities = City.objects.all()
    print("GET CITIES WAS CALLLLED")
    term = request.GET.get('term')
    cities = CandidateModels.City.objects.filter(city_name__istartswith=term)
    city_list = []
    for i in cities:
        data = {}
        data['id'] = i.id
        data['city_name'] = i.city_name
        data['state_name'] = i.state_code.state_name
        city_list.append(data)

    # print("citiesss",cities)
    return JsonResponse(city_list, safe=False)


def get_skills(request):
    print("\n\nget_skills WAS CALLLLED")
    term = request.GET.get('term')
    skills = CandidateModels.Skill.objects.filter(name__istartswith=term)
    skill_list = []
    for i in skills:
        data = {}
        data['id'] = i.id
        data['name'] = i.name
        skill_list.append(data)
    print("skills sent",skill_list)
    return JsonResponse(skill_list, safe=False)

def get_source(request):
    print("\n\nget_source WAS CALLLLED")
    term = request.GET.get('term')
    sources = CandidateModels.Source.objects.filter(name__istartswith=term)
    source_list = []
    for i in sources:
        data = {}
        data['id'] = i.id
        data['name'] = i.name
        source_list.append(data)
    print("skills sent",source_list)
    return JsonResponse(source_list, safe=False)

def get_tags(request):
    term = request.GET.get('term')
    tags = models.Tags.objects.filter(name__istartswith=term,company_id=models.Company.objects.get(user_id=request.user.id))
    tags_list = []
    for i in tags:
        data = {}
        data['id'] = i.id
        data['name'] = i.name
        tags_list.append(data)
    return JsonResponse(tags_list, safe=False)


def get_degrees(request):
    print("GET DEGREES WAS CALLLLLLLED")
    term = request.GET.get('term')
    degrees = CandidateModels.Degree.objects.filter(name__icontains=term)
    print("degreees", degrees)
    return JsonResponse(list(degrees.values()), safe=False)


def advanced_search(request):
    method = None
    custom_queries = []
    count = -1
    form = CandidateForm(request.GET)
    users = []
    advanced_search_form = CandidateForm(request.GET)
    notice_period = request.GET.get('notice_period')
    include_skills = request.GET.getlist('include_skills')
    exclude_skills = request.GET.getlist('exclude_skills')
    preferred_cities_id = request.GET.getlist('preferred_cities')
    current_city_id = request.GET.get('current_city')
    minimum_experience = request.GET.get('minimum_experience')
    maximum_experience = request.GET.get('maximum_experience')
    education_ids = request.GET.getlist('education')
    if request.GET.get('notice_period'):
        notice_period = CandidateModels.NoticePeriod.objects.get(id=request.GET.get('notice_period'))
    else:
        notice_period = CandidateModels.NoticePeriod.objects.get(id=1)
    current_city = ''
    if current_city_id:
        current_city = CandidateModels.City.objects.get(id=current_city_id).city_name

    if current_city:
        q = Q('multi_match', query=current_city, fields=['current_city'])
        custom_queries.append(q)
    preferred_cities = []
    for i in preferred_cities_id:
        preferred_cities.append(CandidateModels.City.objects.get(id=i).city_name)

    if len(preferred_cities):
        for i in preferred_cities:
            q = Q('multi_match', query=i, fields=['preferred_cities'])
            custom_queries.append(q)

    if len(include_skills):
        for i in include_skills:
            q = Q('multi_match', query=i, fields=['skills'])
            custom_queries.append(q)
    if len(exclude_skills):
        for i in exclude_skills:
            q = ~Q('multi_match', query=i, fields=['skills'])
            custom_queries.append(q)

    if minimum_experience == '':
        minimum_experience = 0
    else:
        minimum_experience = int(minimum_experience)

    if maximum_experience == '':
        maximum_experience = 99
    else:
        maximum_experience = int(maximum_experience)

    degrees = []

    for i in education_ids:
        try:
            i = int(i)
            print("INTEGER I ", i)
            degree = CandidateModels.Degree.objects.get(id=i).name
            degrees.append(degree)
        except:
            pass

    if len(degrees):
        for i in degrees:
            q = Q('multi_match', query=i, fields=['education_list'])
            custom_queries.append(q)

    length = len(custom_queries)
    final_query = ''
    print("custom_queries", custom_queries)
    if length:
        final_query = custom_queries[0]
        if length > 1:
            for i in range(1, length):
                final_query = final_query & custom_queries[i]

    print("final_query: ", final_query)

    if final_query == "":
        search_string = request.GET.get('candidate_search')
        search_city = request.GET.get('candidate_search_city')
        if search_string:
            q = Q("multi_match", query=search_string, fields=['skills', 'job_titles'])
            custom_queries.append(q)

        if custom_queries:
            final_query = custom_queries[0]
            if len(custom_queries) >= 1:
                for i in range(1, len(custom_queries)):
                    final_query = final_query & custom_queries[i]

            s = CandidateDocument.search().query(final_query).extra(size=10000)
            for hit in s:
                try:

                    user = User.objects.get(email=hit.email)
                    profile = CandidateModels.Profile.objects.get(candidate_id=user, active=True)
                    candidate_profile = CandidateModels.CandidateProfile.objects.get(candidate_id=user,
                                                                                     profile_id=profile)
                    if candidate_profile.notice_period == notice_period:
                        users.append(user.id)
                except:
                    print("error")
        else:
            profile = CandidateModels.Profile.objects.filter(active=True)
            for i in profile:
                print("the profile id is", i.id)
                candidate_profile = CandidateModels.CandidateProfile.objects.get(profile_id=i)
                if candidate_profile.notice_period == notice_period:
                    users.append(candidate_profile.candidate_id.id)


    else:
        s = CandidateDocument.search().query(final_query).extra(size=10000)
        print("candidate documebnt", s)
        count = 0
        for hit in s:
            print("HIT USER!!!!!")
            # try:
            user = User.objects.get(email=hit.email)
            profiles = CandidateModels.Profile.objects.filter(candidate_id=user, active=True)
            for i in profiles:
                print("prooooooooooooooofile", i)
            if profiles:
                profile = CandidateModels.Profile.objects.get(candidate_id=user, active=True)
                candidate_profile = CandidateModels.CandidateProfile.objects.get(candidate_id=user, profile_id=profile)
                if (candidate_profile.total_experience >= minimum_experience) and (
                        candidate_profile.total_experience <= maximum_experience):
                    if candidate_profile.notice_period == notice_period:
                        users.append(user.id)
                    count += 1
    item = 10
    paginator = Paginator(users, item)
    page_number = request.GET.get("page", 1)
    try:
        candidate = paginator.page(page_number)

    except PageNotAnInteger:
        # If page parameter is not an integer, show first page.
        candidate = paginator.page(1)
    except EmptyPage:
        # If page parameter is out of range, show last existing page.
        candidate = paginator.page(paginator.num_pages)

    if minimum_experience == 0:
        minimum_experience = ''
    if maximum_experience == 99:
        maximum_experience = ""
    education_choices = []
    for i in education_ids:
        education = CandidateModels.Degree.objects.get(id=i)
        education_choices.append((i, education.name))
    if current_city:
        city = CandidateModels.City.objects.get(id=current_city_id)
        current_city_choice = [(city.id, city.city_name)]
    else:
        current_city_choice = None

    preferred_cities = []
    if preferred_cities_id:
        for i in preferred_cities_id:
            city = CandidateModels.City.objects.get(id=i)
            preferred_cities.append((i, city.city_name))

    notice_period = (notice_period.id, notice_period.notice_period)
    advanced_search_form = CandidateForm(current_city=current_city_choice, minimum_experience=minimum_experience,
                                         maximum_experience=maximum_experience, education_choices=education_choices,
                                         preferred_cities=preferred_cities, include_skills=include_skills,
                                         exclude_skills=exclude_skills, notice_period=notice_period)
    return render(request, 'company/search.html', {"users": candidate, 'item': item, 'form': advanced_search_form})

def add_edit_profile(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    print(request.user)
    if request.user.is_company:

        context['country'] = CandidateModels.Country.objects.all()
        context['founded_years'] = [str(i) for i in range(1950, datetime.datetime.now().year + 1)]
        context['industrytype'] = CandidateModels.IndustryType.objects.all()
        context['employee_count_'] = models.CompanyProfile.employee_count_choices
        context['company_type_'] = models.CompanyProfile.company_type_choices
        context['admin_user']=models.Employee.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),employee_id=User.objects.get(id=request.user.id))
        context['departments'] = models.Department.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['role'] = models.Role.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        if request.method == 'POST':
            admin_update=User.objects.get(id=request.user.id)
            if not (admin_update.first_name or admin_update.last_name):
                models.Employee.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),defaults={
                                                        'employee_id':User.objects.get(id=request.user.id),
                                                        'first_name':request.POST.get('first_name'),
                                                        'last_name':request.POST.get('last_name'),
                                                        'role':models.Role.objects.get(id=request.POST.get('role')),
                                                        'department':models.Department.objects.get(id=request.POST.get('department')),
                                                        'contact_num':request.POST.get('user_contactno')
                                                                        })
            admin_update.first_name=request.POST.get('first_name')
            admin_update.last_name=request.POST.get('last_name')
            admin_update.save()
            models.CompanyProfile.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                           defaults={
                                                               'user_id':User.objects.get(id=request.user.id),
                                                               'contact_email':request.POST.get('contact-email'),
                                                               'universal_Name': request.POST.get('universal_name'),
                                                               'compnay_type': request.POST.get('company_type'),
                                                               'industry_type': CandidateModels.IndustryType.objects.get(
                                                                   id=request.POST.get('industrial_type')),
                                                               'company_logo': request.FILES.get('logo'),
                                                               'company_bg':request.FILES.get('bg'),
                                                               'speciality':  ', '.join(request.POST.getlist('specialties')),
                                                               'aboutus':request.POST.get('aboutus'),
                                                               'address': request.POST.get('address'),
                                                               'country': CandidateModels.Country.objects.get(
                                                                   id=request.POST.get('country')),
                                                               'state': CandidateModels.State.objects.get(
                                                                   id=request.POST.get('state')),
                                                               'city': CandidateModels.City.objects.get(
                                                                   id=request.POST.get('city')),
                                                               'zip_code': request.POST.get('zipcode'),
                                                               'contact_no1': request.POST.get('contactno1'),
                                                               'founded_year': request.POST.get('foundedyear'),
                                                               'employee_count': request.POST.get('employeecount')
                                                           })
            return redirect('company:company_profile')
    else:
        return redirect('accounts:user_logout')
    return render(request, 'company/add_profile.html', context)

def update_profile(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    context['country'] = CandidateModels.Country.objects.all()
    context['founded_years'] = [str(i) for i in range(1950, datetime.datetime.now().year + 1)]
    context['industrytype'] = CandidateModels.IndustryType.objects.all()
    context['employee_count_'] = models.CompanyProfile.employee_count_choices
    context['company_type_'] = models.CompanyProfile.company_type_choices
    if models.CompanyProfile.objects.filter(id=id,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
        context['profile_already_exists'] = models.CompanyProfile.objects.get(id=id,
            company_id=models.Company.objects.get(user_id=request.user.id))
    if request.method == 'POST':
        if request.FILES.get('logo'):
            logo= request.FILES.get('logo')
        else:
            logo =context['profile_already_exists'].company_logo
        if request.FILES.get('bg'):
            bg= request.FILES.get('bg')
        else:
            bg =context['profile_already_exists'].company_bg
        models.CompanyProfile.objects.update_or_create(id=id,company_id=models.Company.objects.get(user_id=request.user.id),
                                                       defaults={
                                                           'user_id': User.objects.get(id=request.user.id),
                                                           'contact_email': request.POST.get('contact-email'),
                                                           'universal_Name': request.POST.get('universal_name'),
                                                           'compnay_type': request.POST.get('company_type'),
                                                           'industry_type': CandidateModels.IndustryType.objects.get(
                                                               id=request.POST.get('industrial_type')),
                                                           'company_logo':logo,
                                                           'company_bg': bg,
                                                           'speciality': ', '.join(request.POST.getlist('specialties')),
                                                           'aboutus': request.POST.get('aboutus'),
                                                           'address': request.POST.get('address'),
                                                           'country': CandidateModels.Country.objects.get(
                                                               id=request.POST.get('country')),
                                                           'state': CandidateModels.State.objects.get(
                                                               id=request.POST.get('state')),
                                                           'city': CandidateModels.City.objects.get(
                                                               id=request.POST.get('city')),
                                                           'zip_code': request.POST.get('zipcode'),
                                                           'contact_no1': request.POST.get('contactno1'),
                                                           'founded_year': request.POST.get('foundedyear'),
                                                           'employee_count': request.POST.get('employeecount')
                                                       })
        return redirect('company:company_profile')
    return render(request, 'company/add_profile.html', context)
from django.db.models import Count, Sum


def hire_request(request):
    active = models.CandidateHire.objects.filter(company_id=request.user.id, request_status=1).values('message',
                                                                                                      'company_id',
                                                                                                      'candidate_id',
                                                                                                      'profile_id').annotate(
        cnt=Count('profile_id'))
    new_request = models.CandidateHire.objects.filter(company_id=request.user.id, request_status=0).values('message',
                                                                                                           'company_id',
                                                                                                           'candidate_id',
                                                                                                           'profile_id').annotate(
        cnt=Count('profile_id'))
    archive = models.CandidateHire.objects.filter(company_id=request.user.id, request_status=-1).values('message',
                                                                                                        'company_id',
                                                                                                        'candidate_id',
                                                                                                        'profile_id').annotate(
        cnt=Count('profile_id'))
    shortlisted_candidates = models.ShortlistedCandidates.objects.filter(company_id=request.user.id)
    print("^^^^^^^^^^^^++++++++++++++++++++", shortlisted_candidates)
    data_active = CandidateModels.company_data_request.objects.filter(company_id=request.user.id, status=1).values('id',
                                                                                                                   'message',
                                                                                                                   'company_id',
                                                                                                                   'candidate_id',
                                                                                                                   'profile_id')
    data_new_request = CandidateModels.company_data_request.objects.filter(company_id=request.user.id,
                                                                           status=-1).values('id', 'message',
                                                                                             'company_id',
                                                                                             'candidate_id',
                                                                                             'profile_id')
    data_archive = CandidateModels.company_data_request.objects.filter(company_id=request.user.id, status=-2).values(
        'id', 'message', 'company_id', 'candidate_id', 'profile_id')
    return render(request, 'company/request.html', {'active': active, 'new_request': new_request, 'archive': archive,
                                                    'shortlisted_candidates': shortlisted_candidates,
                                                    'data_active': data_active,
                                                    'data_new_request': data_new_request, 'data_archive': data_archive})


def accept_request(request, profile_id, company_id):
    if request.method == "POST":
        MessageModel.objects.create(user=User.objects.get(id=request.user.id),
                                    recipient=User.objects.get(id=candidate_id),
                                    body=request.POST.get('accept_message'), request_status=1)
        models.CandidateHire.objects.filter(company_id=request.user.id, candidate_id=candidate_id,
                                            profile_id=profile_id).update(request_status=1,
                                                                          message=request.POST.get('accept_message'))
    return redirect('company:hire_request')


def reject_request(request, profile_id, company_id):
    if request.method == "POST":
        MessageModel.objects.create(user=User.objects.get(id=request.user.id),
                                    recipient=User.objects.get(id=candidate_id),
                                    body=request.POST.get('reject_message'), request_status=-1)
        modelsCandidateHire.objects.filter(comapny_id=request.user.id, candidate_id=candidate_id_id,
                                           profile_id=profile_id).update(request_status=-1,
                                                                         message=request.POST.get('reject_message'))
    return redirect('company:hire_request')


def file_request(request):
    if request.is_ajax():
        company = User.objects.get(id=request.user.id)

        profile = CandidateModels.Profile.objects.get(id=request.GET.get('profile'), candidate_id_id=User.objects.get(
            id=int(request.GET.get('candidate'))))

        candidate = User.objects.get(id=int(request.GET.get('candidate')))
        print(candidate)
        if request.GET.get('s_type') == "Experience":
            CandidateModels.company_Hide_Fields_request.objects.update_or_create(company_id_id=company.id,
                                                                                 profile_id_id=profile.id,
                                                                                 candidate_id_id=candidate.id,
                                                                                 defaults={
                                                                                     'exp_document': -1,
                                                                                 })
        elif request.GET.get('s_type') == "Education":
            CandidateModels.company_Hide_Fields_request.objects.update_or_create(company_id_id=company.id,
                                                                                 profile_id_id=profile.id,
                                                                                 candidate_id_id=candidate.id,
                                                                                 defaults={
                                                                                     'edu_document': -1,
                                                                                 })
        elif request.GET.get('s_type') == "Portfolio":
            CandidateModels.company_Hide_Fields_request.objects.update_or_create(company_id_id=company.id,
                                                                                 profile_id_id=profile.id,
                                                                                 candidate_id_id=candidate.id,
                                                                                 defaults={
                                                                                     'portfolio_document': -1,
                                                                                 })
        elif request.GET.get('s_type') == "Certificarte":
            CandidateModels.company_Hide_Fields_request.objects.update_or_create(company_id_id=company.id,
                                                                                 profile_id_id=profile.id,
                                                                                 candidate_id_id=candidate.id,
                                                                                 defaults={
                                                                                     'certificate_document': -1,
                                                                                 })
        elif request.GET.get('s_type') == "email":
            CandidateModels.company_Hide_Fields_request.objects.update_or_create(company_id_id=company.id,
                                                                                 profile_id_id=profile.id,
                                                                                 candidate_id_id=candidate.id,
                                                                                 defaults={
                                                                                     'email': -1,
                                                                                 })
        elif request.GET.get('s_type') == "contact":
            CandidateModels.company_Hide_Fields_request.objects.update_or_create(company_id_id=company.id,
                                                                                 profile_id_id=profile.id,
                                                                                 candidate_id_id=candidate.id,
                                                                                 defaults={
                                                                                     'contact': -1,
                                                                                 })

        return HttpResponse(True)

    else:
        return HttpResponse(False)


def demo(request):
    return render(request, 'company/demo.html')


def candidate_detail(request, url):
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
    profile_id_get = CandidateModels.CandidateProfile.objects.get(url_name=url)
    activeprofile = CandidateModels.Profile.objects.get(candidate_id=profile_id_get.candidate_id, active=True)
    hire = {}
    company_data_status = {}
    # activeprofile=CandidateModels.Profile.objects.get(id=profile_id_get.profile_id)
    if activeprofile.active:
        profile = profile_id_get.profile_id
        candidate_id = ''
        if request.user.is_authenticated:
            print('asdddasddas')
            if request.user.is_company:
                candidate_id = profile_id_get.candidate_id_id
                # hire=CandidateModels.objects.filter(profile_id=activeprofile.id,candidate_id=candidate_id,company_id=User.objects.get(id=request.user.id))
                company_data_status = CandidateModels.company_data_request.objects.filter(profile_id=activeprofile.id,
                                                                                          candidate_id=candidate_id,
                                                                                          company_id=User.objects.get(
                                                                                              id=request.user.id))
            elif request.user.is_candidate:
                candidate_id = request.user.id
        else:
            candidate_id = profile_id_get.candidate_id.id
        user = User.objects.get(id=activeprofile.candidate_id.id)
        print()
        count = 0
        year_title_pairs = {}
        print("before hide field")
        print("user is ", user)
        print("profile is ", profile)
        hidefield = CandidateModels.Candidate_Hide_Fields.objects.get(candidate_id=user, profile_id=profile)
        profile_show = CandidateModels.CandidateProfile.objects.get(candidate_id=user, profile_id=profile)
        skills = CandidateModels.CandidateSkillUserMap.objects.filter(candidate_id=user, profile_id=profile)
        start_years = []
        end_years = []
        last_used = 0
        skill_names = ''
        if skills:
            for i in skills:
                skill_names += i.skill.name + ','
                if i.last_used == 'present':
                    last_used = int(datetime.datetime.now().year)
                else:
                    last_used = int(i.last_used)
                start_year = int(last_used) - int(i.total_exp)
                start_years.append(start_year)
                end_years.append(int(last_used))
        year_salary_pair = []
        company_names = []
        experiences = CandidateModels.CandidateExperience.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        if experiences:
            for i in experiences:
                company_names.append(i.company.company_name)
                end_date_year = 0
                end_date_month = 0
                if i.end_date:
                    if i.end_date == 'present':
                        end_date_year = int(datetime.datetime.now().year)
                        end_date_month = datetime.datetime.now().strftime("%B")
                    else:
                        end_date_year = int(i.end_date.split(',')[1])
                        end_date_month = i.end_date.split(',')[0]

                    salary_start_year = int(i.start_date.split(',')[1])
                    salary_start_year += month[i.start_date.split(',')[0]] / 12
                    salary_end_year = end_date_year
                    salary_end_year += month[end_date_month] / 12
                    year_salary_pair.append([salary_start_year, i.start_salary])
                    year_salary_pair.append([salary_end_year, i.end_salary])
                    if int(end_date_year) not in list(year_title_pairs.keys()):
                        year_title_pairs[end_date_year] = []
                        year_title_pairs[end_date_year].append(i)
                    else:
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
                # year_title_pairs.add(i.end_date.split(',')[1],i.job_profile_name)
        company_names = ','.join(company_names)
        educations = CandidateModels.CandidateEducation.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        if educations:
            for i in educations:
                count += 1
                if i.end_date:
                    if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
                        year_title_pairs[int(i.end_date.split(',')[1])] = []
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
                    else:
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
        certificates = CandidateModels.CandidateCertificationAttachment.objects.filter(candidate_id=user,
                                                                                       profile_id=activeprofile.id)
        if certificates:
            for i in certificates:
                count += 1
                if i.year:
                    if int(i.year) not in list(year_title_pairs.keys()):
                        year_title_pairs[int(i.year)] = []
                        year_title_pairs[int(i.year)].append(i)
                    else:
                        year_title_pairs[int(i.year)].append(i)
        awards = CandidateModels.CandidateAward.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        if awards:
            for i in awards:
                count += 1
                if i.year:
                    if int(i.year) not in list(year_title_pairs.keys()):
                        year_title_pairs[int(i.year)] = []
                        year_title_pairs[int(i.year)].append(i)
                    else:
                        year_title_pairs[int(i.year)].append(i)
        print(hidefield.edu_document)
        portfolio = CandidateModels.CandidatePortfolio.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        if portfolio:
            for i in portfolio:
                count += 1
                if i.year:
                    if int(i.year) not in list(year_title_pairs.keys()):
                        year_title_pairs[int(i.year)] = []
                        year_title_pairs[int(i.year)].append(i)
                    else:
                        year_title_pairs[int(i.year)].append(i)
        print(hidefield.edu_document)
        gaps = CandidateModels.Gap.objects.filter(candidate_id=user, profile_id=activeprofile.id)
        print(gaps)
        if gaps:
            for i in gaps:
                print("enterrred for loop for jgaps")
                if i.end_date:
                    if int(i.end_date.split(',')[1]) not in list(year_title_pairs.keys()):
                        print("ifffffffffffffffffffffffffffffffffffffffffffffff")
                        year_title_pairs[int(i.end_date.split(',')[1])] = []
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
                    else:
                        year_title_pairs[int(i.end_date.split(',')[1])].append(i)
        print("gaaaaaaaaaps ", gaps)
        print(year_title_pairs)
    sorted_key_list = sorted(year_title_pairs)
    sorted_key_list.reverse()
    job_preference = CandidateModels.CandidateJobPreference.objects.filter(candidate_id=user)

    return render(request, 'company/Dashbord-search-c-detail.html',
                  {'company_data_status': company_data_status, 'profile': profile_id_get, 'gaps': gaps,
                   'hidefield': hidefield, 'profile_show': profile_show, 'user': user, 'experiences': experiences,
                   'portfolios': portfolio, 'educations': educations, 'certificates': certificates, 'awards': awards,
                   'sorted_keys': sorted_key_list, 'year_title_pairs': year_title_pairs, 'start_years': start_years,
                   'end_years': end_years, 'skills': skill_names, 'year_salary_pair': year_salary_pair,
                   'company_names': company_names, 'job_preference': job_preference})


def doc_request(request):
    active = models.CandidateHire.objects.filter(company_id=request.user.id, request_status=1).values('id', 'message',
                                                                                                      'company_id',
                                                                                                      'candidate_id',
                                                                                                      'profile_id')
    new_request = models.CandidateHire.objects.filter(company_id=request.user.id, request_status=0).values('id',
                                                                                                           'message',
                                                                                                           'company_id',
                                                                                                           'candidate_id',
                                                                                                           'profile_id')
    archive = models.CandidateHire.objects.filter(company_id=request.user.id, request_status=-1).values('id', 'message',
                                                                                                        'company_id',
                                                                                                        'candidate_id',
                                                                                                        'profile_id')
    print('========================', active)
    data_active = CandidateModels.company_data_request.objects.filter(company_id=request.user.id, status=1).values('id',
                                                                                                                   'message',
                                                                                                                   'company_id',
                                                                                                                   'candidate_id',
                                                                                                                   'profile_id')
    data_new_request = CandidateModels.company_data_request.objects.filter(company_id=request.user.id,
                                                                           status=0).values('id', 'message',
                                                                                            'company_id',
                                                                                            'candidate_id',
                                                                                            'profile_id')
    data_archive = CandidateModels.company_data_request.objects.filter(company_id=request.user.id, status=-2).values(
        'id', 'message', 'company_id', 'candidate_id', 'profile_id')
    print('========================', data_new_request)
    shortlisted_candidates = models.ShortlistedCandidates.objects.filter(company_id=request.user.id)
    print("^^^^^^^^^^^^++++++++++++++++++++", shortlisted_candidates)
    return render(request, 'company/request.html',
                  {'active': active, 'new_request': new_request, 'archive': archive, 'data_active': data_active,
                   'data_new_request': data_new_request, 'data_archive': data_archive,
                   'shortlisted_candidates': shortlisted_candidates})


def document_request(request):
    data = json.loads(request.body.decode('UTF-8'))
    # data = json.loads()
    print("======data============", data)
    CandidateModels.company_data_request.objects.create(message=data['message'],
                                                        candidate_id=User.objects.get(id=int(data['candidate'])),
                                                        profile_id=CandidateModels.Profile.objects.get(
                                                            id=int(data['profile'])),
                                                        company_id=User.objects.get(id=request.user.id))
    return HttpResponse(True)


def company_profile(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if request.user.is_authenticated:
            if request.user.is_company:
                profile = models.CompanyProfile.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id)).exists()
                if not profile:
                    return redirect('company:add_edit_profile')
                else:
                    profile = models.CompanyProfile.objects.get(company_id=models.Company.objects.get(user_id=request.user.id))
                    get_internalcandidate = models.InternalCandidateBasicDetails.objects.filter(
                        company_id=models.Company.objects.get(user_id=request.user.id))
                    completed_job = models.JobCreation.objects.filter(
                        company_id=models.Company.objects.get(user_id=request.user.id))
                context['get_profile']= profile
                context['completed_job']=len(completed_job)
                context['get_internalcandidate']=len(get_internalcandidate)
                return render(request, 'company/Dashbord-company-profile.html',context)
            else:
                return render(request, 'accounts/404.html')
        else:
            return render(request, 'accounts/404.html')
    else:
        return redirect('company:add_edit_profile')

from django.db.models import Count, Sum


def shortlist_candidate(request):
    if request.user.is_authenticated:
        if request.user.is_company:
            user_id = User.objects.get(id=int(request.GET.get('user_id')))
            company_id = User.objects.get(id=request.user.id)
            if models.ShortlistedCandidates.objects.filter(candidate_id=user_id, company_id=company_id).exists():
                models.ShortlistedCandidates.objects.filter(candidate_id=user_id,
                                                            company_id=company_id).delete()
                return HttpResponse('removed')
            else:
                models.ShortlistedCandidates.objects.create(candidate_id=user_id,
                                                            company_id=company_id)
                return HttpResponse('shortlisted')
        else:
            return HttpResponse(False)
    else:
        return HttpResponse(False)


# ############################################    ATS    #################################################


# ########################    Internal Candidate    ########################

def add_candidate(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['working_day_types']= models.InternalCandidatePreference.working_day_choices
        context['company_type']= models.CompanyType.objects.all(),
        context['countries']= CandidateModels.Country.objects.all()
        context['sources']= CandidateModels.Source.objects.all(),
        context['languages']= CandidateModels.Languages.objects.all()
        if request.method == 'POST':
            # Basic Details
            # internal_candidate_skill_obj = models.InternalCandidateProfessionalSkill.objects.create(internal_candidate_id=models.InternalCandidate.objects.get(id=6))
            # for i in request.POST.getlist('professional_skills'):
            #     if i.isnumeric():
            #         main_skill_obj = models.CandidateModels.Skill.objects.get(id=i)
            #         internal_candidate_skill_obj.skills.add(main_skill_obj)
            #     else:
            #         if CandidateModels.InternalCandidateAddedSkill.objects.filter(name=i).exists():
            #             custom_added_skill_obj = CandidateModels.InternalCandidateAddedSkill.objects.get(name=i)
            #         else:
            #             custom_added_skill_obj = CandidateModels.InternalCandidateAddedSkill.objects.create(name=i)
            #         internal_candidate_skill_obj.custom_added_skills.add(custom_added_skill_obj)
            # gender = CandidateModels.Gender.objects.get(name=request.POST.get('gender'))
            # current_country = CandidateModels.Country.objects.get(id=request.POST.get('current_country'))
            # current_state = CandidateModels.State.objects.get(id=request.POST.get('current_state'))
            # current_city = CandidateModels.City.objects.get(id=request.POST.get('current_city'))
            # if request.POST.get('checked-address') == '':
            #     permanent_country = current_country
            #     permanent_state = current_state
            #     permanent_city = current_city
            #     permanent_zip_code = request.POST.get('current_zip_code')
            #     permanent_street = request.POST.get('current_street')
            # else:
            #     permanent_country = CandidateModels.Country.objects.get(id=request.POST.get('permanent_country'))
            #     permanent_state = CandidateModels.State.objects.get(id=request.POST.get('permanent_state'))
            #     permanent_city = CandidateModels.City.objects.get(id=request.POST.get('permanent_city'))
            #     permanent_zip_code = request.POST.get('permanent_zip_code')
            #     permanent_street = request.POST.get('permanent_street')
            # temp, created=models.InternalCandidate.objects.update_or_create(email=request.POST.get('email'),defaults={
            #                                                 'first_name':request.POST.get('first_name'),
            #                                                 'last_name':request.POST.get('last_name'),
            #                                                 'email':request.POST.get('email'),
            #                                                 'gender':gender,
            #                                                 'dob':request.POST.get('dob'),
            #                                                 'phone_no':request.POST.get('phone_no'),
            #                                                 'current_country':current_country,
            #                                                 'current_state':current_state,
            #                                                 'current_city':current_city,
            #                                                 'current_zip_code':request.POST.get('current_zip_code'),
            #                                                 'current_street':request.POST.get('current_street'),
            #                                                 'permanent_country':permanent_country,
            #                                                 'permanent_state':permanent_state,
            #                                                 'permanent_city':permanent_city,
            #                                                 'permanent_zip_code':permanent_zip_code,
            #                                                 'permanent_street':permanent_street,
            #                                           })
            #
            # # PROFESSIONAL DETAILS
            # exp_year = request.POST.get('professional-experience-year')
            # exp_month = request.POST.get('professional-experience-month')
            # experience = exp_year + '.' + exp_month
            # notice_period = CandidateModels.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
            # models.InternalCandidateProfessionalDetail.objects.create(internal_candidate_id=temp, experience=experience,
            #                                                           current_job_title=request.POST.get('professional-job-title'),
            #                                                           highest_qualification=request.POST.get('professional-high-qualify'),
            #                                                           expected_salary=request.POST.get('professional-expect-salary'),
            #                                                           current_salary=request.POST.get('professional-current-salary'),
            #                                                           current_employer=request.POST.get('professional-current-emp'),
            #                                                           skills=request.POST.get('professional_skills'),
            #                                                           notice_period=notice_period)
            #
            # # education details
            #
            # edu_institute = request.POST.getlist('edu_institute')
            # edu_department = request.POST.getlist('edu_department')
            # edu_degree = request.POST.getlist('edu_degree')
            # edu_duration = request.POST.getlist('edu_duration')
            # start_month = request.POST.getlist('edu-detail-start-month')
            # start_year = request.POST.getlist('edu-detail-start-year')
            # end_month = request.POST.getlist('edu-detail-end-month')
            # end_year = request.POST.getlist('edu-detail-end-year')
            # is_pursuing = request.POST.getlist('edu_pursuing_check')
            #
            # print('edu is_pursuing >>>>>>>>',is_pursuing)
            #
            # for inst, dept, deg, dur, start_month, start_year, end_month, end_year, is_purs \
            #         in zip_longest(edu_institute, edu_department, edu_degree, edu_duration, start_month, start_year,
            #                        end_month, end_year, is_pursuing, fillvalue=None):
            #     inst_id, created = CandidateModels.UniversityBoard.objects.get_or_create(name=inst)
            #     deg_id, created = CandidateModels.Degree.objects.get_or_create(name=deg)
            #     start_date = CandidateModels.Month.objects.get(id=start_month).name + "," + " " + start_year
            #     if is_purs == '':
            #         is_purs = True
            #         end_date = None
            #     else:
            #         end_date = CandidateModels.Month.objects.get(id=end_month).name + "," + " " + end_year
            #         is_purs = False
            #     models.InternalCandidateEducation.objects.create(internal_candidate_id=temp,
            #                                                      university_board=inst_id,
            #                                                      department=dept,
            #                                                      degree=deg_id,
            #                                                      duration=dur,
            #                                                      start_date=start_date,
            #                                                      end_date=end_date,
            #                                                      is_pursuing=is_purs
            #                                                      )
            #
            # # experience details
            #
            # job_title = request.POST.getlist('exper_details_jobtitle')
            # company_name = request.POST.getlist('exper_details_companyname')
            # start_month = request.POST.getlist('exper_details_start_month')
            # start_year = request.POST.getlist('exper_details_start_year')
            # end_month = request.POST.getlist('exper_details_end_month')
            # end_year = request.POST.getlist('exper_details_end_year')
            # skills = request.POST.getlist('exper_details_skills')
            # summary = request.POST.getlist('exper_details_summary')
            # work_status = request.POST.getlist('checked_workstatus')
            # # notice_period = request.POST.getlist('exper_details_notice')
            #
            # print('\n\nwork_status >>>>>>>', work_status)
            #
            # for (job_ti, company_name, start_m, start_y, end_m, end_y, skills, summary, work_stat)\
            #         in zip_longest(job_title, company_name, start_month, start_year, end_month,
            #                                 end_year, skills, summary, work_status, fillvalue=None):
            #     start_date = CandidateModels.Month.objects.get(id=start_m).name + "," + " " + start_y
            #     if end_month is not None:
            #         print('>>>>>>>end_m', end_m, type(end_m))
            #         # end_date = CandidateModels.Month.objects.get(id=end_m).name + "," + " " + end_y
            #         end_date = None
            #         work_stat = False
            #     else:
            #         work_stat = True
            #         end_date = None
            #     models.InternalCandidateExperience.objects.create(internal_candidate_id=temp,
            #                                                       job_title=job_ti,
            #                                                       company_name=company_name,
            #                                                       start_date=start_date,
            #                                                       end_date=end_date,
            #                                                       summary=summary,
            #                                                       skills=skills,
            #                                                       currently_working=work_stat)
            #
            # # PREFERENCE
            #
            # country = request.POST.get('preference_country')
            # city = request.POST.get('preference_city')
            # company_type = request.POST.get('preference_company_type')
            # working_day = request.POST.get('preference_working_day')
            # if len(country) and len(city) and len(company_type) and len(working_day):
            #     country = CandidateModels.Country.objects.get(id=request.POST.get('preference_country'))
            #     city = CandidateModels.City.objects.get(id=request.POST.get('preference_city'))
            #     company_type = models.CompanyType.objects.get(id=request.POST.get('preference_company_type'))
            #     models.InternalCandidatePreference.objects.create(internal_candidate_id=temp,country=country,
            #                                                       city=city,company_type=company_type,
            #                                                       working_days=request.POST.get('preference_working_day'))
            #
            # # Portfolio
            #
            # project_name = request.POST.getlist('project_name')
            # project_link = request.POST.getlist('project_link')
            # portfolio_attachment = request.FILES.getlist('portfolio_attachment')
            # print('port attach', portfolio_attachment)
            # portfolio_description = request.POST.getlist('portfolio_description')
            #
            # for (name, link, attachment, descrip) in zip_longest(project_name, project_link,
            #                                                      portfolio_attachment, portfolio_description,fillvalue=None):
            #     models.InternalCandidatePortfolio.objects.create(internal_candidate_id=temp,
            #                                                      project_name=name,project_link=link,
            #                                                      attachment=attachment,
            #                                                      description=descrip)
            temp = models.InternalCandidate.objects.get(id=6)
            # Source
            if request.POST.get('source'):
                selected_source = CandidateModels.Source.objects.get(id=request.POST.get('source'))
                if selected_source.name == 'Other':
                    other_source = request.POST.get('other_source')
                    models.InternalCandidateSource.objects.create(internal_candidate_id=temp,
                                                                source_id=selected_source,
                                                                custom_source_name=other_source)
                else:
                    models.InternalCandidateSource.objects.create(internal_candidate_id=temp, source_id=selected_source)

            #
            # # Attachment
            #
            # resume_file = request.FILES.get('attachment_resume')
            # print('resume_file', resume_file)
            # models.InternalCandidateAttachment.objects.create(
            #     internal_candidate_id=temp,
            #     file_name='resume', file=resume_file)
            # file_names = request.POST.getlist('file_name')
            # print('file_names', file_names)
            # files = request.FILES.getlist('file')
            # print('files', files)
            # if len(file_names) > 0 and len(files) > 0:
            #     for (name, file) in zip_longest(file_names,files):
            #         models.InternalCandidateAttachment.objects.create(internal_candidate_id=temp, file_name=name,
            #                                                           file=file)
        return render(request, 'company/ATS/add_candidate.html', context)
    else:
        return redirect('company:add_edit_profile')

signer = Signer()


def all_candidates(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        data = []
        context['Edit'] = False
        context['Delete'] = False
        context['View'] = False
        context['SalaryView']=False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
            if permissions.permissionsmodel.modelname == 'Salary':
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        if context['View']:
            context['my_param'] = request.GET
            candidates = models.InternalCandidateBasicDetails.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),withdraw_by_Candidate=False).order_by('-create_at')
            candidate_in_review = models.CandidateTempDatabase.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id)).order_by('-create_at')
            myFilter = CandidateFilter(request.GET, queryset=candidates)
            candidates = myFilter.qs 
            context['myFilter']=myFilter
            context['candidates'] = candidates
            context['candidate_in_review']= candidate_in_review
            if models.Employee.objects.filter(employee_id=request.user).exists():
                employee_obj = models.Employee.objects.get(employee_id=request.user)
                context['employee_obj']= employee_obj
            # for candidate in candidates:
            #     candidate_dict = {'id': candidate.id, 'name': candidate.first_name + ' ' + candidate.last_name,
            #                       'city': candidate.current_city.city_name}
            #     professional_detail = models.InternalCandidateProfessionalDetail.objects.get(internal_candidate_id=candidate.id)
            #     candidate_dict['job_title'] = professional_detail.current_job_title
            #     candidate_dict['experience'] = professional_detail.experience
            #     candidate_dict['expected_salary'] = professional_detail.expected_salary
            #     candidate_dict['notice_period'] = professional_detail.notice_period.notice_period
            #     candidate_dict['source'] = models.InternalCandidateSource.objects.get(internal_candidate_id=candidate.id)
            #     data.append(candidate_dict)
            
            return render(request, 'company/ATS/all_candidates.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def view_candidate(request, candidate_id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Associate'] = False
        context['View'] = False
        context['SalaryView']=False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                if permissions.permissionname == 'Associate':
                    context['Associate'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
            if permissions.permissionsmodel.modelname == 'Salary':
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        if context['View']:
            if models.InternalCandidateBasicDetails.objects.filter(id=candidate_id,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
                basic_detail = models.InternalCandidateBasicDetails.objects.get(id=candidate_id,
                                                                                company_id=models.Company.objects.get(
                                                                                    user_id=request.user.id))
                # ==============
                candidates = models.AppliedCandidate.objects.filter(candidate=basic_detail.candidate_id,job_id__close_job=False).values_list('job_id', flat=True)
                agency_submit_candidate = models.AssociateCandidateAgency.objects.filter(candidate_id=basic_detail.candidate_id,job_id__close_job=False).values_list('job_id', flat=True)
                job_array = list(chain(candidates, agency_submit_candidate))
                print(job_array)
                # agencyjob = models.AssignJobInternal.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
                # context['job_list'] = agencyjob.filter(~Q(job_id__in=job_array))
                print('\n', job_array)
                # context['applied_job_list'] = models.AssignJobInternal.objects.filter(job_id__in=job_array,agency_id=models.Agency.objects.get(user_id=request.user.id))
                agencyjob=models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_publish=True)
                # print('no applied job',agencyjob.filter(Q(id__in=job_array)))
                context['opening_job']=models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_publish=True,close_job=False)
                context['appliedjob']=models.JobCreation.objects.filter(id__in=job_array,company_id=models.Company.objects.get(user_id=request.user.id),is_publish=True)
                # ==============
                # context['opening_job']=models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_publish=True)
                context['assign_job']=models.AssociateCandidateInternal.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),internal_candidate_id=models.InternalCandidateBasicDetails.objects.get(id=candidate_id))

                # professional_detail = models.InternalCandidateProfessionalDetail.objects.get(internal_candidate_id=candidate_id)
                # candidate_preference = models.InternalCandidatePreference.objects.get(internal_candidate_id=candidate_id)
                context['candidate_education'] = CandidateModels.CandidateEducation.objects.filter(candidate_id=basic_detail.candidate_id)
                context['candidate_experience'] = CandidateModels.CandidateExperience.objects.filter(candidate_id=basic_detail.candidate_id)
                context['candidate_certification']=CandidateModels.CandidateCertificationAttachment.objects.filter(candidate_id=basic_detail.candidate_id)
                context['candidate_award']=CandidateModels.CandidateAward.objects.filter(candidate_id=basic_detail.candidate_id)
                context['candidate_portfolio']=CandidateModels.CandidatePortfolio.objects.filter(candidate_id=basic_detail.candidate_id)
                context['candidate_preferences']=CandidateModels.CandidateJobPreference.objects.filter(candidate_id=basic_detail.candidate_id)
                notes = models.InternalCandidateNotes.objects.filter(internal_candidate_id=candidate_id,company_id=models.Company.objects.get(user_id=request.user.id))
                skills = []
                for i in basic_detail.skills.all():
                    skills.append(i.name)
                
                context['basic_detail'] = basic_detail
                context['skills'] = skills
                context['notes'] = notes
                applied_job=models.AppliedCandidate.objects.filter(candidate_id=basic_detail.candidate_id,company_id=models.Company.objects.get(user_id=request.user.id))
                context['appliedjobcount']=len(applied_job)
                # if ChatModels.PrivateChat.objects.filter(Q(user1=User.objects.get(id=basic_detail.candidate_id.id)) & Q(user2=request.user)|Q(user1=request.user) & Q(user2=User.objects.get(id=basic_detail.candidate_id.id))).exists():
                #     context['chat_unique_id']=ChatModels.PrivateChat.objects.filter(Q(user1=User.objects.get(id=basic_detail.candidate_id.id)) & Q(user2=request.user)|Q(user1=request.user) & Q(user2=User.objects.get(id=basic_detail.candidate_id.id)))
                
                # =================
                candidate_stages_data = []
                for job in applied_job:
                    stages = models.CandidateJobStagesStatus.objects.filter(
                        company_id=models.Company.objects.get(user_id=request.user.id),
                        candidate_id=job.candidate_id,
                        job_id=job.job_id).order_by('sequence_number')

                    data = {'id': User.objects.get(id=job.candidate_id),'job_obj':job.job_id, 'stages': stages,'applied_date':job.create_at}
                    candidate_stages_data.append(data)
                context['applied_job']= candidate_stages_data

                # =====================
                return render(request, 'company/ATS/Candidate_view.html', context)
            else:
                return HttpResponse('Invalid Url')
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')


def submitted_view_candidate(request, candidate_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if AgencyModels.InternalCandidateBasicDetail.objects.filter(id=candidate_id).exists():
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            basic_detail = AgencyModels.InternalCandidateBasicDetail.objects.get(id=candidate_id)
            skills = []
            context['basic_detail'] = basic_detail
            return render(request, 'company/ATS/submitted_candidate_view.html', context)
        else:
            return HttpResponse('Invalid Url')
    else:
        return redirect('company:add_edit_profile')

def internal_candidate_notes(request):
    if request.method == 'POST':
        print('\n\n\nmessage', request.POST.get('message'))
        print('\n\n\ndate', request.POST.get('date'))
        print('\n\n\nuser', request.POST.get('user'))
        print('\n\n\ndepartment', request.POST.get('department'))
        print('\n\n\ncandidate_id', request.POST.get('candidate_id'))
        # try:
        candidate = models.InternalCandidateBasicDetails.objects.get(id=request.POST.get('candidate_id'))
        created_note = models.InternalCandidateNotes.objects.create(internal_candidate_id=candidate,
                                                                    company_id=models.Company.objects.get(
                                                                        user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id),
                                                                    note=request.POST.get('message'))
        return JsonResponse({'date': created_note.create_at, 'status': 'success'}, safe=False)
        # except:
        # return JsonResponse({'status': 'failed'}, safe=False)

# ########################    Internal Candidate  End  ########################


# ########################    JOB    ########################

def job_template_creation(request,jobtemplate_id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['if_template']=True
        # if 'get_template_job' in request.session:
        #     context['if_template']=True
        context['get_job_template'] = models.JobCreationTemplate.objects.get(id=jobtemplate_id)
        context['job_owner'] = models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['job_types'] = CandidateModels.JobTypes.objects.all()
        context['template_category'] = models.TemplateCategory.objects.filter(stage=1,company_id=models.Company.objects.get(user_id=request.user.id))
        context['job_status'] = CandidateModels.JobStatus.objects.all()
        context['job_shift'] = CandidateModels.JobShift.objects.all()
        context['countries'] = CandidateModels.Country.objects.all()
        context['industry_types'] = CandidateModels.IndustryType.objects.all()
        context['departments'] = models.Department.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        get_all_agency = AgencyModels.CompanyAgencyConnection.objects.filter(
            company_id=models.Company.objects.get(user_id=request.user.id), is_accepted=True).values_list('agency_id')
        get_agency = AgencyModels.AgencyType.objects.filter(agency_id__in=get_all_agency, is_agency=True).values_list(
            'agency_id')
        get_freelancer = AgencyModels.AgencyType.objects.filter(agency_id__in=get_all_agency,
                                                                is_freelancer=True).values_list('agency_id')
        context['external_agency'] = AgencyModels.AgencyProfile.objects.filter(
            agency_id__in=get_agency)  # here will be filter query later
        context['external_freelancer'] = AgencyModels.FreelancerProfile.objects.filter(agency_id__in=get_freelancer)#here will be filter query later
        if request.method == 'POST':
            if request.POST.get('remote_job') == 'yes':
                remote_job = True
            else:
                remote_job = False
            min_salary = 0
            max_salary = 0
            salary_as_per_market = False
            if request.POST.get('as-per-market') == 'as_per_market':
                salary_as_per_market = True
                min_salary = min_salary
                max_salary = max_salary
            else:
                min_salary = request.POST.get('Min')
                max_salary = request.POST.get('Max')
            user_id = User.objects.get(id=request.user.id)
            job_type = CandidateModels.JobTypes.objects.get(id=request.POST.get('job_type'))
            # status = CandidateModels.JobStatus.objects.get(id=request.POST.get('status'))
            industry_type = CandidateModels.IndustryType.objects.get(id=request.POST.get('industry_type'))
            country_id = CandidateModels.Country.objects.get(id=request.POST.get('country'))
            city_id = CandidateModels.City.objects.get(id=request.POST.get('city'))
            assign_internal_id=request.POST.getlist('internal')
            assign_external_id=request.POST.getlist('external')

            department = models.Department.objects.get(id=request.POST.get('department'))

            job_id = models.JobCreation.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                    user_id=User.objects.get(id=request.user.id),
                                                    job_title=request.POST.get('job_title'),
                                                    contact_name=User.objects.get(id=request.POST.get('contact_person')),
                                                    job_owner=User.objects.get(id=request.POST.get('job_owner')),
                                                    job_type=job_type, target_date=request.POST.get('target_date'),
                                                    industry_type=industry_type, remote_job=remote_job,
                                                    salary_as_per_market=salary_as_per_market,
                                                    min_salary=min_salary,
                                                    max_salary=max_salary,
                                                    experience_year_min=request.POST.get('experience_year_min'),
                                                    experience_year_max=request.POST.get('experience_year_max'),
                                                    job_description=request.POST.get('job_description'),
                                                    benefits=request.POST.get('job_benefit'),
                                                    requirements=request.POST.get('job_requirement'), country=country_id,
                                                    city=city_id,
                                                    department=department,
                                                    zip_code=request.POST.get('zipcode'))
            for i in request.POST.getlist('job_skills'):
                if i.isnumeric():
                    main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                    job_id.required_skill.add(main_skill_obj)
                else:
                    tag_cre=CandidateModels.Skill.objects.create(name=i)
                    job_id.required_skill.add(tag_cre)
            for shift in request.POST.getlist('job_shifts'):
                if shift.isnumeric():
                    main_shift_obj = CandidateModels.JobShift.objects.get(id=shift)
                    job_id.job_shift_id.add(main_shift_obj)
            for assign_id in assign_external_id:
                models.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_external=True,recruiter_id=User.objects.get(id=int(assign_id)))
            for assign_id in assign_internal_id:
                models.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id)))

            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"  
            job_user=list(set([request.POST.get('job_owner'), request.POST.get('contact_person')]))
            for i in job_user:
                description = "New job "+job_id.job_title+" has been created by "+request.user.first_name+" "+request.user.last_name
                if i != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i), verb="Job Create/publish",
                                description=description,image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                    job_id.id))
            return redirect('company:workflow_selection', id=job_id.id)
        return render(request, 'company/ATS/job_creation.html', context)
    else:
        return redirect('company:add_edit_profile')

def job_creation(request,jobid=None):
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add']=False
        context['Edit']=False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
        if context['Add'] or context['Edit'] :
            context['if_template']=True
            if jobid:
                context['if_template']=False
                context['get_job_template'] = models.JobCreation.objects.get(id=jobid)
                context['external_assign'] = models.CompanyAssignJob.objects.filter(job_id=models.JobCreation.objects.get(id=jobid),
                                                                                    recruiter_type_external=True).values_list(
                    'recruiter_id', flat=True)

                context['internal_assign'] = models.CompanyAssignJob.objects.filter(job_id=models.JobCreation.objects.get(id=jobid),
                                                                                    recruiter_type_internal=True).values_list(
                    'recruiter_id', flat=True)
                context['job_assign']=models.CompanyAssignJob.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),job_id=models.JobCreation.objects.get(id=jobid))
            context['job_owner'] = models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            context['job_types'] = CandidateModels.JobTypes.objects.all()
            context['template_category'] = models.TemplateCategory.objects.filter(stage=CandidateModels.Stage_list.objects.get(name='Job Creation'),company_id=models.Company.objects.get(user_id=request.user.id))
            # context['job_status'] = CandidateModels.JobStatus.objects.all()
            context['job_shift'] = CandidateModels.JobShift.objects.all()
            context['countries'] = CandidateModels.Country.objects.all()
            context['industry_types'] = CandidateModels.IndustryType.objects.all()
            context['departments'] = models.Department.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            get_all_agency=AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=True).values_list('agency_id')
            get_agency=AgencyModels.AgencyType.objects.filter(agency_id__in=get_all_agency,is_agency=True).values_list('agency_id')
            get_freelancer=AgencyModels.AgencyType.objects.filter(agency_id__in=get_all_agency,is_freelancer=True).values_list('agency_id')
            context['external_agency'] = AgencyModels.AgencyProfile.objects.filter(agency_id__in=get_agency)#here will be filter query later
            context['external_freelancer'] = AgencyModels.FreelancerProfile.objects.filter(agency_id__in=get_freelancer)#here will be filter query later


            if request.method == 'POST':
                user_id = User.objects.get(id=request.user.id)
                if request.POST.get('remote_job') == 'yes':
                    remote_job = True
                else:
                    remote_job = False
                job_type = CandidateModels.JobTypes.objects.get(id=request.POST.get('job_type'))
                # status = CandidateModels.JobStatus.objects.get(id=request.POST.get('status'))
                industry_type = CandidateModels.IndustryType.objects.get(id=request.POST.get('industry_type'))
                country_id = CandidateModels.Country.objects.get(id=request.POST.get('country'))
                city_id = CandidateModels.City.objects.get(id=request.POST.get('city'))
                department_id = models.Department.objects.get(id=request.POST.get('department'))
                assign_internal_id=request.POST.getlist('internal')
                assign_external_id=request.POST.getlist('external')
                min_salary=0
                max_salary=0
                salary_as_per_market=False
                if request.POST.get('as-per-market')=='as_per_market':
                    salary_as_per_market=True
                    min_salary =min_salary
                    max_salary=max_salary
                else:
                    min_salary= request.POST.get('Min')
                    max_salary= request.POST.get('Max')
                job_id=''
                if jobid:
                    job_create,update = models.JobCreation.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),id=jobid,defaults={
                                                            'user_id': User.objects.get(id=request.user.id),
                                                            'job_title': request.POST.get('job_title'),
                                                            'contact_name': User.objects.get(id=request.POST.get('contact_person')),
                                                            'job_owner': User.objects.get(id=request.POST.get('job_owner')),
                                                            'job_type' : job_type,
                                                            'target_date' : request.POST.get('target_date'),
                                                            'industry_type' : industry_type,
                                                            'remote_job' : remote_job,
                                                            'salary_as_per_market':salary_as_per_market,
                                                            'min_salary' : min_salary,
                                                            'max_salary' : max_salary,
                                                            'experience_year_min':request.POST.get('experience_year_min'),
                                                            'experience_year_max':request.POST.get('experience_year_max'),
                                                            'job_description' : request.POST.get('job_description'),
                                                            'benefits' : request.POST.get('job_benefit'),
                                                            'requirements' : request.POST.get('job_requirement'),
                                                            'country': country_id,
                                                            'city': city_id,
                                                            'department':department_id,
                                                            'zip_code' : request.POST.get('zipcode'),
                                                            'updated_at':datetime.datetime.now()})
                    job_create.required_skill.clear()
                    for i in request.POST.getlist('job_skills'):
                        if i.isnumeric():
                            main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                            job_create.required_skill.add(main_skill_obj)
                        else:
                            tag_cre=CandidateModels.Skill.objects.create(name=i)
                            job_create.required_skill.add(tag_cre)
                    job_create.job_shift_id.clear()
                    for shift in request.POST.getlist('job_shifts'):
                        if shift.isnumeric():
                            main_shift_obj = CandidateModels.JobShift.objects.get(id=shift)
                            job_create.job_shift_id.add(main_shift_obj)
                    print("-------------------",assign_job)
                    for assign_id in assign_external_id:
                            models.CompanyAssignJob.objects.filter(job_id=job_create,company_id=models.Company.objects.get(user_id=request.user.id),recruiter_type_external=True,recruiter_id=User.objects.get(id=int(assign_id))).delete()
                            models.CompanyAssignJob.objects.create(job_id=job_create,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_external=True,recruiter_id=User.objects.get(id=int(assign_id)))
                    for assign_id in assign_internal_id:
                        print(assign_id)
                        models.CompanyAssignJob.objects.filter(job_id=job_create,company_id=models.Company.objects.get(user_id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id))).delete()
                        models.CompanyAssignJob.objects.create(job_id=job_create,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id)))
                    if job_create.is_publish:
                        result = AgencyModels.AssociateJob.objects.filter(job_id=job_create).count()
                        count = models.AppliedCandidate.objects.filter(job_id=job_create).count()
                        # Notification
                        description = job_create.company_id.company_id.company_name + " Job Edit By Company"
                        if job_create.contact_name.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=job_create.contact_name.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                                            job_create.id))
                        if job_create.job_owner.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=job_create.job_owner.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                                            job_create.id))
                        all_assign_users=models.CompanyAssignJob.objects.filter(job_id=job_create)
                        
                        for i in all_assign_users:
                            print(i.recruiter_type_external)
                            if i.recruiter_type_internal:
                                description = job_create.company_id.company_id.company_name + " Job Edit By Company"
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                                            job_create.id))
                            if i.recruiter_type_external :
                                print("==========",all_assign_users)
                                description = job_create.company_id.company_id.company_name + " Job Edit By Company"
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/agency/job_view/" + str(
                                                                                            job_create.id))
                        if (count+result)==0:
                            return redirect('company:workflow_selection', id=job_create)
                        else:
                            return redirect('company:created_job_view', id=job_create)
                    else:
                        return redirect('company:workflow_selection', id=job_create)
                else:
                    job_id = models.JobCreation.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            job_title=request.POST.get('job_title'),
                                                            contact_name=User.objects.get(id=request.POST.get('contact_person')),
                                                            job_owner=User.objects.get(id=request.POST.get('job_owner')),
                                                            job_type=job_type, target_date=request.POST.get('target_date'),
                                                            industry_type=industry_type, remote_job=remote_job,
                                                            salary_as_per_market=salary_as_per_market,
                                                            min_salary=min_salary,
                                                            max_salary=max_salary,
                                                            experience_year_min=request.POST.get('experience_year_min'),
                                                            experience_year_max=request.POST.get('experience_year_max'),
                                                            job_description=request.POST.get('job_description'),
                                                            benefits=request.POST.get('job_benefit'),
                                                            department=department_id,
                                                            requirements=request.POST.get('job_requirement'), country=country_id,
                                                            city=city_id, zip_code=request.POST.get('zipcode'))
                    for i in request.POST.getlist('job_skills'):
                        if i.isnumeric():
                            main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                            job_id.required_skill.add(main_skill_obj)
                        else:
                            tag_cre=CandidateModels.Skill.objects.create(name=i)
                            job_id.required_skill.add(tag_cre)
                    for shift in request.POST.getlist('job_shifts'):
                        if shift.isnumeric():
                            main_shift_obj = CandidateModels.JobShift.objects.get(id=shift)
                            job_id.job_shift_id.add(main_shift_obj)
                    for assign_id in assign_external_id:
                            models.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_external=True,recruiter_id=User.objects.get(id=int(assign_id)))
                    for assign_id in assign_internal_id:
                        models.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id)))
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                job_user=list(set([request.POST.get('job_owner'), request.POST.get('contact_person')]))
                for i in job_user:
                    description = "New job "+job_id.job_title+" has been created by "+request.user.first_name+" "+request.user.last_name
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Job Create/publish",
                                    description=description,image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                        job_id.id))
                return redirect('company:workflow_selection', id=job_id.id)
            return render(request, 'company/ATS/job_creation.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def job_creation_select_template(request):
    if request.method=='POST':
        job_template = json.loads(request.body.decode('UTF-8'))
        print(job_template)
        get_templatejob_id=models.JobCreationTemplate.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),category=models.TemplateCategory.objects.get(
                                                    id=int(job_template['category'])),
                                                    template=models.Template_creation.objects.get(
                                                    id=int(job_template['template'])))
        request.session['get_template_job']=get_templatejob_id.id
        data = {"status": "true"}
        data['url']='/company/job_template_creation/'+str(get_templatejob_id)
        return JsonResponse(data)
        # return HttpResponseRedirect("company:job_template_creation",jobtemplate_id=get_templatejob_id)
        

def job_creation_template(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['job_types'] = CandidateModels.JobTypes.objects.all()
        context['template_category'] = models.TemplateCategory.objects.filter(stage=1,company_id=models.Company.objects.get(user_id=request.user.id))
        # context['job_status'] = CandidateModels.JobStatus.objects.all()
        context['job_shift'] = CandidateModels.JobShift.objects.all()
        context['countries'] = CandidateModels.Country.objects.all()
        context['industry_types'] = CandidateModels.IndustryType.objects.all()
        context['departments'] = models.Department.objects.filter(
            company_id=models.Company.objects.get(user_id=request.user.id))
        if request.method == 'POST':
            if request.POST.get('remote_job') == 'yes':
                remote_job = True
            else:
                remote_job = False
            min_salary = 0
            max_salary = 0
            salary_as_per_market = False
            if request.POST.get('as-per-market') == 'as_per_market':
                salary_as_per_market = True
                min_salary = min_salary
                max_salary = max_salary
            else:
                min_salary = request.POST.get('Min')
                max_salary = request.POST.get('Max')
            user_id = User.objects.get(id=request.user.id)
            job_type = CandidateModels.JobTypes.objects.get(id=request.POST.get('job_type'))
            # status = CandidateModels.JobStatus.objects.get(id=request.POST.get('status'))
            industry_type = CandidateModels.IndustryType.objects.get(id=request.POST.get('industry_type'))
            country_id = CandidateModels.Country.objects.get(id=request.POST.get('country'))
            city_id = CandidateModels.City.objects.get(id=request.POST.get('city'))
            department_id = None
            if request.POST.get('department'):
                department_id = models.Department.objects.get(id=request.POST.get('department'))
            template_id,created = models.JobCreationTemplate.objects.update_or_create(stage=CandidateModels.Stage_list.objects.get(
                                                        id=int(request.session['create_template']['stageid'])),
                                                        category=models.TemplateCategory.objects.get(
                                                        id=int(request.session['create_template']['categoryid'])),
                                                        template=models.Template_creation.objects.get(
                                                        id=int(request.session['create_template']['templateid'])),  
                                                        company_id=models.Company.objects.get(user_id=request.user.id), defaults={
                                                        'user_id':User.objects.get(id=request.user.id),
                                                        'job_title':request.POST.get('job_title'),
                                                    'job_type':job_type, 'target_date':request.POST.get('target_date'),
                                                    'industry_type':industry_type, 'remote_job':remote_job,
                                                    'salary_as_per_market':salary_as_per_market,
                                                    'min_salary':min_salary,
                                                    'max_salary':max_salary,
                                                    'experience_year_min':request.POST.get('experience_year_min'),
                                                    'experience_year_max':request.POST.get('experience_year_max'),
                                                    'job_description':request.POST.get('job_description'),
                                                    'benefits':request.POST.get('job_benefit'),
                                                    'department': department_id,
                                                    'requirements':request.POST.get('job_requirement'), 'country':country_id,
                                                    'city':city_id, 'zip_code':request.POST.get('zipcode')})
            job_shifts = request.POST.getlist('job_shifts')
            for shift in job_shifts:
                template_id.jobshift.add(CandidateModels.JobShift.objects.get(id=int(shift)))
            template_id.required_skill.clear()
            for i in request.POST.getlist('job_skills'):
                if i.isnumeric():
                    main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                    template_id.required_skill.add(main_skill_obj)
                else:
                    tag_cre=CandidateModels.Skill.objects.create(name=i)
                    template_id.required_skill.add(tag_cre)
            template_id.save()
            template_id.template.status = True
            template_id.template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            description = template_name.name+" has been added to your workspace"
            all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            for i in all_internal_users:
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Job Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/job_template_view/"+str(template_id.template.id))
            
            all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                            user_id=request.user)).values_list('employee_id', flat=True)
            get_email=[]
            
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Job','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'templateid':template_id.id,'link':'job_template_view'})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return redirect('company:template_listing')
        return render(request, 'company/ATS/job_creation_template.html', context)
    else:
        return redirect('company:add_edit_profile')

def job_creation_template_edit(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['get_template']=models.JobCreationTemplate.objects.get(template=models.Template_creation.objects.get(
                                                        id=id))
        context['job_types'] = CandidateModels.JobTypes.objects.all()
        context['template_category'] = models.TemplateCategory.objects.filter(stage=1,company_id=models.Company.objects.get(user_id=request.user.id))
        # context['job_status'] = CandidateModels.JobStatus.objects.all()
        context['job_shift'] = CandidateModels.JobShift.objects.all()
        context['countries'] = CandidateModels.Country.objects.all()
        context['industry_types'] = CandidateModels.IndustryType.objects.all()
        if request.method == 'POST':
            if request.POST.get('remote_job') == 'yes':
                remote_job = True
            else:
                remote_job = False
            min_salary = 0
            max_salary = 0
            salary_as_per_market = False
            
            if request.POST.get('as-per-market') == 'as_per_market':
                print(request.POST.get('as-per-market'))
                salary_as_per_market = True
                min_salary = min_salary
                max_salary = max_salary
            else:
                min_salary = request.POST.get('Min')
                max_salary = request.POST.get('Max')
            job_type = CandidateModels.JobTypes.objects.get(id=request.POST.get('job_type'))
            # status = CandidateModels.JobStatus.objects.get(id=request.POST.get('status'))
            industry_type = CandidateModels.IndustryType.objects.get(id=request.POST.get('industry_type'))
            country_id = CandidateModels.Country.objects.get(id=request.POST.get('country'))
            city_id = CandidateModels.City.objects.get(id=request.POST.get('city'))
            template_id,created = models.JobCreationTemplate.objects.update_or_create(template=models.Template_creation.objects.get(
                                                        id=id), 
                                                        company_id=models.Company.objects.get(user_id=request.user.id), defaults={
                                                        'update_by':User.objects.get(id=request.user.id),
                                                        'update_at':datetime.datetime.now(),
                                                        'job_title':request.POST.get('job_title'),
                                                    'job_type':job_type, 'target_date':request.POST.get('target_date'),
                                                    'industry_type':industry_type, 'remote_job':remote_job,
                                                    'salary_as_per_market':salary_as_per_market,
                                                    'min_salary':min_salary,
                                                    'max_salary':max_salary,
                                                    'experience_year_min':request.POST.get('experience_year_min'),
                                                    'experience_year_max':request.POST.get('experience_year_max'),
                                                    'job_description':request.POST.get('job_description'),
                                                    'benefits':request.POST.get('job_benefit'),
                                                    'requirements':request.POST.get('job_requirement'), 'country':country_id,
                                                    'city':city_id, 'zip_code':request.POST.get('zipcode')})
            job_shifts = request.POST.getlist('job_shifts')
            for shift in job_shifts:
                template_id.jobshift.add(CandidateModels.JobShift.objects.get(id=int(shift)))
            template_id.required_skill.clear()
            for i in request.POST.getlist('job_skills'):
                if i.isnumeric():
                    main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                    template_id.required_skill.add(main_skill_obj)
                else:
                    tag_cre=CandidateModels.Skill.objects.create(name=i)
                    template_id.required_skill.add(tag_cre)
            template_id.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit Job Template"
            if context['get_template'].user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=context['get_template'].user_id.id),verb="Edit Job Template",
                                                                    description=description,
                                                                    target_url=header+"://"+current_site.domain+"/company/job_template_view/"+str(context['get_template'].template.id))
            return redirect('company:template_listing')
        return render(request, 'company/ATS/job_creation_template.html', context)
    else:
        return redirect('company:add_edit_profile')

def job_openings_table(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['SalaryView'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                print(permissions.permissionname,'====',permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
            if permissions.permissionsmodel.modelname == 'Salary':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        if context['Add'] or  context['Edit'] or  context['Delete']:
            jobs = models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),close_job=False).order_by('-created_at')
            # jobs = models.JobCreation.objects.all()
            closejob = models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),close_job=True).order_by('-created_at')
            myFilter = JobFilter(request.GET, queryset=jobs)
            jobs = myFilter.qs 
            context['myFilter']=myFilter
            context['jobs'] = jobs
            context['closejob'] = closejob
            return render(request, 'company/ATS/job_openings_table.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def job_openings_table_filter(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                print(permissions.permissionname,'====',permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
        if context['Add'] or  context['Edit'] or  context['Delete']:
            jobs = models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),close_job=False).order_by('-created_at')
            # jobs = models.JobCreation.objects.all()
            closejob = models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),close_job=True).order_by('-created_at')
            myFilter = JobFilter(request.GET, queryset=jobs)
            jobs = myFilter.qs 
            context['myFilter']=myFilter
            context['jobs'] = jobs
            context['closejob'] = closejob
            return render(request, 'company/ATS/job_openings_table.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def job_openings_requests(request):
    return render(request, 'company/ATS/job_openings_requests.html')

def job_delete(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        deljob=models.JobCreation.objects.get(id=int(category_data['job_id']),company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        if deljob:
            return HttpResponse(True)
        else:
            return HttpResponse(True)


def created_job_view(request, id):
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['View'] = False
        context['Edit'] = False
        context['Publish'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Publish':
                    context['Publish'] = True
        get_all_agency = AgencyModels.CompanyAgencyConnection.objects.filter(
            company_id=models.Company.objects.get(user_id=request.user.id), is_accepted=True).values_list('agency_id')
        get_agency = AgencyModels.AgencyType.objects.filter(agency_id__in=get_all_agency, is_agency=True).values_list(
            'agency_id')
        get_freelancer = AgencyModels.AgencyType.objects.filter(agency_id__in=get_all_agency,
                                                                is_freelancer=True).values_list('agency_id')

        context['external_agency'] = AgencyModels.AgencyProfile.objects.filter(
            agency_id__in=get_agency)  # here will be filter query later
        context['external_freelancer'] = AgencyModels.FreelancerProfile.objects.filter(
            agency_id__in=get_freelancer)  # here will be filter query later

        context['job_owner'] = models.Employee.objects.filter(
            company_id=models.Company.objects.get(user_id=request.user.id))
        job_obj = models.JobCreation.objects.get(id=id)
        get_recruiter_external=models.CompanyAssignJob.objects.filter(job_id=job_obj,recruiter_type_external=True)
        context['external']= get_recruiter_external
        context['external_assign'] =models.CompanyAssignJob.objects.filter(job_id=job_obj,recruiter_type_external=True).values_list('recruiter_id',flat=True)

        context['internal_assign'] = models.CompanyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True).values_list('recruiter_id',flat=True)
        get_recruiter_internal=models.CompanyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True)
        context['internal']=get_recruiter_internal
        context['job_obj']= job_obj
        context['active_job_count']=len(models.JobCreation.objects.filter(company_id=job_obj.company_id.id,close_job=False,close_job_targetdate=False,is_publish=True))
        context['close_job_count'] = len(models.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=True))
        context['last_close_job'] = models.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=True).order_by('-close_job_at').first()
        context['latest_10_job'] = models.JobCreation.objects.filter(company_id=job_obj.company_id.id,close_job=False,close_job_targetdate=False,is_publish=True).order_by('-publish_at')

        if models.JobWorkflow.objects.filter(job_id=job_obj).exists():
            job_workflow = models.JobWorkflow.objects.get(job_id=job_obj)
            context['job_workflow']=job_workflow
            if job_workflow.withworkflow:
                context['workflow']=True
            else:
                context['workflow']=False
            if job_workflow.workflow_id:
                main_workflow = models.Workflows.objects.get(id=job_workflow.workflow_id.id)
                workflow_stages = models.WorkflowStages.objects.filter(workflow=main_workflow).order_by('sequence_number')
                context['workflow_stages']= workflow_stages
                context['main_workflow']= main_workflow

                workflow_data = []
                for stage in workflow_stages:
                    stage_dict = {'stage': stage, 'data': ''}
                    if stage.stage.name == 'MCQ Test':
                        mcq_template = models.ExamTemplate.objects.get(company_id=stage.company_id, template=stage.template,
                                                                        stage=stage.stage)
                        total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                        time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                        if mcq_template.question_wise_time:
                            get_template_que = models.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)

                            for time in get_template_que:
                                total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                    "%M:%S")
                            stage_dict['mcq_time'] = total_time.time()
                        else:
                            stage_dict['mcq_time'] = datetime.datetime.strptime(mcq_template.duration, "%M:%S").time()
                        if mcq_template.marking_system == "question_wise":
                            get_template_que = models.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
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
                        descriptive_template = models.DescriptiveExamTemplate.objects.get(
                            company_id=stage.company_id,
                            stage=stage.stage,
                            template=stage.template)
                        total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                        time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')

                        get_template_que = models.DescriptiveExamQuestionUnit.objects.filter(
                            template=descriptive_template.template.id)

                        for time in get_template_que:
                            total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time, "%M:%S")
                        stage_dict['descriptive_time'] = total_time.time()

                        get_template_que = models.DescriptiveExamQuestionUnit.objects.filter(
                            template=descriptive_template.template.id)
                        total_marks = 0
                        for mark in get_template_que:
                            total_marks += int(mark.question_mark)
                        stage_dict['descriptive_marks'] = total_marks
                        stage_dict['data'] = descriptive_template

                    if stage.stage.name == 'Image Test':
                        image_template = models.ImageExamTemplate.objects.get(company_id=stage.company_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)
                        total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                        time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                        if image_template.question_wise_time:
                            get_template_que = models.ImageExamQuestionUnit.objects.filter(
                                template=image_template.template.id)

                            for time in get_template_que:
                                total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                    "%M:%S")
                            stage_dict['image_time'] = total_time.time()
                        else:
                            stage_dict['image_time'] = datetime.datetime.strptime(image_template.duration, "%M:%S").time()
                        if image_template.marking_system == "question_wise":
                            get_template_que = models.ImageExamQuestionUnit.objects.filter(
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

                        audio_template = models.AudioExamTemplate.objects.get(company_id=stage.company_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)

                        get_template_que = models.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                        total_marks = 0
                        for mark in get_template_que:
                            total_marks += int(mark.question_mark)
                        stage_dict['audio_marks'] = total_marks
                        stage_dict['data'] = audio_template

                    if stage.stage.name == 'Coding Test':

                        coding_template = models.CodingExamConfiguration.objects.get(company_id=stage.company_id,
                                                                                        template_id=stage.template)
                        if coding_template.assignment_type == 'marks':
                            coding_que_marks = models.CodingExamQuestions.objects.filter(
                                coding_exam_config_id=coding_template.id)
                            total_marks = 0
                            for i in coding_que_marks:
                                total_marks += int(i.marks)
                            stage_dict['total_marks'] = total_marks
                        else:
                            coding_que_rating = models.CodingScoreCard.objects.filter(coding_exam_config_id=coding_template)
                            stage_dict['coding_que_rating'] = coding_que_rating
                        stage_dict['data'] = coding_template

                    workflow_data.append(stage_dict)

                context['workflow_data'] = workflow_data
        if request.method == 'POST':
            if 'edit' in request.POST:
                return redirect('company:job_edit',job_obj.id)
            else:
                job_obj.is_publish = True
                job_obj.publish_at = datetime.datetime.now()
                job_obj.updated_at = datetime.datetime.now()
                job_obj.save()
                if not models.JobWorkflow.objects.filter(job_id=job_obj).exists():
                    job_workflow_obj,created = models.JobWorkflow.objects.update_or_create(job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id),
                                                            defaults={'onthego':True, 'workflow_id':None,'user_id':User.objects.get(id=request.user.id)})
                    job_workflow_obj.save()
                # onthego change
                if job_workflow.onthego:
                    stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                    models.OnTheGoStages.objects.update_or_create(job_id=job_obj,company_id=job_obj.company_id,stage=stage_obj,
                                                                    defaults={'user_id':User.objects.get(id=request.user.id),
                                                                            'stage_name':"Job Applied",'sequence_number':1})
                job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
                for j in job_assign_recruiter:
                    if j.recruiter_type_external:
                        get_recruiter=models.CompanyAssignJob.objects.get(id=j.id)
                        send_email= User.objects.get(id=get_recruiter.recruiter_id.id)
                        mail_subject = 'You have been invited to a new job'
                        # current_site = get_current_site(request)You have been invited to work on new Job”” In Company”” by “”. Please accept it to get started.
                        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"You have been invited to work on new Job "+job_obj.job_title+" In Company "+job_obj.company_id.company_id.company_name+ " by "+request.user.first_name+" "+request.user.last_name+". Please accept it to get started."})
                        to_email = send_email.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        try:
                            msg.send()
                            models.AssignExternal.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),job_id=job_obj,recruiter_id=AgencyModels.Agency.objects.get(user_id=send_email.id),defaults={'user_id':User.objects.get(id=request.user.id),'send_email':True})
                        except:
                            models.AssignExternal.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),job_id=job_obj,recruiter_id=AgencyModels.Agency.objects.get(user_id=send_email.id),defaults={'user_id':User.objects.get(id=request.user.id),'send_email':False})
                            continue
                    if j.recruiter_type_internal:
                        print("==================",j)
                        get_recruiter=models.CompanyAssignJob.objects.get(id=j.id)
                        send_email= User.objects.get(id=get_recruiter.recruiter_id.id)
                        mail_subject = 'You have been assigned new job'
                        # current_site = get_current_site(request)
                        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"You have been assigned to new Job "+job_obj.job_title+" By "+request.user.first_name + ' '+request.user.last_name + "Please login to review and submit new candidates."})
                        to_email = send_email.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        try:
                            msg.send()
                            models.AssignInternal.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),job_id=job_obj,recruiter_id=User.objects.get(id=send_email.id),defaults={'user_id':User.objects.get(id=request.user.id),'send_email':True})
                        except:
                            print('not send')
                            models.AssignInternal.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),job_id=job_obj,recruiter_id=User.objects.get(id=send_email.id),defaults={'user_id':User.objects.get(id=request.user.id),'send_email':False})
                            continue
                # Notification
                description = "You have been assigned to  "+job_obj.job_title+" Job"
                job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
                if job_obj.contact_name.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                                    job_obj.id))
                if job_obj.job_owner.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                                    job_obj.id))
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        description = "You have been assigned to  "+job_obj.job_title+" Job"
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                                    job_obj.id))
                    if i.recruiter_type_external :
                        description = "You have been assigned to  "+job_obj.job_title+" Job"
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/agency/job_view/" + str(
                                                                                    job_obj.id))
                    # closedate=datetime.datetime.combine(datetime.datetime.strptime(str(interview_schedule_obj.date),'%Y-%m-%d').date())
                    # closedate = closedate.astimezone(pytz.utc)
                    # Scheduler.add_job(
                    #                     closejob,
                    #                     trigger=DateTrigger(run_date=closedate),
                    #                     args = [job_obj],
                    #                     misfire_grace_time=6000,
                    #                     id='company_jobid_'+str(job_obj.id)
                    #                     # replace_existing=True
                    #                 )
                return redirect('company:job_openings_table')
        return render(request, 'company/ATS/job_view.html', context)
    else:
        return redirect('company:add_edit_profile')

def closejob(job_obj):
    job_obj.close_job=True
    job_obj.close_job_targetdate=True
    job_obj.close_job_at=datetime.datetime.now()
    job_obj.save()
    # Notification
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    to_email=[]
    job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
    description = "This Job "+job_obj.job_title+" has been closed. No more action required!"
    to_email.append(job_obj.contact_name.email)
    to_email.append(job_obj.job_owner.email)
    if job_obj.contact_name.id != request.user.id:
        
        notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                        job_obj.id))
    if job_obj.job_owner.id != request.user.id:
        notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                        job_obj.id))
    all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
    for i in all_assign_users:
        to_email.append(i.recruiter_id.email)
        if i.recruiter_type_internal:
            if i.recruiter_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                        job_obj.id))
        if i.recruiter_type_external :
            if i.recruiter_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/agency/job_view/" + str(
                                                                        job_obj.id))
    applied_candidates=models.AppliedCandidate.objects.filter(company_id=job_obj.company_id,job_id=job_obj)
    for applied_candidate in applied_candidates:
        to_email.append(applied_candidate.candidate.email)
    to_email=list(set(to_email))
    mail_subject = job_obj.job_title + " has been closed"
    html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"The job you are working with is been closed by "+job_obj.company_id.company_id.company_name+". No action required from your end."})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
    msg.attach_alternative(html_content, "text/html")
    # try:
    msg.send()
  
def assign_job(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if request.method=='POST':
            job_obj=models.JobCreation.objects.get(id=request.POST.get('job_obj'),company_id=models.Company.objects.get(user_id=request.user.id))
            for assign_id in request.POST.getlist('external-selector-1'):
                models.CompanyAssignJob.objects.filter(job_id=job_obj,
                                                    company_id=models.Company.objects.get(user_id=request.user.id),
                                                    recruiter_type_external=True,
                                                    recruiter_id=User.objects.get(id=int(assign_id))).delete()
                models.CompanyAssignJob.objects.create(job_id=job_obj,
                                                    company_id=models.Company.objects.get(user_id=request.user.id),
                                                    user_id=User.objects.get(id=request.user.id),
                                                    recruiter_type_external=True,
                                                    recruiter_id=User.objects.get(id=int(assign_id)))
            for assign_id in request.POST.getlist('internal-selector-1'):
                models.CompanyAssignJob.objects.filter(job_id=job_obj,
                                                    company_id=models.Company.objects.get(user_id=request.user.id),
                                                    recruiter_type_internal=True,
                                                    recruiter_id=User.objects.get(id=int(assign_id))).delete()
                models.CompanyAssignJob.objects.create(job_id=job_obj,
                                                    company_id=models.Company.objects.get(user_id=request.user.id),
                                                    user_id=User.objects.get(id=request.user.id),
                                                    recruiter_type_internal=True,
                                                    recruiter_id=User.objects.get(id=int(assign_id)))
            if job_obj.is_publish:
                for j in request.POST.getlist('external-selector-1'):
                    get_external=models.CompanyAssignJob.objects.get(job_id=job_obj,
                                                        company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id),
                                                        recruiter_type_external=True,
                                                        recruiter_id=User.objects.get(id=int(j)))
                    if get_external.recruiter_type_external:
                        get_recruiter = models.CompanyAssignJob.objects.get(id=get_external.id)
                        send_email = User.objects.get(id=j)
                        mail_subject = 'You have been invited to a new job'
                        # current_site = get_current_site(request)You have been invited to work on new Job”” In Company”” by “”. Please accept it to get started.
                        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"You have been invited to work on new Job "+job_obj.job_title+" In Company "+job_obj.company_id.company_id.company_name+ " by "+request.user.first_name+" "+request.user.last_name+". Please accept it to get started."})
                        to_email = send_email.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        # try:
                        msg.send()
                        models.AssignExternal.objects.update_or_create(
                            company_id=models.Company.objects.get(user_id=request.user.id), job_id=job_obj,
                            recruiter_id=AgencyModels.Agency.objects.get(user_id=send_email.id),
                            defaults={'user_id': User.objects.get(id=request.user.id), 'send_email': True})
                for j in request.POST.getlist('internal-selector-1'):
                    get_external = models.CompanyAssignJob.objects.get(job_id=job_obj,
                                                                    company_id=models.Company.objects.get(
                                                                        user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id),
                                                                    recruiter_type_internal=True,
                                                                    recruiter_id=User.objects.get(id=int(j)))
                    if get_external.recruiter_type_internal:
                        get_recruiter = models.CompanyAssignJob.objects.get(id=get_external.id)
                        send_email = User.objects.get(id=j)
                        mail_subject = 'You have been assigned new job'
                        # current_site = get_current_site(request)
                        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"You have been assigned to new Job "+job_obj.job_title+" By "+request.user.first_name + ' '+request.user.last_name + "Please login to review and submit new candidates."})
                        to_email = send_email.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        try:
                            msg.send()
                            models.AssignInternal.objects.update_or_create(
                                company_id=models.Company.objects.get(user_id=request.user.id), job_id=job_obj,
                                recruiter_id=User.objects.get(id=send_email.id),
                                defaults={'user_id': User.objects.get(id=request.user.id), 'send_email': True})
                        except:
                            print('not send')
                            models.AssignInternal.objects.update_or_create(
                                company_id=models.Company.objects.get(user_id=request.user.id), job_id=job_obj,
                                recruiter_id=User.objects.get(id=send_email.id),
                                defaults={'user_id': User.objects.get(id=request.user.id), 'send_email': False})
                            continue
            return redirect('company:created_job_view', id=job_obj.id)
    else:
        return redirect('company:add_edit_profile')
# ########################    JOB Creation End   ########################


# ########################    Workflow Management    ########################


def workflow_list(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Workflow':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            data = []
            flows = models.Workflows.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id)).order_by('-created_at')
            for flow in flows:
                stages = models.WorkflowStages.objects.filter(workflow=flow,display=True,company_id=models.Company.objects.get(user_id=request.user.id)).order_by('sequence_number')
                stage_list = [stage.stage_name for stage in stages]
                data.append({'workflow_id': flow.id, 'workflow_name': flow.name,'is_configured':flow.is_configured, 'stages': stage_list})
            context['stage']=data
            return render(request, 'company/ATS/workflow_list.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def workflow_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):    
        Workflows_obj = models.Workflows.objects.get(id=id)
        stages = models.WorkflowStages.objects.filter(workflow=Workflows_obj, display=True).order_by('sequence_number')
        workflow_data = []
        for stage in stages:
            stage_dict = {'stage': stage, 'data': '','workflow_configuration':''}
            if stage.stage.name == 'MCQ Test':
                mcq_template = models.ExamTemplate.objects.get(company_id=stage.company_id, template=stage.template,
                                                            stage=stage.stage)
                total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                if mcq_template.question_wise_time:
                    get_template_que = models.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)

                    for time in get_template_que:
                        total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                        "%M:%S")
                    stage_dict['mcq_time'] = total_time.time()
                else:
                    stage_dict['mcq_time'] = datetime.datetime.strptime(mcq_template.duration, "%M:%S").time()
                if mcq_template.marking_system == "question_wise":
                    get_template_que = models.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
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
                stage_dict['workflow_configuration'] = models.WorkflowConfiguration.objects.get(workflow_stage=stage)
                stage_dict['data'] = mcq_template

            if stage.stage.name == 'Descriptive Test':
                descriptive_template = models.DescriptiveExamTemplate.objects.get(
                    company_id=stage.company_id,
                    stage=stage.stage,
                    template=stage.template)
                total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')

                get_template_que = models.DescriptiveExamQuestionUnit.objects.filter(
                    template=descriptive_template.template.id)

                for time in get_template_que:
                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time, "%M:%S")
                stage_dict['descriptive_time'] = total_time.time()

                get_template_que = models.DescriptiveExamQuestionUnit.objects.filter(
                    template=descriptive_template.template.id)
                total_marks = 0
                for mark in get_template_que:
                    total_marks += int(mark.question_mark)
                stage_dict['descriptive_marks'] = total_marks
                stage_dict['data'] = descriptive_template

            if stage.stage.name == 'Image Test':
                image_template = models.ImageExamTemplate.objects.get(company_id=stage.company_id,
                                                                    stage=stage.stage,
                                                                    template=stage.template)
                total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                if image_template.question_wise_time:
                    get_template_que = models.ImageExamQuestionUnit.objects.filter(
                        template=image_template.template.id)

                    for time in get_template_que:
                        total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                        "%M:%S")
                    stage_dict['image_time'] = total_time.time()
                else:
                    stage_dict['image_time'] = datetime.datetime.strptime(image_template.duration, "%M:%S").time()
                if image_template.marking_system == "question_wise":
                    get_template_que = models.ImageExamQuestionUnit.objects.filter(
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
                stage_dict['workflow_configuration'] = models.WorkflowConfiguration.objects.get(workflow_stage=stage)
                stage_dict['data'] = image_template

            if stage.stage.name == 'Audio Test':
                audio_template = models.AudioExamTemplate.objects.get(company_id=stage.company_id,
                                                                    stage=stage.stage,
                                                                    template=stage.template)

                get_template_que = models.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                total_marks = 0
                for mark in get_template_que:
                    total_marks += int(mark.question_mark)
                stage_dict['audio_marks'] = total_marks
                stage_dict['data'] = audio_template

            if stage.stage.name == 'Coding Test':
                coding_template = models.CodingExamConfiguration.objects.get(company_id=stage.company_id,
                                                                            template_id=stage.template)
                if coding_template.assignment_type == 'marks':
                    coding_que_marks = models.CodingExamQuestions.objects.filter(
                        coding_exam_config_id=coding_template.id)
                    total_marks = 0
                    for i in coding_que_marks:
                        total_marks += int(i.marks)
                    stage_dict['total_marks'] = total_marks
                else:
                    coding_que_rating = models.CodingScoreCard.objects.filter(coding_exam_config_id=coding_template)
                    stage_dict['coding_que_rating'] = coding_que_rating

                stage_dict['workflow_configuration'] = models.WorkflowConfiguration.objects.get(workflow_stage=stage)
                stage_dict['data'] = coding_template


            if stage.stage.name == 'Interview':
                print(stage.template)
                interview_template = models.InterviewTemplate.objects.get(company_id=stage.company_id,template_id=stage.template)
                interview_scorecards = models.InterviewScorecard.objects.filter(interview_template=interview_template)
                stage_dict['data'] = interview_template
                stage_dict['interview_scorecards'] = interview_scorecards

            workflow_data.append(stage_dict)

        context['workflow_data'] = workflow_data
        return render(request, 'company/ATS/workflow_view.html',context)
    else:
        return redirect('company:add_edit_profile')

def create_workflow(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Workflow':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
        if context['Add']:
            if request.method == 'POST':
                workflow_data = json.loads(request.body.decode('UTF-8'))
                workflow_obj = models.Workflows.objects.create(name=workflow_data['name'],
                                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id))
                first = True
                count = 1
                workflow_data = workflow_data['data']
                for data in workflow_data:
                    print('\n\n\nlen', len(workflow_data))
                    if len(workflow_data) == 1:
                        stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name='Job Applied', workflow=workflow_obj,
                                                            stage=stage_obj, sequence_number=count, display=False)
                        count += 1

                        stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                        category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                        template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name=data['stage_name'], workflow=workflow_obj,
                                                            stage=stage_obj,
                                                            category=category_obj, template=template_obj,
                                                            sequence_number=count)
                        count += 1

                        stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name='Job Offer', workflow=workflow_obj,
                                                            stage=stage_obj, sequence_number=count, display=False)
                        count += 1
                    else:
                        if first:
                            print('first called', data)
                            stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                            models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name='Job Applied', workflow=workflow_obj,
                                                                stage=stage_obj, sequence_number=count,display=False)
                            first = False
                            count += 1

                            stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                            category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                            template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                            models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name=data['stage_name'], workflow=workflow_obj,
                                                                stage=stage_obj,
                                                                category=category_obj, template=template_obj,
                                                                sequence_number=count)
                            count += 1
                        elif data == workflow_data[-1]:
                            stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                            category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                            template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                            models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name=data['stage_name'], workflow=workflow_obj,
                                                                stage=stage_obj,
                                                                category=category_obj, template=template_obj,
                                                                sequence_number=count)
                            count += 1

                            stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                            models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name='Job Offer', workflow=workflow_obj,
                                                                stage=stage_obj, sequence_number=count,display=False)
                            count += 1
                        else:
                            stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                            category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                            template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                            models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name=data['stage_name'], workflow=workflow_obj,
                                                                stage=stage_obj,
                                                                category=category_obj, template=template_obj,
                                                                sequence_number=count)
                            count += 1
                
                request.session['workflow_configure'] = workflow_obj.id
                print("the set session valyue",request.session['workflow_configure'])
                return HttpResponse(True)
                # return redirect("company:workflow_configuration")
            return render(request, 'company/ATS/create_workflow.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def edit_workflow(request, id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        workflow_obj = models.Workflows.objects.get(id=id)
        get_activejob=models.JobWorkflow.objects.filter(workflow_id=workflow_obj,job_id__close_job_targetdate=False,job_id__close_job=False)
        if get_activejob:
            return HttpResponse(False)
        stages = models.WorkflowStages.objects.filter(workflow=workflow_obj,display=True)
        if request.method == 'POST':
            workflow_data = json.loads(request.body.decode('UTF-8'))
            print('\n\n workflow data1', workflow_data['data'])
            print('\n\n workflow name', workflow_data['name'])

            # workflow
            workflow_obj = models.Workflows.objects.get(id=id)
            workflow_obj.name = workflow_data['name']
            workflow_obj.is_configured = False
            workflow_obj.save()

            # stages

            models.WorkflowStages.objects.filter(workflow=workflow_obj).delete()
            count = 1
            first = True
            workflow_data = workflow_data['data']
            for data in workflow_data:
                print('\n\n\nlen', len(workflow_data))
                if len(workflow_data) == 1:
                    stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                    models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id),
                                                        stage_name='Job Applied', workflow=workflow_obj,
                                                        stage=stage_obj, sequence_number=count, display=False)
                    count += 1

                    stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                    category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                    template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                    models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id),
                                                        stage_name=data['stage_name'], workflow=workflow_obj,
                                                        stage=stage_obj,
                                                        category=category_obj, template=template_obj,
                                                        sequence_number=count)
                    count += 1

                    stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                    models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id),
                                                        stage_name='Job Offer', workflow=workflow_obj,
                                                        stage=stage_obj, sequence_number=count, display=False)
                    count += 1
                else:
                    if first:
                        print('first called', data)
                        stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name='Job Applied', workflow=workflow_obj,
                                                            stage=stage_obj, sequence_number=count, display=False)
                        first = False
                        count += 1

                        stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                        category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                        template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name=data['stage_name'], workflow=workflow_obj,
                                                            stage=stage_obj,
                                                            category=category_obj, template=template_obj,
                                                            sequence_number=count)
                        count += 1
                    elif data == workflow_data[-1]:
                        stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                        category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                        template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name=data['stage_name'], workflow=workflow_obj,
                                                            stage=stage_obj,
                                                            category=category_obj, template=template_obj,
                                                            sequence_number=count)
                        count += 1

                        stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name='Job Offer', workflow=workflow_obj,
                                                            stage=stage_obj, sequence_number=count, display=False)
                        count += 1
                    else:
                        stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                        category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                        template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                        models.WorkflowStages.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name=data['stage_name'], workflow=workflow_obj,
                                                            stage=stage_obj,
                                                            category=category_obj, template=template_obj,
                                                            sequence_number=count)
                        count += 1
            # current_site = get_current_site(request)
            # header=request.is_secure() and "https" or "http"    
            # all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            # for i in all_internal_users:
            #     description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Create Workflow"
            #     if i.employee_id.id != request.user.id:
            #         notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Workflow" + str(workflow_obj.id),
            #                                                             description=description,
            #                                                             target_url=header+"://"+current_site.domain+"/company/workflow_view/"+str(workflow_obj.id))            
            request.session['workflow_configure'] = workflow_obj.id
            return HttpResponse(True)
        context['stages']= stages
        context['workflow_obj']= workflow_obj,
        context['is_edit']= True
        return render(request, 'company/ATS/create_workflow.html',context )
    else:
        return redirect('company:add_edit_profile')

def get_workflow_data(request):
    stages_data = []
    category_data = []
    template_data = []
    stages = CandidateModels.Stage_list.objects.filter(active=True).exclude(name__in=["Job Creation"])
    for i in stages:
        # stage
        if models.TemplateCategory.objects.filter(stage=i.id,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
            stage_dict = {'key': i.id, 'stage_name': i.name}
            stages_data.append(stage_dict)
            print('satge name', i.name)

            # category
            categories = models.TemplateCategory.objects.filter(stage=i.id,company_id=models.Company.objects.get(user_id=request.user.id))
            cate_list = []
            for cat in categories:
                if models.Template_creation.objects.filter(category=cat.id,status=True).exists():
                    cate_dict = {'key': cat.id, 'cate_name': cat.name}
                    cate_list.append(cate_dict)
                tem_list = []
                templates = models.Template_creation.objects.filter(category=cat.id,status=True)
                for temp in templates:
                    tem_dict = {'key': temp.id, 'temp_name': temp.name}
                    tem_list.append(tem_dict)
                temp_dict = {'cateKey': cat.id, 'temp_list': tem_list}
                template_data.append(temp_dict)
            categ_dict = {'stageKey': i.id, 'cate_list': cate_list}
            category_data.append(categ_dict)

    # print('\n\ncategory_data', category_data)
    print('\n\ntemplate_data', template_data)
    return JsonResponse(
        {'stages_data': list(stages_data), 'category_data': list(category_data), 'template_data': list(template_data)})


def workflow_configuration(request,workflow_id=None):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if workflow_id == None:
            workflow_id = request.session.get('workflow_configure')
        if workflow_id:
            workflow_obj = models.Workflows.objects.get(id=workflow_id)
            workflow_stages = models.WorkflowStages.objects.filter(workflow=workflow_obj,display=True)
            internaluser=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)))
            workflow_data = []
            for stage in workflow_stages:
                stage_dict = {'stage': stage, 'data': ''}
                if stage.stage.name == 'MCQ Test':
                    print('aaaaaaaaaaa',stage.company_id,'-------',stage.template,'--------',stage.stage)
                    mcq_template = models.ExamTemplate.objects.get(company_id=stage.company_id,template=stage.template,
                                                                stage=stage.stage)
                    total_time=datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                    time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                    if mcq_template.question_wise_time:
                        get_template_que=models.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
                    
                        for time in get_template_que:
                            total_time=total_time-time_zero+datetime.datetime.strptime(time.question_time, "%M:%S")
                        stage_dict['mcq_time']=total_time.time()
                    else:
                        stage_dict['mcq_time']=datetime.datetime.strptime(mcq_template.duration, "%M:%S").time()
                    if mcq_template.marking_system=="question_wise":
                        get_template_que=models.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
                        total_marks=0
                        for mark in get_template_que:
                            total_marks+=int(mark.question_mark)
                        stage_dict['mcq_marks']=total_marks
                    else:
                        print(mcq_template.marking_system)
                        stage_dict['mcq_marks']=(int(mcq_template.basic_questions_count)*int(mcq_template.basic_question_marks))+(int(mcq_template.intermediate_questions_count)*int(mcq_template.intermediate_question_marks))+(int(mcq_template.advanced_questions_count)*int(mcq_template.advanced_question_marks))
                        
                    stage_dict['data'] = mcq_template

                if stage.stage.name == 'Descriptive Test':
                    descriptive_template = models.DescriptiveExamTemplate.objects.get(
                        company_id=stage.company_id,
                        stage=stage.stage,
                        template=stage.template)
                    total_time=datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                    time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                    
                    get_template_que=models.DescriptiveExamQuestionUnit.objects.filter(template=descriptive_template.template.id)
                    
                    for time in get_template_que:
                        total_time=total_time-time_zero+datetime.datetime.strptime(time.question_time, "%M:%S")
                    stage_dict['descriptive_time']=total_time.time()
                
                    get_template_que=models.DescriptiveExamQuestionUnit.objects.filter(template=descriptive_template.template.id)
                    total_marks=0
                    for mark in get_template_que:
                        total_marks+=int(mark.question_mark)
                    stage_dict['descriptive_marks']=total_marks
                    stage_dict['data'] = descriptive_template

                if stage.stage.name == 'Image Test':
                    image_template = models.ImageExamTemplate.objects.get(company_id=stage.company_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)
                    total_time=datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                    time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                    if image_template.question_wise_time:
                        get_template_que=models.ImageExamQuestionUnit.objects.filter(template=image_template.template.id)
                    
                        for time in get_template_que:
                            total_time=total_time-time_zero+datetime.datetime.strptime(time.question_time, "%M:%S")
                        stage_dict['image_time']=total_time.time()
                    else:
                        stage_dict['image_time']=datetime.datetime.strptime(image_template.duration, "%M:%S").time()
                    if image_template.marking_system=="question_wise":
                        get_template_que=models.ImageExamQuestionUnit.objects.filter(template=image_template.template.id)
                        total_marks=0
                        for mark in get_template_que:
                            total_marks+=int(mark.question_mark)
                        stage_dict['image_marks']=total_marks
                    else:
                        stage_dict['image_marks']=(int(image_template.basic_questions_count)*int(image_template.basic_question_marks))+(int(image_template.intermediate_questions_count)*int(image_template.intermediate_question_marks))+(int(image_template.advanced_questions_count)*int(image_template.advanced_question_marks))
                        
                    stage_dict['data'] = image_template

                if stage.stage.name == 'Audio Test':
                    print("company_id",stage.company_id)
                    print("stage",stage.stage)
                    print("templte ",stage.template)
                    audio_template = models.AudioExamTemplate.objects.get(company_id=stage.company_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)
                    
                    get_template_que = models.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                    total_marks=0
                    for mark in get_template_que:
                        total_marks+=int(mark.question_mark)
                    stage_dict['audio_marks']=total_marks
                    stage_dict['data'] = audio_template

                if stage.stage.name == 'Coding Test':
                    print('\n\n\nstage.company_id',  stage.company_id)
                    print('template',  stage.template)
                    coding_template = models.CodingExamConfiguration.objects.get(company_id=stage.company_id,
                                                                                template_id=stage.template)
                    if coding_template.assignment_type=='marks':
                        coding_que_marks=models.CodingExamQuestions.objects.filter(coding_exam_config_id=coding_template.id)
                        total_marks=0
                        for i in coding_que_marks:
                            total_marks+=int(i.marks)
                        stage_dict['total_marks']=total_marks
                    else:
                        coding_que_rating=models.CodingScoreCard.objects.filter(coding_exam_config_id=coding_template)
                        stage_dict['coding_que_rating']=coding_que_rating
                    stage_dict['data'] = coding_template

                workflow_data.append(stage_dict)

            if request.method == 'POST':
                for stage in workflow_stages:
                    if stage.stage.name == 'JCR':
                        if request.POST.get('jcr-action') == 'auto':
                            is_automation = True
                            shortlist = request.POST.get('jcr-short-list')
                            onhold = request.POST.get('jcr-on-hold')
                            reject = request.POST.get('jcr-rejected')
                        else:
                            is_automation = False
                            shortlist = None
                            onhold = None
                            reject = None
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,
                                                                    company_id=stage.company_id,
                                                                    is_automation=is_automation,
                                                                    shortlist=shortlist,
                                                                    onhold=onhold,
                                                                    reject=reject)

                    if stage.stage.name == 'Prerequisites':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,company_id=stage.company_id,)

                    if stage.stage.name == 'MCQ Test':
                        if request.POST.get('mcq-action-'+str(stage.template.id)) == 'auto':
                            is_automation = True
                            shortlist = request.POST.get('mcq-short-list-'+str(stage.template.id))
                            # onhold = request.POST.get('mcq-on-hold')
                            reject = request.POST.get('mcq-rejected-'+str(stage.template.id))
                            print(shortlist,reject)
                        else:
                            is_automation = False
                            shortlist = None
                            # onhold = None
                            reject = None
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage, company_id=stage.company_id,
                                                                    is_automation=is_automation,
                                                                    shortlist=shortlist,
                                                                    # onhold=onhold,
                                                                    reject=reject)

                    if stage.stage.name == 'Image Test':
                        if request.POST.get('image-action-'+str(stage.template.id)) == 'auto':
                            is_automation = True
                            shortlist = request.POST.get('image-short-list-'+str(stage.template.id))
                            # onhold = request.POST.get('image-on-hold')
                            reject = request.POST.get('image-rejected-'+str(stage.template.id))
                        else:
                            is_automation = False
                            shortlist = None
                            # onhold = None
                            reject = None

                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,company_id=stage.company_id,
                                                                    is_automation=is_automation,
                                                                    shortlist=shortlist,
                                                                    # onhold=onhold,
                                                                    reject=reject)

                    if stage.stage.name == 'Paragraph MCQ Test':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,company_id=stage.company_id)

                    if stage.stage.name == 'Descriptive Test':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,company_id=stage.company_id)

                    if stage.stage.name == 'Coding Test':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,company_id=stage.company_id)

                    if stage.stage.name == 'Interview':
                        interviewer = request.POST.getlist('interviewers')
                        interviewer_create=models.WorkflowConfiguration.objects.create(workflow_stage=stage,company_id=stage.company_id)
                        for user_id in interviewer:
                            interviewer_create.interviewer.add(User.objects.get(id=int(user_id)))
                workflow_obj.is_configured = True
                workflow_obj.save()
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"  
                all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
                get_email=[]
                for j in all_internaluser:
                    get_email.append(User.objects.get(id=j).email)
                mail_subject = 'New Workflow Added'
                link=header+"://"+current_site.domain+"/company/workflow_view/"+str(workflow_obj.id)
                html_content = render_to_string('company/email/workflow_create.html',{'username':request.user.first_name+' '+request.user.last_name,'workflowname':workflow_obj.name,'workflowid':workflow_id,'link':link  })
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send() 
                description = workflow_obj.name+" has been added to your workspace"
                all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
                for i in all_internal_users:
                    if i.employee_id.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Workflow",
                                                                            description=description,image="/static/notifications/icon/company/Workflow.png",
                                                                            target_url=header+"://"+current_site.domain+"/company/workflow_view/"+str(workflow_obj.id))
                if 'workflow_configure' in request.session:
                    del request.session['workflow_configure']
                return redirect('company:workflow_list')
            context['internaluser']=internaluser
            context['workflow_name']= workflow_obj.name
            context['workflow_stages']= workflow_stages
            context['workflow_data']=workflow_data
            return render(request, 'company/ATS/workflow_configuration.html', context)
        else:
            return render(request, 'accounts/404.html')
    else:
        return redirect('company:add_edit_profile')

def workflow_selection(request, id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        workflows = models.Workflows.objects.filter(is_configured=True,company_id=models.Company.objects.get(user_id=request.user.id))
        context['workflows']= workflows
        job_obj = models.JobCreation.objects.get(id=id)
        if models.JobWorkflow.objects.filter(job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
            context['selectedworkflows']=models.JobWorkflow.objects.get(job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id))
        if request.method == 'POST':
            if request.POST.get('workflowtype')=='onthego':
                job_workflow_obj,created = models.JobWorkflow.objects.update_or_create(job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id),
                                                        defaults={'onthego':True, 'workflow_id':None,'user_id':User.objects.get(id=request.user.id)})
                if request.POST.get('application_review') == 'application_review':
                    job_workflow_obj.is_application_review = True
                    job_workflow_obj.save()
            if request.POST.get('workflowtype')=='withworkflow':
                workflow = models.Workflows.objects.get(id=request.POST.get('selected_workflow'))
                job_workflow_obj,created = models.JobWorkflow.objects.update_or_create(job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id),
                                                            defaults={'workflow_id':workflow,'withworkflow':True,'user_id':User.objects.get(id=request.user.id)})
                if request.POST.get('application_review') == 'application_review':
                    job_workflow_obj.is_application_review = True
                    job_workflow_obj.save()
            return redirect('company:created_job_view', id=job_obj.id)
        return render(request, 'company/ATS/workflow_selection.html', context)
    else:
        return redirect('company:add_edit_profile')

# ########################    Workflow Management End   ########################


# ################################################################################


# PRE REQUISITES VIEW


def pre_requisites(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        return render(request, 'company/ATS/prerequisites-form.html',context)
    else:
        return redirect('company:add_edit_profile')

def save_pre_requisites(request):
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    if request.method == 'POST':
        data = json.loads(request.body.decode('UTF-8'))
        print("data", data)
        template_data = data[0]['template-data']
        print("tempplate _data ", template_data)
        pre_requisite, created = models.PreRequisites.objects.get_or_create(
            stage=CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid'])),
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid'])),
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid'])),
            company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
        pre_requisite.data = json.dumps(data[0]['template-data'])
        pre_requisite.html_data = data[0]['html-data']
        pre_requisite.save()
        pre_requisite.template.status = True
        pre_requisite.template.save()
        
        data = {}
        data['status'] = True
        data['url'] = header+"://"+current_site.domain+'/company/template_listing/'
        template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        description = template_name.name+" has been added to your workspace"
        all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
        for i in all_internal_users:
            if i.employee_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Pre-Requisites Template",
                                                                    description=description,image="/static/notifications/icon/company/Template.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/view_pre_requisites/"+str(pre_requisite.id))
        all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
        get_email=[]
        
        for j in all_internaluser:
            get_email.append(User.objects.get(id=j).email)
        link=header+"://"+current_site.domain+"/company/view_pre_requisites/"+str(pre_requisite.id)
        mail_subject = 'New Template Added'
        html_content = render_to_string('company/email/template_create.html',{'template_type':'Eligibility Criteria','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        del request.session['create_template']
        return HttpResponse(json.dumps(data))
    else:
        data = {}
        data['status'] = False
        data['url'] = ''
        return HttpResponse(json.dumps(data))


def view_pre_requisites(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        pre_requisite = models.PreRequisites.objects.get(id=id,company_id=models.Company.objects.get(user_id= request.user))
        context["pre_requisite"] = pre_requisite
        return render(request,"company/ATS/prerequisites-preview-template.html",context)
    else:
        return redirect('company:add_edit_profile')

# jcr
def get_jcr_data(request):
    context = {}
    jcr_obj_temp = models.JCR.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                             stage=CandidateModels.Stage_list.objects.get(
                                                 id=int(request.session['create_template']['stageid'])),
                                             category=models.TemplateCategory.objects.get(
                                                 id=int(request.session['create_template']['categoryid'])),
                                             template=models.Template_creation.objects.get(
                                                 id=int(request.session['create_template']['templateid']))).order_by(
        '-id')
    jcr_categories = jcr_obj_temp.filter(pid=None).order_by('id')
    print("jcrrrrrrrr all daaaata", jcr_obj_temp)
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
        print("kabkjasdadadakasdjkasdkljd;ldk;laskd;ldksd===================================ndlkmnklmadasdm")
        context['getStoreData'] = 'null'
    getStoreData = json.dumps(context)
    return getStoreData


def jcr(request):
    print("===============")
    if request.method == 'POST':
        jcr_data = json.loads(request.body.decode('UTF-8'))
        print(jcr_data['updateCategoryList'])
        for main_data in jcr_data['updateCategoryList']:
            models.JCR.objects.update_or_create(name=main_data['cat_name'],
                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                stage=CandidateModels.Stage_list.objects.get(
                                                    id=int(request.session['create_template']['stageid'])),
                                                category=models.TemplateCategory.objects.get(
                                                    id=int(request.session['create_template']['categoryid'])),
                                                template=models.Template_creation.objects.get(
                                                    id=int(request.session['create_template']['templateid'])),
                                                defaults={'user_id':User.objects.get(id=request.user.id),
                                                'name': main_data['cat_name'],
                                                          'ratio': main_data['cat_value']})
        return JsonResponse(get_jcr_data(request), safe=False)
    return render(request, 'company/ATS/jcr_wizards.html', {'getStoreData': get_jcr_data(request)})


def insert_jcr(request):
    context = {}
    jcr_data = []
    jcr_obj = models.JCR.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                        stage=CandidateModels.Stage_list.objects.get(
                                            id=int(request.session['create_template']['stageid'])),
                                        category=models.TemplateCategory.objects.get(
                                            id=int(request.session['create_template']['categoryid'])),
                                        template=models.Template_creation.objects.get(
                                            id=int(request.session['create_template']['templateid'])),
                                        pid=None).order_by(
        'id')
    if jcr_obj.exists():
        for record in jcr_obj:
            obj_dict = {}
            obj_dict['cat_name'] = record.name
            obj_dict['cat_value'] = record.ratio
    if request.method == 'POST':
        jcr_data = json.loads(request.body.decode('UTF-8'))
        print(jcr_data['getStoreData'])
        for record in jcr_data['getStoreData']:
            for add_item in record['addDetailsItem']:
                if add_item['id']:
                    # get_key = models.JCR.objects.get(id=int(record['id']))
                    models.JCR.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                        stage=CandidateModels.Stage_list.objects.get(
                                                            id=int(request.session['create_template']['stageid'])),
                                                        category=models.TemplateCategory.objects.get(
                                                            id=int(request.session['create_template']['categoryid'])),
                                                        template=models.Template_creation.objects.get(
                                                            id=int(request.session['create_template']['templateid'])),
                                                        id=int(add_item['id']), defaults={'user_id':User.objects.get(id=request.user.id),
                            'name': add_item['cat_type'], 'ratio': add_item['cate_percent'], 'flag': None,
                        })
                else:
                    get_key = models.JCR.objects.get(name=record['cat_name'], company_id=models.Company.objects.get(user_id=request.user.id),
                                                     stage=CandidateModels.Stage_list.objects.get(
                                                         id=int(request.session['create_template']['stageid'])),
                                                     category=models.TemplateCategory.objects.get(
                                                         id=int(request.session['create_template']['categoryid'])),
                                                     template=models.Template_creation.objects.get(
                                                         id=int(request.session['create_template']['templateid'])))
                    models.JCR.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                        stage=CandidateModels.Stage_list.objects.get(
                                                            id=int(request.session['create_template']['stageid'])),
                                                        category=models.TemplateCategory.objects.get(
                                                            id=int(request.session['create_template']['categoryid'])),
                                                        template=models.Template_creation.objects.get(
                                                            id=int(request.session['create_template']['templateid'])),
                                                        pid=get_key, name=add_item['cat_type'], defaults={'user_id':User.objects.get(id=request.user.id),
                            'name': add_item['cat_type'], 'ratio': int(add_item['cate_percent']), 'flag': None,
                        })
                if add_item['cat_subtype']:
                    print("?>>>>>>>>>>>>>>>>>", add_item['cat_subtype'])
                    for cat_subtype in add_item['cat_subtype']:

                        if 'id' in [*cat_subtype] and cat_subtype['id']:
                            print("================", cat_subtype['id'])
                            models.JCR.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                stage=CandidateModels.Stage_list.objects.get(id=int(
                                                                    request.session['create_template']['stageid'])),
                                                                category=models.TemplateCategory.objects.get(
                                                                    id=int(request.session['create_template'][
                                                                               'categoryid'])),
                                                                template=models.Template_creation.objects.get(id=int(
                                                                    request.session['create_template']['templateid'])),
                                                                id=cat_subtype['id'],
                                                                defaults={'user_id':User.objects.get(id=request.user.id),
                                                                    'name': cat_subtype['question'],
                                                                    'ratio': cat_subtype['q_percent'], 'flag': None,
                                                                })
                        else:
                            get_item_key = models.JCR.objects.get(name=add_item['cat_type'], company_id=models.Company.objects.get(user_id=request.user.id),
                                                                  stage=CandidateModels.Stage_list.objects.get(id=int(
                                                                      request.session['create_template']['stageid'])),
                                                                  category=models.TemplateCategory.objects.get(
                                                                      id=int(request.session['create_template'][
                                                                                 'categoryid'])),
                                                                  template=models.Template_creation.objects.get(id=int(
                                                                      request.session['create_template'][
                                                                          'templateid'])))
                            models.JCR.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                stage=CandidateModels.Stage_list.objects.get(id=int(
                                                                    request.session['create_template']['stageid'])),
                                                                category=models.TemplateCategory.objects.get(
                                                                    id=int(request.session['create_template'][
                                                                               'categoryid'])),
                                                                template=models.Template_creation.objects.get(id=int(
                                                                    request.session['create_template']['templateid'])),
                                                                pid=get_item_key, name=cat_subtype['question'],
                                                                defaults={'user_id':User.objects.get(id=request.user.id),
                                                                    'name': cat_subtype['question'],
                                                                    'ratio': int(cat_subtype['q_percent']),
                                                                    'flag': cat_subtype['matching'],
                                                                })
                        if cat_subtype['details']:
                            for detail in cat_subtype['details']:
                                if 'id' in [*detail] and detail['id']:
                                    models.JCR.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                        stage=CandidateModels.Stage_list.objects.get(id=int(
                                                                            request.session['create_template'][
                                                                                'stageid'])),
                                                                        category=models.TemplateCategory.objects.get(
                                                                            id=int(request.session['create_template'][
                                                                                       'categoryid'])),
                                                                        template=models.Template_creation.objects.get(
                                                                            id=int(request.session['create_template'][
                                                                                       'templateid'])),
                                                                        id=detail['id'], defaults={'user_id':User.objects.get(id=request.user.id),
                                            'name': detail['title'], 'ratio': int(detail['percent']), 'flag': None,
                                        })
                                else:
                                    get_sub_item_key = models.JCR.objects.get(name=cat_subtype['question'],
                                                                              company_id=models.Company.objects.get(user_id=request.user.id),
                                                                              stage=CandidateModels.Stage_list.objects.get(
                                                                                  id=int(request.session[
                                                                                             'create_template'][
                                                                                             'stageid'])),
                                                                              category=models.TemplateCategory.objects.get(
                                                                                  id=int(request.session[
                                                                                             'create_template'][
                                                                                             'categoryid'])),
                                                                              template=models.Template_creation.objects.get(
                                                                                  id=int(request.session[
                                                                                             'create_template'][
                                                                                             'templateid'])))
                                    models.JCR.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                        stage=CandidateModels.Stage_list.objects.get(id=int(
                                                                            request.session['create_template'][
                                                                                'stageid'])),
                                                                        category=models.TemplateCategory.objects.get(
                                                                            id=int(request.session['create_template'][
                                                                                       'categoryid'])),
                                                                        template=models.Template_creation.objects.get(
                                                                            id=int(request.session['create_template'][
                                                                                       'templateid'])),
                                                                        pid=get_sub_item_key, name=detail['title'],
                                                                        defaults={'user_id':User.objects.get(id=request.user.id),
                                                                            'name': detail['title'],
                                                                            'ratio': int(detail['percent']),
                                                                            'flag': None,
                                                                        })
        models.Template_creation.objects.filter(
            stage=CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid'])),
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid'])),
            id=int(request.session['create_template']['templateid'])).update(status=True)
        data = {"true": "true", 'getStoreData': get_jcr_data(request)}
        return JsonResponse(json.dumps(data), safe=False)


def remove_jcr(request):
    print("=============================remove_jcr--------")
    if request.method == 'POST':
        jcr_data = json.loads(request.body.decode('UTF-8'))
        if jcr_data['deleteid']:
            models.JCR.objects.get(company_id=User.objects.get(id=request.user.id), stage=CandidateModels.Stage_list.objects.get(
                id=int(request.session['create_template']['stageid'])),
                                   category=models.TemplateCategory.objects.get(
                                       id=int(request.session['create_template']['categoryid'])),
                                   template=models.Template_creation.objects.get(
                                       id=int(request.session['create_template']['templateid'])),
                                   id=int(jcr_data['deleteid'])).delete()
            data = {"true": "true", 'getStoreData': get_jcr_data(request)}
            return JsonResponse(data)
        else:
            data = {"true": "false", 'getStoreData': get_jcr_data(request)}
            return JsonResponse(data)


def remove_sub_jcr(request):
    print("=============================remove_sub_jcr")
    if request.method == 'POST':
        jcr_data = json.loads(request.body.decode('UTF-8'))

        if jcr_data['deleteid']:
            models.JCR.objects.get(company_id=User.objects.get(id=request.user.id), stage=CandidateModels.Stage_list.objects.get(
                id=int(request.session['create_template']['stageid'])),
                                   category=models.TemplateCategory.objects.get(
                                       id=int(request.session['create_template']['categoryid'])),
                                   template=models.Template_creation.objects.get(
                                       id=int(request.session['create_template']['templateid'])),
                                   id=int(jcr_data['deleteid'])).delete()
            data = {"true": "true", 'getStoreData': get_jcr_data(request)}
            return JsonResponse(data)
        else:
            data = {"true": "false", 'getStoreData': get_jcr_data(request)}
            return JsonResponse(data)


def jcr_preview(request,template_id):
    context = {}
    jcr_obj_temp = models.JCR.objects.filter(template=models.Template_creation.objects.get(id=template_id)).order_by( '-id')
    jcr_categories = jcr_obj_temp.filter(pid=None).order_by('id')
    context['getStoreData'] = []
    for category in jcr_categories:
        if int(category.ratio) != 0:
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
    getStoreData = json.dumps(context['getStoreData'])

    return render(request, 'company/ATS/jcr-template-preview.html', {'getStoreData': getStoreData})


def template_listing(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Template':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            if 'create_template' in request.session:
                context['active_stageid']=request.session['create_template']['stageid']
                context['active_categoryid']=request.session['create_template']['categoryid']
            get_stage = CandidateModels.Stage_list.objects.filter(active=True).order_by('id')
            context['stage'] = get_stage
            get_category = models.TemplateCategory.objects.filter(
                company_id=models.Company.objects.get(user_id=request.user.id)).order_by('id')
            context['get_category']= get_category
            print('get_category>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',get_category)
            get_templates = models.Template_creation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            context['get_templates']= get_templates
            if request.method == 'POST':
                print('\n\n\nstage>>>', request.POST.get('stage'))
                print('\n\n\ncategory>>>', request.POST.get('category'))
                print('\n\n\ntemplate-name>>>', request.POST.get('template-name'))
                print('\n\n\ntemplate-description>>>', request.POST.get('template-description'))
                template_create = models.Template_creation.objects.create(name=request.POST.get('template-name'),
                                                                        description=request.POST.get('template-description'),
                                                                        stage=CandidateModels.Stage_list.objects.get(
                                                                            id=int(request.POST.get('stage'))),
                                                                        category=models.TemplateCategory.objects.get(
                                                                            id=int(request.POST.get('category'))),
                                                                        company_id=models.Company.objects.get(user_id=request.user.id),
                                                                            user_id=User.objects.get(id=request.user.id))
                stage = CandidateModels.Stage_list.objects.get(id=int(request.POST.get('stage')))
                if 'create_template' in request.session:
                    del request.session['create_template']
                request.session['create_template'] = {'stageid': template_create.stage.id,
                                                    'categoryid': template_create.category.id,
                                                    'templateid': template_create.id}
                
                print('stage name  >>>>>..', stage.name)
                data = {}
                data['status'] = True
                if str(stage.name).upper() == 'JOB CREATION':
                    return redirect('company:job_creation_template')
                if str(stage.name).upper() == 'JCR':
                    return redirect('company:jcr')
                if str(stage.name).upper() == 'PREREQUISITES':
                    return redirect('company:pre_requisites')
                if str(stage.name).upper() == 'MCQ TEST':
                    return redirect('company:add_exam_template')
                if str(stage.name).upper() == 'CODING TEST':
                    return redirect('company:coding_exam_configuration')
                if str(stage.name).upper() == 'DESCRIPTIVE TEST':
                    return redirect('company:descriptive_exam_template')
                if str(stage.name).upper() == 'IMAGE TEST':
                    return redirect('company:image_add_exam_template')
                if str(stage.name).upper() == 'AUDIO TEST':
                    return redirect('company:audio_exam_template')
                if str(stage.name).upper() == 'INTERVIEW':
                    return redirect('company:interview_template')
                if str(stage.name).upper() == 'CUSTOM':
                    return redirect('company:custom_template')
            return render(request, 'company/ATS/template-creation.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')
def add_category(request):
    if request.method == 'POST':
        category_name = json.loads(request.body.decode('UTF-8'))
        print("======================================", category_name)
        create_stage_id = models.TemplateCategory.objects.create(name=category_name['add_category'],
                                                                 stage=CandidateModels.Stage_list.objects.get(
                                                                     id=int(category_name['stage_id'])),
                                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id))
        create_stage_id.save()
        data = {}
        data['status'] = True
        data['cat_id'] = create_stage_id.id
        return HttpResponse(json.dumps(data))


def delete_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        models.TemplateCategory.objects.get(id=int(category_data['cat_id']),
                                            stage=CandidateModels.Stage_list.objects.get(id=int(category_data['stage_id'])),
                                            company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def update_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        print(category_data)
        category_get = models.TemplateCategory.objects.get(id=int(category_data['cat_id']),
                                                           stage=CandidateModels.Stage_list.objects.get(
                                                               id=int(category_data['stage_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id))
        category_get.name = category_data['cat_name']
        category_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def get_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        category_get = models.TemplateCategory.objects.filter(
            stage=CandidateModels.Stage_list.objects.get(id=int(category_data['stage_id'])),
            company_id=models.Company.objects.get(user_id=request.user.id))
        print("============------", category_get)
        data = {}
        data['status'] = True
        data['category_get'] = serializers.serialize('json', category_get)
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)


def get_job_template(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        print(category_data)
        template_data=[]
        get_job_template = models.Template_creation.objects.filter(category=models.TemplateCategory.objects.get(id=int(category_data['category'])),
            company_id=models.Company.objects.get(user_id=request.user.id))
        for template_get in get_job_template:
            template_data.append({'template_id':template_get.id,'template_name':template_get.name})
        print("============------", get_job_template)
        data = {}
        data['status'] = True
        data['get_job_template'] = template_data
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)

def job_template_view(request, template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
        if context['Add'] or context['Edit']:
            job_obj = models.JobCreationTemplate.objects.get(template=models.Template_creation.objects.get(id=template_id))
            context['job_obj']= job_obj
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
        return render(request, 'company/ATS/job-template-view.html', context)
    else:
        return redirect('company:add_edit_profile')
# def create_template(request):
#     if request.method == 'POST':
#         template_data = json.loads(request.body.decode('UTF-8'))
#         template_create = models.Template_creation.objects.create(name=template_data['template_name'],
#                                                                   description=template_data['template_discriiption'],
#                                                                   stage=CandidateModels.Stage_list.objects.get(
#                                                                       id=int(template_data['stage_id'])),
#                                                                   category=models.TemplateCategory.objects.get(
#                                                                       id=int(template_data['category_id'])),
#                                                                   company_id=User.objects.get(id=request.user.id))
#         print("============------", template_data)
#         template_create.save()
#         get_stage = CandidateModels.Stage_list.objects.get(id=int(template_data['stage_id']))
#         request.session['create_template'] = {'stageid': template_create.stage.id,
#                                               'categoryid': template_create.category.id,
#                                               'templateid': template_create.id}
#         data = {}
#         data['status'] = True
#         if str(get_stage.name).upper() == 'JCR':
#             return redirect('company:jcr')
#             # data['url'] = 'http://192.168.1.72:8000/company/jcr/'
#         if str(get_stage.name).upper() == 'PREREQUISITES':
#             return redirect('company:pre_requisites')
#             # data['url'] = 'http://192.168.1.72:8000/company/pre_requisites/'
#         # if str(get_stage.name).upper() == 'MCQ TEST':
#         #     data['url'] = 'http://192.168.1.72:8000/company/add_exam_template/'
#         #     return HttpResponse(json.dumps(data))
#         if str(get_stage.name).upper() == 'JOB CREATION':
#             return redirect('company:job_creation')
#             # data['url'] = 'http://192.168.1.72:8000/company/job_creation/'
#             # return HttpResponse(json.dumps(data))
#     else:
#         return HttpResponse(False)


def delete_template(request):
    data={}
    if request.method == 'POST':
        template_data = json.loads(request.body.decode('UTF-8'))
        get_workflow=models.WorkflowStages.objects.filter(template=int(template_data['template_id'])).values_list('workflow_id')
        get_job=models.JobWorkflow.objects.filter(workflow_id__in=get_workflow).values_list('job_id')
        job_status=models.JobCreation.objects.filter(id__in=get_job)
        print('get_workflow',get_workflow)
        print('get_job',get_job)
        active=''
        for jobstatus in job_status:
            print(jobstatus.status.name)
            if jobstatus.status.name=='In Progress':
                active=True
        print(active)
        if not active:
            delete_template=models.Template_creation.objects.get(id=int(template_data['template_id']),
                                             category=models.TemplateCategory.objects.get(
                                                 id=int(template_data['cat_id'])),
                                             stage=CandidateModels.Stage_list.objects.get(id=int(template_data['stage_id'])),
                                             company_id=models.Company.objects.get(user_id=request.user.id)).delete()
            if delete_template:
                data['status'] = True
            else:
                data['status'] = False
            
        else:
            data['status'] = 'replica'
        
        return JsonResponse(data)


def view_job(request, id):
    context = {}
    job_obj = models.JobCreation.objects.get(id=id)
    context['job_obj']=job_obj
    context['active_job_count'] = len(
        models.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=False,
                                                 close_job_targetdate=False,
                                                 is_publish=True))
    context['close_job_count'] = len(
        models.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=True))
    context['last_close_job'] = models.JobCreation.objects.filter(company_id=job_obj.company_id.id,
                                                                         close_job=True).order_by(
        '-close_job_at').first()
    context['latest_10_job'] = models.JobCreation.objects.filter(company_id=job_obj.company_id.id,
                                                                        close_job=False,
                                                                        close_job_targetdate=False,
                                                                        is_publish=True).order_by(
        '-publish_at')
    if 'view_job' in request.session:
        del request.session['view_job']
    if request.user.is_authenticated:
        if request.user.is_candidate:
            print("==========================")
            request.session['view_job']=job_obj.id
            request.session['job_type']='company'
            return redirect('candidate:job_view')
    else:
        return render(request, 'company/ATS/job-opening-view.html', context)


def add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.Paragraph_subject.objects.create(subject_name=subject_name['subject_name'],
                                                             company_id=models.Company.objects.get(user_id=request.user.id),
                                                             user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {}
        data['status'] = True
        data['subject_id'] = subject_id.id
        data['subject_name'] = subject_id.subject_name
        return HttpResponse(json.dumps(data))


def update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        subject_get = models.Paragraph_subject.objects.get(id=int(subject_data['sub_id']),
                                                           company_id=models.Company.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        # print(subject_data)
        models.Paragraph_subject.objects.get(id=int(subject_data['sub_id']),
                                             company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def list_paragraph(request):
    subject = models.Paragraph_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
    print(subject)
    return render(request, 'company/ATS/paragraph_card_list.html', {'subject': subject})


def preview_paragraph(request, id):
    if models.Paragraph_subject.objects.filter(id=id).exists():
        data = []
        subject_obj = models.Paragraph_subject.objects.get(id=id)
        paragraphs = models.Paragraph.objects.filter(subject=subject_obj)
        for para in paragraphs:
            questions = models.Paragraph_option.objects.filter(paragraph=para.id,
                                                               company_id=models.Company.objects.get(user_id=request.user.id))
            dict = {'para': para, 'questions': questions}
            data.append(dict)
    else:
        data = None
    return render(request, 'company/ATS/paragraph_preview_template.html', {'paragraphs': data, 'sub_id': id})


def delete_paragraph(request):
    if request.method == 'POST':
        para_data = json.loads(request.body.decode('UTF-8'))
        print('\n\npara_data????', para_data)
        para_obj = models.Paragraph.objects.get(id=para_data['para_id'])
        models.Paragraph_option.objects.filter(paragraph=para_obj).delete()
        para_obj.delete()
        return HttpResponse(True)


def add_paragraph(request,id):
    subject_obj = models.Paragraph_subject.objects.get(id=id)
    if request.method == 'POST':
        print(request.POST)
        print(request.POST.get('inlineRadioOptions'))
        print(request.POST.get('paragraph'))
        paragraph_create=models.Paragraph.objects.create(subject=models.Paragraph_subject.objects.get(id=id),paragraph_type=request.POST.get('inlineRadioOptions'),paragraph_description=request.POST.get('paragraph'),company_id=User.objects.get(id=request.user.id))
        paragraph_create.save()
        question = request.POST.getlist('pq-quote-label')
        print('question', question)
        option1=request.POST.getlist('opt-input-1')
        option2=request.POST.getlist('opt-input-2')
        option3=request.POST.getlist('opt-input-3')
        option4=request.POST.getlist('opt-input-4')
        answer=[]
        for i in range(1,len(question)+1):
            answer.append(request.POST.get('inlineRadioOptionsSelect-'+str(i)))
        para_questions=zip(question,option1,option2,option3,option4,answer)
        print('para_questions', para_questions)
        for ii in para_questions:
            print('ii', question)
            create_que_option=models.Paragraph_option.objects.create(company_id =User.objects.get(id=request.user.id),
                                                                    paragraph = paragraph_create,
                                                                    subject = subject_obj,
                                                                    question=ii[0],option1=ii[1],option2=ii[2],option3=ii[3],option4=ii[4],answer=ii[5])
            create_que_option.save()
        if 'save' in request.POST:
            return redirect('company:preview_paragraph', id=id)
    return render(request, 'company/ATS/paragraph_add_question.html',{'sub_name':subject_obj.subject_name,})





def descriptive_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.Descriptive_subject.objects.create(subject_name=subject_name['subject_name'],
                                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_id.subject_name}
        return HttpResponse(json.dumps(data))


def descriptive_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.Descriptive_subject.objects.get(id=int(subject_data['sub_id']),
                                                             company_id=models.Company.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def descriptive_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.Descriptive_subject.objects.get(id=int(subject_data['sub_id']),
                                               company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def descriptive_list(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['subject'] = models.Descriptive_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            return render(request,'company/ATS/descriptive_all.html',context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_add(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        subject_obj = models.Descriptive_subject.objects.get(id=id)
        descriptive_que=models.Descriptive.objects.filter(subject=subject_obj,
                                                                company_id=models.Company.objects.get(user_id=request.user.id),created_at__date=datetime.datetime.today().date())
        if request.method == 'POST':
            descriptive_data = json.loads(request.body.decode('UTF-8'))
            descriptive_obj = models.Descriptive.objects.create(subject=subject_obj,
                                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                paragraph_description=descriptive_data['que'])
            data = {'id': descriptive_obj.id, 'paragraph_description': descriptive_obj.paragraph_description}
            return HttpResponse(json.dumps(data))
        context['sub_id']= id
        context['subject_obj']=subject_obj
        context['descriptive_que']=descriptive_que
        return render(request,'company/ATS/descriptive_add.html', context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            if models.Descriptive_subject.objects.filter(id=id).exists():
                subject_obj = models.Descriptive_subject.objects.get(id=id)
                questions = models.Descriptive.objects.filter(subject=subject_obj)
                context['questions']=questions
                context['sub_id']=id
            else:
                context['questions']= None
                context['sub_id'] = id
            return render(request,'company/ATS/descriptive_view.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def delete_descriptive_question(request):
    if request.method == 'POST':
        desc_data = json.loads(request.body.decode('UTF-8'))
        models.Descriptive.objects.get(id=desc_data['que_id'],company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def descriptive_template_view(request,template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        print('\n\ntemplate_id desssssssssssss', template_id)
        exam_name=''
        if models.DescriptiveExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id)).exists():
            questions = models.DescriptiveExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id))
            exam_name=models.DescriptiveExamTemplate.objects.get(template=models.Template_creation.objects.get(id=template_id))

            # questions = models.Descriptive.objects.filter(subject=subject_obj)
            print('questions',questions)
        else:
            questions = None
        context['questions']=questions
        context['exam_data']=exam_name
        return render(request,'company/ATS/descriptive_template_view.html',context)
    else:
        return redirect('company:add_edit_profile')

#views added after templates

def mcq_template_view(request,template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        # print("template_id",template_id)
        exam_name=models.ExamTemplate.objects.get(template=models.Template_creation.objects.get(id=template_id))
        question_wise_flag=False
        print("exam question wise",exam_name.question_wise_time)
        print("exam_name.marking_system",exam_name.marking_system)
        if exam_name.question_wise_time or (exam_name.marking_system == "question_wise"):
            mcq_question=models.ExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id))
            question_wise_flag  =True
        else:
            basic_questions = exam_name.basic_questions.all()
            intermediate_questions = exam_name.intermediate_questions.all()
            advanced_questions = exam_name.advanced_questions.all()
            mcq_question = list(chain(basic_questions, intermediate_questions, advanced_questions))
        # print("mcq qustion",mcq_question)
        context['mcq_que']=mcq_question
        context['exam_data']=exam_name
        context["question_wise_flag"]=question_wise_flag
        return render(request,'company/ATS/mcq_template_view.html',context)
    else:
        return redirect('company:add_edit_profile')

def add_exam_template(request,template_id=None):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        subject=models.MCQ_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['subject']=subject
        if template_id:
            template = get_object_or_404(models.Template_creation,id=template_id)
            stage = template.stage
            category=template.category
            context['template_id'] = template_id
            exam_template = models.ExamTemplate.objects.filter(template=template)
            if exam_template.exists():
                context['exam_template']= exam_template[0]
        else:
            stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))

        context['template_name']=template.name

        if request.method == "POST":
            exam_template,update = models.ExamTemplate.objects.update_or_create(stage=stage,
                                                            category=category,
                                                            template=template,
                                                            company_id=models.Company.objects.get(user_id=request.user.id),
                                                            defaults={
                                                            'subject': models.MCQ_subject.objects.get(id=int(request.POST.get("language_name"))),
                                                            'exam_name' : request.POST.get("exam_name"),
                                                            'exam_type' : request.POST.get("examtype"),
                                                            'total_question'  : request.POST.get("no_of_total_questions"),
                                                            'basic_questions_count' : request.POST.get("no_of_basic_questions"),
                                                            'intermediate_questions_count' : request.POST.get("no_of_intermediate_questions"),
                                                            'advanced_questions_count' : request.POST.get("no_of_advanced_questions"),
                                                            'user_id' : User.objects.get(id=request.user.id),
                                                            })
            print("created")
            #check for negative marking
            if request.POST.get("nagative-mark"):
                exam_template.allow_negative_marking = True
                exam_template.negative_mark_percent = request.POST.get("negative_mark_percent")
            else:
                exam_template.allow_negative_marking = False
            #check for custom marking system
            print("exatm type",request.POST.get("examtype")=="custom")
            if request.POST.get("examtype") == "custom":
                exam_template.marking_system = request.POST.get("eachall")
                print(request.POST.get('eachall'))
                if request.POST.get("eachall") == "category_wise":
                    print("basic question marks",request.POST.get("marks_of_basic_questions"))
                    exam_template.basic_question_marks = request.POST.get("marks_of_basic_questions")
                    exam_template.intermediate_question_marks = request.POST.get("marks_of_intermediate_questions")
                    exam_template.advanced_question_marks = request.POST.get("marks_of_advanced_questions")
                else:
                    exam_template.basic_question_marks = None
                    exam_template.intermediate_question_marks = None
                    exam_template.advanced_question_marks = None
            else:
                print("ramdom")
                exam_template.marking_system = 'category_wise'
                print(request.POST.get('eachall'))
                print("basic question marks", request.POST.get("marks_of_basic_questions"))
                exam_template.basic_question_marks = request.POST.get("marks_of_basic_questions")
                exam_template.intermediate_question_marks = request.POST.get("marks_of_intermediate_questions")
                exam_template.advanced_question_marks = request.POST.get("marks_of_advanced_questions")
                exam_template.template.status = True
                exam_template.template.save()
            print("=======================================================================================================",request.POST.get("question-wise-time"))
            if request.POST.get("question-wise-time") == None:
                exam_template.question_wise_time = False
                exam_template.duration = request.POST.get("exam_duration")
            else:
                exam_template.question_wise_time = True
                
            exam_template.save()
            sub=models.MCQ_subject.objects.get(id=int(request.POST.get("language_name")))
            request.session['sub']=sub.id
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"            
            if not exam_template.exam_type == "custom":
                all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
                for i in all_internal_users:
                    description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Create MCQ Template"
                    if i.employee_id.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create MCQ Template",
                                                                            description=description,
                                                                            target_url=header+"://"+current_site.domain+"/company/mcq_template_view/"+str(exam_template.template.id))
                return redirect('company:template_listing')
            return redirect('company:exam_view',pk=exam_template.id)
        return render(request,"company/ATS/add-mcq-exam.html",context)
    else:
        return redirect('company:add_edit_profile')

def exam_view(request,pk):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.ExamTemplate.objects.get(id=pk)
        print(exam_template.marking_system)
        context['exam_template'] = exam_template
        if not exam_template.exam_type == "custom":
            return redirect('company:template_listing')
        if exam_template.exam_type == "custom":
            basic_questions = models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "basic",mcq_subject=models.MCQ_subject.objects.get(id=int(request.session['sub'])))
            intermediate_questions =  models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",mcq_subject=models.MCQ_subject.objects.get(id=int(request.session['sub'])))
            advanced_questions =  models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "advance",mcq_subject=models.MCQ_subject.objects.get(id=int(request.session['sub'])))


        #getting basic qustioons according to page no
        context["basic_questions"] = basic_questions
        #getting intermediate qustioons according to page no
        context["intermediate_questions"] = intermediate_questions
        #getting basic qustioons according to page no
        context["advanced_questions"] = advanced_questions
        # del request.session['sub']

    
        return render(request,"company/ATS/mcq_exam_question_select.html",context)
    else:
        return redirect('company:add_edit_profile')

def exam_edit(request,pk):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.ExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template

        exam_paper = models.QuestionPaper.objects.get(exam_template= exam_template,company_id = models.Company.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        mcq_subject = exam_paper.exam_template.subject
        if not exam_template.exam_type == "custom":
            return redirect('company:template_listing')
        if exam_template.exam_type == "custom":
            basic_questions = models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "basic",mcq_subject=mcq_subject)
            intermediate_questions =  models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",mcq_subject=mcq_subject)
            advanced_questions =  models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "advance",mcq_subject=mcq_subject)

        #getting basic qustioons according to page no
        context["basic_questions"] = basic_questions
        #getting intermediate qustioons according to page no
        context["intermediate_questions"] = intermediate_questions
        #getting basic qustioons according to page no
        context["advanced_questions"] = advanced_questions
        # del request.session['sub']
        
        if exam_template.question_wise_time or exam_template.marking_system == "question_wise_time" :
            selected_basic_questions = []
            selected_intermediate_questions = []
            selected_advanced_questions = []


            for i in exam_paper.exam_question_units.all():
                if i.question.question_level.level_name == "basic":
                    selected_basic_questions.append(i.question)
                elif i.question.question_level.level_name == "intermediate":
                    selected_intermediate_questions.append(i.question)
                else:
                    selected_advanced_questions.append(i.question)


            context["selected_basic_questions"] = exam_template.basic_questions.all()
            context["selected_intermediate_questions"] = exam_template.intermediate_questions.all()
            context["selected_advanced_questions"] = exam_template.advanced_questions.all()
        else:
            context["selected_basic_questions"] = exam_template.basic_questions.all()
            context["selected_intermediate_questions"] = exam_template.intermediate_questions.all()
            context["selected_advanced_questions"] = exam_template.advanced_questions.all()
        # print("selected basic question",selected_basic_questions)
    # <QueryDict: {'{"5":[1,"null"],"7":[1,"null"],"8":[1,"null"]}': ['']}>

        if request.method == "POST":
            all_questions = json.loads(request.body.decode('UTF-8'))
            question_ids = [i for i in all_questions.keys()]
            print("all _questions",all_questions)
            print("request.pOOOOOOOOOOOOOOOOOOOOOST",request.POST)
            if exam_template.question_wise_time or exam_template.marking_system=="question_wise":
                # exam_paper = models.QuestionPaper.objects.get(exam_template=exam_template)
                exam_paper.exam_question_units.all().delete()

                for id in question_ids:
                    question = models.mcq_Question.objects.get(id=id)
                    print("=================",id)
                    exam_question_unit = models.ExamQuestionUnit.objects.create(question=question,template=exam_template.template)
                    if exam_template.marking_system == "question_wise":
                        exam_question_unit.question_mark = all_questions[str(question.id)][0]#marks are stored at index 0
                    if exam_template.question_wise_time:
                        exam_question_unit.question_time = all_questions[str(question.id)][1] # time is stored at index 1
                    exam_question_unit.save()
                    exam_paper.exam_question_units.add(exam_question_unit)

                
            else:
                exam_template.basic_questions.clear()
                exam_template.intermediate_questions.clear()
                exam_template.advanced_questions.clear()
                for id in question_ids:
                    question = models.mcq_Question.objects.get(id=id)
                    if question.question_level.level_name == "basic":
                        exam_template.basic_questions.add(question)
                    elif question.question_level.level_name == "intermediate":
                        exam_template.intermediate_questions.add(question)
                    else:
                        exam_template.advanced_questions.add(question)

            exam_template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit MCQ Template"
            if context['get_template'].user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=context['get_template'].user_id.id),verb="Edit MCQ Template",
                            description=description,
                            target_url=header+"://"+current_site.domain+"/company/mcq_template_view/"+str(exam_templatetemplate.id))
                # for i in in 
        return render(request,"company/ATS/mcq_exam_question_edit.html",context)
    else:
        return redirect('company:add_edit_profile')

def create_exam(request,pk):
    exam_template = get_object_or_404(models.ExamTemplate,id=pk)
    question_paper = models.QuestionPaper.objects.create(exam_template=exam_template,
                                                        company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id))
    # basic_questions = models.Question.objects.filter(question_level__level_name = "Basic")
    # intermediate_questions = models.Question.objects.filter(question_level__level_name = "Intermediate")
    # advanced_questions = models.Question.objects.filter(question_level__level_name = "Advanced")
    if exam_template.exam_type == "custom":
        question_data = json.loads(request.body.decode('UTF-8'))
        print(question_data)
        question_ids = [i for i in question_data.keys()]
        print(question_ids)
        for id in question_ids:
            question = models.mcq_Question.objects.get(id=id)
            print("=================",id)
            if exam_template.marking_system == "question_wise" or exam_template.question_wise_time:
                exam_question_unit = models.ExamQuestionUnit.objects.create(question=question,template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid'])))
                if exam_template.marking_system == "question_wise":
                    exam_question_unit.question_mark = question_data[str(question.id)][0]#marks are stored at index 0
                if exam_template.question_wise_time:
                    exam_question_unit.question_time = question_data[str(question.id)][1] # time is stored at index 1
                exam_question_unit.save()
                question_paper.exam_question_units.add(exam_question_unit)
            if question.question_level.level_name == "basic":
                print('basic========================')
                exam_template.basic_questions.add(question)
            elif question.question_level.level_name == "intermediate":
                print('intermediate========================')
                exam_template.intermediate_questions.add(question)
            else:
                print('advance========================')
                exam_template.advanced_questions.add(question)
        exam_template.save()
    exam_template.template.status = True
    exam_template.template.save()
    all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    description = template_name.name+" has been added to your workspace"
    for i in all_internal_users:
        if i.employee_id.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create MCQ Template",
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/company/mcq_template_view/"+str(exam_template.template.id))
    print("question idsssss",question_ids)
    all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                    user_id=request.user)).values_list('employee_id', flat=True)
    get_email=[]
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/company/mcq_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'MCQ Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return HttpResponse("lolwa")
#end later views



# MCQ subject crud

def mcq_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.MCQ_subject.objects.create(subject_name=subject_name['subject_name'],
                                                             company_id=models.Company.objects.get(user_id=request.user.id),
                                                             user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {}
        data['status'] = True
        data['subject_id'] = subject_id.id
        data['subject_name'] = subject_id.subject_name
        return HttpResponse(json.dumps(data))


def mcq_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        subject_get = models.MCQ_subject.objects.get(id=int(subject_data['sub_id']),
                                                           company_id=models.Company.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def mcq_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        # print(subject_data)
        models.MCQ_subject.objects.get(id=int(subject_data['sub_id']),
                                             company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def mcq_subject_list(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['subject']= models.MCQ_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),)
            return render(request, 'company/ATS/mcq_subject.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')


def preview_mcq(request, id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            level = CandidateModels.QuestionDifficultyLevel.objects.all()
            context['sub_id'] = id
            
            context['level'] = level
            if models.MCQ_subject.objects.filter(id=id).exists():
                data = []
                subject_obj = models.MCQ_subject.objects.get(id=id)
                context['sub_name'] = subject_obj.subject_name
                data=models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),mcq_subject=models.MCQ_subject.objects.get(id=id))
                context['questions']=data
            else:
                data = None
                context['questions'] = data
            return render(request, 'company/ATS/mcq_view.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def add_mcq(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
        if context['Add']:
            level = CandidateModels.QuestionDifficultyLevel.objects.all()
            subject_obj = models.MCQ_subject.objects.get(id=id)
            question_get=models.mcq_Question.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),mcq_subject=models.MCQ_subject.objects.get(id=id),created_at__date=datetime.datetime.today().date())
            page = request.GET.get('page', 1)
            paginator = Paginator(question_get, 10)
            try:
                question = paginator.page(page)
            except PageNotAnInteger:
                question = paginator.page(1)
            except EmptyPage:
                question = paginator.page(paginator.num_pages)
            if request.method == 'POST':
                level=request.POST.get('question_level')
                question = request.POST.get('question')
                option1=request.POST.get('option_1')
                option2=request.POST.get('option_2')
                option3=request.POST.get('option_3')
                option4=request.POST.get('option_4')
                answer=request.POST.get('correct_answer')
                create_que_option=models.mcq_Question.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id),
                                                                    mcq_subject=models.MCQ_subject.objects.get(id=id),
                                                                    question_description =question,
                                                                    question_level =CandidateModels.QuestionDifficultyLevel.objects.get(id=int(level)),
                                                                    correct_option =answer,option_a =option1 ,option_b =option2,option_c =option3 ,option_d =option4)
                create_que_option.save()
                return redirect('company:add_mcq',id)
            context['sub_name']=subject_obj.subject_name
            context['level'] = level
            context['question'] = question
            return render(request, 'company/ATS/mcq_add.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def mcq_delete_question(request):
    if request.method == 'POST':
        question_data = json.loads(request.body.decode('UTF-8'))
        # print(subject_data)
        models.mcq_Question.objects.get(id=int(question_data['question_id']),
                                             company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)

def get_basic_count(request):
    data = {}
    if request.method == 'POST':
        get_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='basic')
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        basic_count = models.mcq_Question.objects.filter(mcq_subject=models.MCQ_subject.objects.get(id=int(subject_data['subject_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id),question_level=get_type.id)
        print('++++++++++++++++++++++++++++++',len(basic_count))
        data['basic_count'] = len(basic_count)
        data['status'] = True
    else:
        data['basic_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))

def get_intermediate_count(request):
    data = {}
    if request.method == 'POST':
        get_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='intermediate')
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        intermediate_count = models.mcq_Question.objects.filter(mcq_subject=models.MCQ_subject.objects.get(id=int(subject_data['subject_id'])),
                                                          question_level=get_type.id)
        print('++++++++++++++++++++++++++++++',len(intermediate_count))
        data['intermediate_count'] = len(intermediate_count)
        data['status'] = True
    else:
        data['intermediate_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))

def get_advance_count(request):
    data = {}
    if request.method == 'POST':
        get_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='advance')
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        advance_count = models.mcq_Question.objects.filter(mcq_subject=models.MCQ_subject.objects.get(id=int(subject_data['subject_id'])),
                                                          question_level=get_type.id)
        print('++++++++++++++++++++++++++++++',len(advance_count))
        data['advance_count'] = len(advance_count)
        data['status'] = True
    else:
        data['advance_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))





# Image based question bank


def image_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.ImageSubject.objects.create(subject_name=subject_name['subject_name'],
                                                        company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_id.subject_name}
        return HttpResponse(json.dumps(data))


def image_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.ImageSubject.objects.get(id=int(subject_data['sub_id']),
                                                             company_id=models.Company.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def image_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.ImageSubject.objects.get(id=int(subject_data['sub_id']),
                                               company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def image_based_all(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['subject'] = models.ImageSubject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            return render(request,'company/ATS/image_based_all.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')
def image_based_question_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            if models.ImageSubject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),id=id).exists():
                subject_obj = models.ImageSubject.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=id)
                
                questions = models.ImageOption.objects.filter(subject_id=subject_obj)
                context['sub_id']=id
                context['sub_name']=subject_obj.subject_name
                context['questions'] = questions
            return render(request, 'company/ATS/image_based_question_view.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')
def image_based_question_add(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        subject_obj = models.ImageSubject.objects.get(id=id)
        image_question=models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),created_at__date=datetime.datetime.today().date())
        image_que=[]
        for image_questions in image_question:
            if models.ImageOption.objects.filter(question_id=image_questions.id,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
                option=models.ImageOption.objects.get(question_id=image_questions.id,company_id=models.Company.objects.get(user_id=request.user.id))
                image_que.append({'question':image_questions.image_que_description,'que_file':image_questions.question_file,'correct_option':option.answer,'option1':option.option1,'option1_file':option.file1,'option2':option.option2,'option2_file':option.file2,'option3':option.option3,'option3_file':option.file3,'option4':option.option4,'option4_file':option.file4})
        level = CandidateModels.QuestionDifficultyLevel.objects.all()
        if request.method == 'POST':
            print('123',request.POST)
            print('\n\nfiles',request.FILES)
            level=request.POST.get('question_level')
            img_question_obj = models.ImageQuestion.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                user_id=User.objects.get(id=request.user.id),
                                                subject=subject_obj,
                                                question_level=CandidateModels.QuestionDifficultyLevel.objects.get(id=int(level)),
                                                image_que_description=request.POST.get('question'),
                                                question_file=request.FILES.get('question_file'))

            options_obj = models.ImageOption.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                user_id=User.objects.get(id=request.user.id),
                                                subject_id=subject_obj,question_id=img_question_obj,answer=request.POST.get('correct_answer'),
                                                option1=request.POST.get('option_1'),option2=request.POST.get('option_2'),
                                                option3=request.POST.get('option_3'),option4=request.POST.get('option_4'),
                                                file1=request.FILES.get('option_file1'),file2=request.FILES.get('option_file2'),
                                                file3=request.FILES.get('option_file3'),file4=request.FILES.get('option_file4'))
            data = {'question': img_question_obj.image_que_description,'question_id':img_question_obj.id,
                    'question_file': True if img_question_obj.question_file else False, 'option1': options_obj.option1,
                    'option2': options_obj.option2, 'option3': options_obj.option3, 'option4': options_obj.option4,
                    'file1': True if options_obj.file1 else False, 'file2': True if options_obj.file2 else False,
                    'file3': True if options_obj.file3 else False, 'file4': True if options_obj.file4 else False}
            return HttpResponse(json.dumps(data))
        context['sub_id']=id
        context['level']=level
        context['sub_name']=subject_obj.subject_name
        context['image_question']=image_que
        return render(request, 'company/ATS/image_based_question_add.html',context)
    else:
        return redirect('company:add_edit_profile')

def delete_image_question(request):
    if request.method == 'POST':
        img_data = json.loads(request.body.decode('UTF-8'))
        que_obj = models.ImageQuestion.objects.get(id=img_data['que_id'])
        models.ImageOption.objects.get(question_id=que_obj).delete()
        que_obj.delete()
        return HttpResponse(True)


def images_template_view(request,template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_name=models.ImageExamTemplate.objects.get(template=models.Template_creation.objects.get(id=template_id))
        question_wise_flag=False
        context['question_wise_time']=exam_name.question_wise_time
        context['marking_system']=exam_name.marking_system
        if exam_name.question_wise_time or exam_name.marking_system == "question_wise":
            image_question=models.ImageExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id))
            question_wise_flag  =True
            img_options=models.ImageExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id)).values_list('question')
        
            options_get=models.ImageOption.objects.filter(question_id__in=img_options)
            context["options"]=options_get
            # context['img_question']=image_question
        else:
            print("asdasdasdasdas\n\n\n\ in else")
            basic_questions = exam_name.basic_questions.all()
            intermediate_questions = exam_name.intermediate_questions.all()
            advanced_questions = exam_name.advanced_questions.all()
            image_question = list(chain(basic_questions, intermediate_questions, advanced_questions))

            # img_options=models.ImageExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id)).values_list('question')
            options_get=models.ImageOption.objects.filter(question_id__in=image_question)
            context["options"]=options_get   
        context['img_question']=image_question
        # imageque=models.ImageExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id))
        # print("555555555555555555555555555555",imageque)

        context['exam_data']=exam_name
        context['question_wise_flag']=question_wise_flag
        # print(imageque)
        return render(request,"company/ATS/image-template-view.html",context)
    else:
        return redirect('company:add_edit_profile')

#  CODING EXAM QUESTION BANK
def coding_add_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        if subject_data['type'] == 'backend':
            api_subject = CandidateModels.CodingApiSubjects.objects.get(id=subject_data['subject_id'])
        else:
            api_subject = None
        subject_id = models.CodingSubject.objects.create(api_subject_id=api_subject,
                                                         type=subject_data['type'],
                                                         company_id=models.Company.objects.get(user_id=request.user.id),
                                                         user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        if subject_id.type == 'backend':
            subject_name = subject_id.api_subject_id.name
        else:
            subject_name = 'Html/CSS/Js'
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_name,
                'type': subject_id.type}
        return HttpResponse(json.dumps(data))


def coding_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.CodingSubject.objects.get(id=int(subject_data['sub_id']),
                                                       company_id=models.Company.objects.get(user_id=request.user.id))
        subject_get.api_subject_id = CandidateModels.CodingApiSubjects.objects.get(id=subject_data['api_sub_id'])
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def coding_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.CodingSubject.objects.get(id=int(subject_data['sub_id']),
                                         company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def coding_add_category(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('UTF-8'))

        category_id = models.CodingSubjectCategory.objects.create(category_name=data['category_name'],
                                                                  subject_id=models.CodingSubject.objects.get(
                                                                      id=data['sub_id']),
                                                                  company_id=models.Company.objects.get(user_id=request.user.id),
                                                                  user_id=User.objects.get(id=request.user.id))
        category_id.save()
        data = {'status': True, 'category_id': category_id.id, 'category_name': category_id.category_name}
        return HttpResponse(json.dumps(data))


def coding_update_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        category_get = models.CodingSubjectCategory.objects.get(id=int(category_data['cat_id']),
                                                                company_id=User.objects.get(id=request.user.id))
        category_get.category_name = category_data['cat_name']
        category_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def coding_delete_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        models.CodingSubjectCategory.objects.get(id=int(category_data['category_id']),
                                                 company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def coding_subject_all(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['api_subjects']= CandidateModels.CodingApiSubjects.objects.filter(status=True)
            context['subject'] = models.CodingSubject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            return render(request, 'company/ATS/coding_subject_all.html', context)
    else:
        return redirect('company:add_edit_profile')

# def coding_category_all(request, id):
#     context = {}
#     context['Add'] = False
#     context['Edit'] = False
#     context['Delete'] = False
#     context['permission'] = check_permission(request)
#     for permissions in context['permission']:
#         if permissions.permissionsmodel.modelname == 'Question Bank':
#             print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
#             if permissions.permissionname == 'Add':
#                 context['Add'] = True
#             if permissions.permissionname == 'Edit':
#                 context['Edit'] = True
#             if permissions.permissionname == 'Delete':
#                 context['Delete'] = True
#     if context['Add'] or context['Edit'] or context['Delete']:
#         subject = models.CodingSubject.objects.get(company_id=models.Company.objects.get(user_id=request.user.id), id=id)
#         categories = models.CodingSubjectCategory.objects.filter(subject_id=subject,company_id=models.Company.objects.get(user_id=request.user.id))
#         context['categories']=categories
#         context['sub_id'] = id
#         return render(request, 'company/ATS/coding_category_all.html',context)
#     else:
#         return render(request, 'company/ATS/not_permoission.html', context)


def coding_category_all(request, id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            subject = models.CodingSubject.objects.get(company_id=models.Company.objects.get(user_id=request.user.id), id=id)
            categ = models.CodingSubjectCategory.objects.get(subject_id=subject)
            return redirect('company:coding_question_add',categ.id)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def coding_question_add(request, id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        category_obj = models.CodingSubjectCategory.objects.get(id=id)
        coding_ques=models.CodingQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                category_id=category_obj,created_at__date=datetime.datetime.today().date())
        if request.method == 'POST':
            category_obj = models.CodingSubjectCategory.objects.get(id=id)
            coding_data = json.loads(request.body.decode('UTF-8'))
            question_obj = models.CodingQuestion.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                category_id=category_obj,
                                                                question_type=coding_data['question_type'],
                                                                coding_que_title=coding_data['que_title'],
                                                                coding_que_description=coding_data['que'])
            data = {'id': question_obj.id, 'coding_que_description': question_obj.coding_que_description,
                    'question_type': question_obj.question_type, 'coding_que_title': question_obj.coding_que_title}
            return HttpResponse(json.dumps(data))
        context['category_id']= id
        context['coding_ques']=coding_ques
        return render(request, 'company/ATS/coding_question_add.html',context)
    else:
        return redirect('company:add_edit_profile')

# def coding_question_view(request, id):
#     context = {}
#     context['Add'] = False
#     context['Edit'] = False
#     context['Delete'] = False
#     context['permission'] = check_permission(request)
#     for permissions in context['permission']:
#         if permissions.permissionsmodel.modelname == 'Question Bank':
#             print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
#             if permissions.permissionname == 'Add':
#                 context['Add'] = True
#             if permissions.permissionname == 'Edit':
#                 context['Edit'] = True
#             if permissions.permissionname == 'Delete':
#                 context['Delete'] = True
#     if context['Add'] or context['Edit'] or context['Delete']:
#         categ_obj = models.CodingSubjectCategory.objects.get(id=id)
#         questions = models.CodingQuestion.objects.filter(category_id=categ_obj,
#                                                          company_id=models.Company.objects.get(user_id=request.user.id))
#         context['questions']=questions
#         context['category_id'] = id
#         return render(request, 'company/ATS/coding_question_view.html', context)
#     else:
#         return render(request, 'company/ATS/not_permoission.html', context)


def coding_question_view(request, id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            categ_obj = models.CodingSubjectCategory.objects.get(subject_id=id)
            questions = models.CodingQuestion.objects.filter(category_id=categ_obj,
                                                            company_id=models.Company.objects.get(user_id=request.user.id))
            context['questions']=questions
            context['category_id'] = categ_obj.id
            return render(request, 'company/ATS/coding_question_view.html', context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')


def delete_coding_question(request):
    if request.method == 'POST':
        coding_data = json.loads(request.body.decode('UTF-8'))
        models.CodingQuestion.objects.get(id=coding_data['que_id']).delete()
        return HttpResponse(True)


#  CODING EXAM CONFIGURATION




def coding_exam_configuration(request,template_id=None):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        user_obj = User.objects.get(id=request.user.id)
        backend_subjects = models.CodingSubject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),type='backend')
        frontend_subjects = models.CodingSubject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),type='frontend')
        context['backend_subjects'] = backend_subjects
        context['frontend_subjects'] = frontend_subjects
        if template_id:
            print("inside if")
            template_obj = get_object_or_404(models.Template_creation,id=template_id)
            # stage = template.stage
            # category=template.category
            context['template_id'] = template_id
            exam_template = models.CodingExamConfiguration.objects.filter(template_id=template_obj)
            if exam_template.exists():
                print("inside nested if")
                context['exam_template']= exam_template[0]
        else:
            # stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            # category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template_obj=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))

        context['template_obj']= template_obj
        if request.method == 'POST':
            print('\n\n\n\n\n\n  technology', request.POST.get('total_time'))
            # template_obj = models.Template_creation.objects.get(id=int(
                # request.session['create_template']['templateid']))
            if request.POST.getlist('technology-type')[0] == 'backend':
                coding_subject_id = models.CodingSubject.objects.get(id=request.POST.get('backend_selected_subject'))
            else:
                coding_subject_id = models.CodingSubject.objects.get(id=request.POST.get('frontend_selected_subject'))
            
            # coding_category_id = models.CodingSubjectCategory.objects.get(id=request.POST.get('backend_selected_subject_category'))
            coding_category_id = models.CodingSubjectCategory.objects.get(subject_id=coding_subject_id.id)
            models.CodingExamConfiguration.objects.update_or_create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id),
                                                                    template_id=template_obj,
                                                                    defaults={'created_at':datetime.datetime.now(),
                                                                        'exam_name': request.POST.get('exam_name'),
                                                                            'total_time': request.POST.get('total_time'),
                                                                            'total_question': request.POST.get(
                                                                                'total_question'),
                                                                            'assignment_type':
                                                                                request.POST.getlist('assignment_type')[
                                                                                    0],
                                                                            'exam_type': "custom",
                                                                            'technology':
                                                                                request.POST.getlist('technology-type')[0],
                                                                            'coding_subject_id': coding_subject_id,
                                                                            'coding_category_id':coding_category_id,
                                                                            })
            exam_configuration = models.CodingExamConfiguration.objects.get(
                company_id=models.Company.objects.get(user_id=request.user.id),
                template_id=template_obj)
            request.session['exam_configuration_id'] = exam_configuration.id
            return redirect('company:coding_question_selection')
        return render(request, 'company/ATS/coding_exam_configuration.html',context)
    else:
        return redirect('company:add_edit_profile')

def coding_question_selection(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if 'exam_configuration_id' in request.session:
            exam_configuration_id = request.session['exam_configuration_id']
            exam_configuration_obj = models.CodingExamConfiguration.objects.get(id=exam_configuration_id)
            categ_id = exam_configuration_obj.coding_category_id
            no_of_que = int(exam_configuration_obj.total_question)
            questions = models.CodingQuestion.objects.filter(category_id=categ_id).order_by('-id')
            print('questions', no_of_que, questions)
            if request.method == 'POST':
                print('\n\n\n\n\n\n  technology', request.POST)
                question_ids = request.POST.get("question_id_list")
                question_ids = question_ids[1:len(question_ids)-1]
                question_ids = question_ids.split(",")
                print("qurestion_ids",question_ids)
                print('\n\n\npost called')
                for i in question_ids:
                    question = questions.get(id=int(i))
                    models.CodingExamQuestions.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            coding_exam_config_id=exam_configuration_obj, question_id=question)
                if exam_configuration_obj.assignment_type == 'marks':
                    return redirect('company:coding_question_marking')
                if exam_configuration_obj.assignment_type == 'rating':
                    return redirect('company:coding_question_rating')
            context['exam_configuration']= exam_configuration_obj
            context['questions']= questions
            context['no_of_que']=range(0,no_of_que)
            return render(request, 'company/ATS/coding_question_selection.html',context)
        else:
            return render(request, 'accounts/404.html')
    else:
        return redirect('company:add_edit_profile')

def coding_question_edit_selection(request,template_id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_configuration_obj = models.CodingExamConfiguration.objects.get(template_id__id=template_id)
        categ_id = exam_configuration_obj.coding_category_id
        no_of_que = int(exam_configuration_obj.total_question)
        questions = models.CodingQuestion.objects.filter(category_id=categ_id).order_by('-id')
        exam_questions = models.CodingExamQuestions.objects.filter(coding_exam_config_id=exam_configuration_obj)
        print("exam_questions",exam_questions)


                # if exam_configuration_obj.assignment_type == 'marks':
        coding_ids = []

        for i in exam_questions:
            coding_ids.append(i.question_id.id)
        context['exam_configuration']=exam_configuration_obj
        context['questions']=questions
        context['no_of_que']=range(0,no_of_que)
        context['exam_question_ids']=coding_ids


        if request.method == "POST":

            print("request.post",request.POST)
            new_question_id_list = request.POST.get("question_id_list")
            print("length of string",type(len(new_question_id_list)-1))
            new_question_id_list = new_question_id_list[1:len(new_question_id_list)-1]
            new_question_id_list = new_question_id_list.split(",")
            print("new question ids",new_question_id_list)
            exam_questions.delete()

            for i in new_question_id_list:
                question = questions.get(id=int(i))
                
                new_exam_question = models.CodingExamQuestions.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            coding_exam_config_id=exam_configuration_obj, question_id=question)
            if exam_configuration_obj.assignment_type == 'marks':
                return redirect('company:coding_question_marking_edit',exam_config_id=exam_configuration_obj.id)
            if exam_configuration_obj.assignment_type == 'rating':
                return redirect('company:coding_question_rating_edit',exam_config_id=exam_configuration_obj.id)
            
        return render(request, 'company/ATS/coding_question_edit_selection.html',context)
    else:
        return redirect('company:add_edit_profile')

def coding_question_marking(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_configuration_id = request.session['exam_configuration_id']
        exam_configuration_obj = models.CodingExamConfiguration.objects.get(id=exam_configuration_id)
        questions = models.CodingExamQuestions.objects.filter(coding_exam_config_id=exam_configuration_obj).order_by('-id')
        if request.method == 'POST':
            print('\n\nmarks', request.POST.getlist('question_marks'))
            marks = request.POST.getlist('question_marks')
            for que, mark in zip(questions, marks):
                que.marks = mark
                que.save()
            exam_configuration_obj.template_id.status = True
            exam_configuration_obj.template_id.save()
            all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                            user_id=request.user)).values_list('employee_id', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http" 
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            link=header+"://"+current_site.domain+"/company/coding_template_view/"+str(exam_configuration_obj.template_id.id)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Coding Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace" 
            all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            for i in all_internal_users:
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Coding Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/coding_template_view/"+str(exam_configuration_obj.template_id.id))

            return redirect('company:template_listing')
        context['questions']= questions
        return render(request, 'company/ATS/coding_question_marking.html', context)
    else:
        return redirect('company:add_edit_profile')

def coding_question_marking_edit(request,exam_config_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_configuration_obj = models.CodingExamConfiguration.objects.get(id=exam_config_id)
        questions = models.CodingExamQuestions.objects.filter(coding_exam_config_id=exam_configuration_obj).order_by('-id')
        if request.method == 'POST':
            print('\n\nmarks', request.POST.getlist('question_marks'))
            marks = request.POST.getlist('question_marks')
            for i in  range(len(marks)):
                question = questions[i]
                question.marks = marks[i]
                question.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit Coding Template"
            if exam_configuration_obj.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=context['get_template'].user_id.id),verb="Edit Coding Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/company/coding_template_view/"+str(exam_configuration_obj.template_id.id))

            return redirect('company:template_listing')
        context['questions']= questions
        return render(request, 'company/ATS/coding_question_marking_edit.html', context)
    else:
        return redirect('company:add_edit_profile')


def coding_question_rating(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_configuration_id = request.session['exam_configuration_id']
        exam_configuration_obj = models.CodingExamConfiguration.objects.get(id=exam_configuration_id)
        if request.method == 'POST':
            scorecard_title = request.POST.getlist('title')
            models.CodingScoreCard.objects.filter(coding_exam_config_id=exam_configuration_obj).delete()
            for title in scorecard_title:
                models.CodingScoreCard.objects.create(title=title, coding_exam_config_id=exam_configuration_obj)
            exam_configuration_obj.template_id.status = True
            exam_configuration_obj.template_id.save()
            all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                            user_id=request.user)).values_list('employee_id', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            link = header+"://"+current_site.domain+"/company/coding_template_view/"+str(exam_configuration_obj.template_id.id)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Coding Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace"
            all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            for i in all_internal_users:
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Coding Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/coding_template_view/"+str(exam_configuration_obj.template_id.id))

            return redirect('company:template_listing')
        return render(request, 'company/ATS/coding_question_rating.html',context)
    else:
        return redirect('company:add_edit_profile')

def coding_question_rating_edit(request,exam_config_id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_configuration_obj = get_object_or_404(models.CodingExamConfiguration,id=exam_config_id)
        score_cards= models.CodingScoreCard.objects.filter(coding_exam_config_id=exam_configuration_obj)
        context["score_cards"] = score_cards
        exam_configuration_obj = models.CodingExamConfiguration.objects.get(id=exam_config_id)
        if request.method == 'POST':
            scorecard_title = request.POST.getlist('title')
            models.CodingScoreCard.objects.filter(coding_exam_config_id=exam_configuration_obj).delete()
            for title in scorecard_title:
                models.CodingScoreCard.objects.create(title=title, coding_exam_config_id=exam_configuration_obj)
            exam_configuration_obj.template_id.status = True
            exam_configuration_obj.template_id.save()
            return redirect('company:template_listing')
        return render(request, 'company/ATS/coding_question_rating_edit.html',context)
    else:
        return redirect('company:add_edit_profile')
def get_subject_categories(request,subject_id):
    # subject = models.CodingSubject.objects.get(id=subject_id)
    all_categories = models.CodingSubjectCategory.objects.filter(subject_id__id = subject_id)
    category_data = []

    for i in all_categories:
        category_data.append([i.id,i.category_name])

    return HttpResponse(json.dumps(category_data))


def coding_template_view(request, template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        template_getque= models.CodingExamConfiguration.objects.get(template_id=models.Template_creation.objects.get(id=template_id))
        questions=models.CodingExamQuestions.objects.filter(coding_exam_config_id=template_getque.id)
        basic_count = questions.filter(question_id__question_type='basic').count()
        intermediate_count = questions.filter(question_id__question_type='intermediate').count()
        advance_count = questions.filter(question_id__question_type='advance').count()
        context['questions']= questions
        context['exam_data']=template_getque
        context['basic_count']=basic_count
        context['intermediate_count']=intermediate_count
        context['advance_count']=advance_count
        return render(request, 'company/ATS/coding_template_view.html', context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_exam_template(request,template_id=None):
    # views added after templates
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        subject = models.Descriptive_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['subject'] = subject
        if template_id:
            template = get_object_or_404(models.Template_creation,id=template_id)
            print("template", template)
            stage = template.stage
            category=template.category
            context['template_id'] = template_id
            exam_template = models.DescriptiveExamTemplate.objects.filter(template=template)
            if exam_template.exists():
                context['exam_template']= exam_template[0]
        else:
            stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        if request.method == "POST":
            exam_template,update     = models.DescriptiveExamTemplate.objects.update_or_create(
                stage=stage,
                category=category,
                template=template,
                company_id=models.Company.objects.get(user_id=request.user.id),
                defaults={
                'subject' : models.Descriptive_subject.objects.get(id=int(request.POST.get("language_name"))),
                'exam_name' : request.POST.get("exam_name"),
                'total_question' : request.POST.get("no_of_total_questions"),
                'user_id' : User.objects.get(id=request.user.id),
                })
            request.session['sub'] = int(request.POST.get("language_name"))
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            for i in all_internal_users:
                description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Create Descriptive Template"
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Descriptive Template",
                                                                        description=description,
                                                                        target_url=header+"://"+current_site.domain+"/company/descriptive_template_view/"+str(exam_template.template.id))
            return redirect('company:descriptive_exam_view', pk=exam_template.id)
        return render(request, "company/ATS/add-descriptive_exam.html", context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_exam_view(request, pk):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.DescriptiveExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        descriptive_questions = models.Descriptive.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                subject=models.Descriptive_subject.objects.get(
                                                                    id=int(request.session['sub'])))

        # getting basic qustioons according to page no
        context["basic_questions"] = descriptive_questions
        
    # del request.session['sub']
        return render(request, "company/ATS/descriptive_exam-view.html", context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_exam_edit(request, pk):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        print("edit was called")
        exam_template = models.DescriptiveExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template

        
        exam_paper = models.DescriptiveQuestionPaper.objects.get(exam_template= exam_template,company_id = models.Company.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        descriptive_subject = exam_paper.exam_template.subject

        descriptive_questions = models.Descriptive.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                subject=descriptive_subject)


        if request.method == "POST":
            all_questions = json.loads(request.body.decode('UTF-8'))
            question_ids = [i for i in all_questions.keys()]
            print("all _questions",all_questions)
            print("request.pOOOOOOOOOOOOOOOOOOOOOST",request.POST)
            if exam_template.question_wise_time :
                # exam_paper = models.QuestionPaper.objects.get(exam_template=exam_template)
                exam_paper.exam_question_units.all().delete()

                for id in question_ids:
                    question = models.Descriptive.objects.get(id=id)
                    print("=================",id)
                    exam_question_unit = models.DescriptiveExamQuestionUnit.objects.create(question=question,template=exam_template.template)
                    # if exam_template.marking_system == "question_wise":
                    exam_question_unit.question_mark = all_questions[str(question.id)][0]#marks are stored at index 0
                    if exam_template.question_wise_time:
                        exam_question_unit.question_time = all_questions[str(question.id)][1] # time is stored at index 1
                    exam_question_unit.save()
                    exam_paper.exam_question_units.add(exam_question_unit)

                
            else:
                exam_template.basic_questions.clear()
                exam_template.intermediate_questions.clear()
                exam_template.advanced_questions.clear()
                for id in question_ids:
                    question = models.Descriptive.objects.get(id=id)
                    if question.question_level.level_name == "basic":
                        exam_template.basic_questions.add(question)
                    elif question.question_level.level_name == "intermediate":
                        exam_template.intermediate_questions.add(question)
                    else:
                        exam_template.advanced_questions.add(question)

            exam_template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit descriptive Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Edit descriptive Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/company/descriptive_template_view/"+str(exam_template.template.id))
        # del request.session['sub']
        context["basic_questions"] = descriptive_questions
        
    # del request.session['sub']
        return render(request, "company/ATS/descriptive_exam-edit.html", context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_question_rating(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_configuration_id = request.session['exam_configuration_id']
        exam_configuration_obj = models.descriptive_exam_template.objects.get(id=exam_configuration_id)
        if request.method == 'POST':
            scorecard_title = request.POST.getlist('title')
            for title in scorecard_title:
                models.DescriptiveScoreCard.objects.create(title=title,coding_exam_config_id=exam_configuration_obj)
        return render(request, 'company/ATS/descriptive-rating.html',context)
    else:
        return redirect('company:add_edit_profile')

def descriptive_create_exam(request, pk):
    exam_template = get_object_or_404(models.DescriptiveExamTemplate, id=pk)
    user = User.objects.get(id=request.user.id)
    question_paper = models.DescriptiveQuestionPaper.objects.create(exam_template=exam_template, 
                                                                    company_id=models.Company.objects.get(user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id))
    
    question_data = json.loads(request.body.decode('UTF-8'))
    question_ids = [i for i in question_data.keys()]
    for id in question_ids:

        question = models.Descriptive.objects.get(id=id)
        print("=================", id)
        exam_question_unit = models.DescriptiveExamQuestionUnit.objects.create(question=question,template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid'])))
        exam_question_unit.question_mark = question_data[str(question.id)][0]  # marks are stored at index 0
        exam_question_unit.question_time = question_data[str(question.id)][1]
        exam_template.descriptivequestions.add(question)# time is stored at index 1
        exam_question_unit.save()
        question_paper.exam_question_units.add(exam_question_unit)
    exam_template.save()
    exam_template.template.status = True
    exam_template.template.save()
    print("question idsssss", question_ids)
    all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    get_email=[]
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/company/descriptive_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'Descriptive Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
       
    # description = template_name.name+" has been added to your workspace"
    # for i in all_internal_users:
    #     if i.employee_id.id != request.user.id:
    #         notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create descriptive Template" + str(exam_template.template_id.id),
    #                                                             description=description,image="/static/notifications/icon/company/Template.png",
    #                                                             target_url=header+"://"+current_site.domain+"/company/descriptive_template_view/"+str(exam_template.template_id.id))

    return HttpResponse("/company/template_listing")


def descriptive_get_count(request):
    data = {}
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        basic_count = models.Descriptive.objects.filter(subject=models.Descriptive_subject.objects.get(id=int(subject_data['subject_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id))
        print('++++++++++++++++++++++++++++++',len(basic_count))
        data['basic_count'] = len(basic_count)
        data['status'] = True
    else:
        data['basic_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))



# Image exam

# views added after templates


def image_add_exam_template(request,template_id=None):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        subject=models.ImageSubject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['subject']=subject
        if template_id:
            template = get_object_or_404(models.Template_creation,id=template_id)
            print("template", template)
            stage = template.stage
            category=template.category
            context['template_id'] = template_id
            exam_template = models.ImageExamTemplate.objects.filter(template=template)
            if exam_template.exists():
                context['exam_template']= exam_template[0]
        else:
            stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        if request.method == "POST":
            print('asdddddddddddasdasdasdasdasdasdasdas')
            exam_template,update = models.ImageExamTemplate.objects.update_or_create(stage=stage,
                                                            category=category,
                                                            template=template,
                                                            company_id=models.Company.objects.get(user_id=request.user.id),
                                                            defaults={
                                                            'subject':models.ImageSubject.objects.get(id=int(request.POST.get("language_name"))),
                                                            'exam_name':request.POST.get("exam_name"),
                                                            'exam_type' : request.POST.get("examtype"),
                                                            'total_question':request.POST.get("no_of_total_questions"),
                                                            'basic_questions_count' : request.POST.get("no_of_basic_questions"),
                                                            'intermediate_questions_count' : request.POST.get("no_of_intermediate_questions"),
                                                            'advanced_questions_count' : request.POST.get("no_of_advanced_questions"),
                                                            'user_id': User.objects.get(id=request.user.id)})
            print("created")
            #check for negative marking
            if request.POST.get("nagative-mark"):
                exam_template.allow_negative_marking = True
                exam_template.negative_mark_percent = request.POST.get("negative_mark_percent")
            else:
                exam_template.allow_negative_marking = False
            #check for custom marking system
            print("exatm type",request.POST.get("examtype")=="custom")
            if request.POST.get("examtype") == "custom":
                print("legit")
                exam_template.marking_system = request.POST.get("eachall")
                print(request.POST.get('eachall'))
                if request.POST.get("eachall") == "category_wise":
                    print("basic question marks",request.POST.get("marks_of_basic_questions"))
                    exam_template.basic_question_marks = request.POST.get("marks_of_basic_questions")
                    exam_template.intermediate_question_marks = request.POST.get("marks_of_intermediate_questions")
                    exam_template.advanced_question_marks = request.POST.get("marks_of_advanced_questions")
                else:
                    exam_template.basic_question_marks = None
                    exam_template.intermediate_question_marks = None
                    exam_template.advanced_question_marks = None
            print("=======================================================================================================",request.POST.get("question-wise-time"))
            if request.POST.get("question-wise-time") == None:
                exam_template.question_wise_time = False
                exam_template.duration = request.POST.get("exam_duration")
            else:
                exam_template.question_wise_time = True
            exam_template.save()
            sub=models.ImageSubject.objects.get(id=int(request.POST.get("language_name")))
            request.session['sub']=sub.id
            if not  exam_template.exam_type == "custom":
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"    
                all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
                for i in all_internal_users:
                    description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Create Image Template"
                    if i.employee_id.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Image Template",
                                                                            description=description,
                                                                            target_url=header+"://"+current_site.domain+"/company/images_template_view/"+str(exam_template.template.id))

                return redirect('company:template_listing')
            return redirect('company:image_exam_view',pk=exam_template.id)
        return render(request,"company/ATS/image-add-exam.html",context)
    else:
        return redirect('company:add_edit_profile')

def image_exam_view(request,pk):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.ImageExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        if exam_template.exam_type == "custom":
            basic_questions = models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "basic",subject=models.ImageSubject.objects.get(id=int(request.session['sub'])))
            intermediate_questions =  models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",subject=models.ImageSubject.objects.get(id=int(request.session['sub'])))
            advanced_questions =  models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "advance",subject=models.ImageSubject.objects.get(id=int(request.session['sub'])))
            options = models.ImageOption.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                        subject_id=models.ImageSubject.objects.get(
                                                                            id=int(request.session['sub'])))
            #getting basic qustioons according to page no
            context["basic_questions"] = basic_questions
            #getting intermediate qustioons according to page no
            context["intermediate_questions"] = intermediate_questions
            #getting basic qustioons according to page no
            context["advanced_questions"] = advanced_questions
            context["options"]=options
        else:
            return redirect('company:template_listing')
        # del request.session['sub']
        return render(request,"company/ATS/image-exam-view.html",context)
    else:
        return redirect('company:add_edit_profile')

def image_exam_edit(request,pk):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.ImageExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        
        exam_paper = models.ImageQuestionPaper.objects.get(exam_template= exam_template,company_id = models.Company.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        img_subject = exam_paper.exam_template.subject

        if exam_template.exam_type != "custom":
            return redirect('company:template_listing')

        basic_questions = models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "basic",subject=img_subject)
        intermediate_questions =  models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",subject=img_subject)
        advanced_questions =  models.ImageQuestion.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),question_level__level_name = "advance",subject=img_subject)
        options = models.ImageOption.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                    subject_id=img_subject)
        #getting basic qustioons according to page no
        context["basic_questions"] = basic_questions
        #getting intermediate qustioons according to page no
        context["intermediate_questions"] = intermediate_questions
        #getting basic qustioons according to page no
        context["advanced_questions"] = advanced_questions
        context["options"]=options
    

        if request.method == "POST":
            all_questions = json.loads(request.body.decode('UTF-8'))
            question_ids = [i for i in all_questions.keys()]
            print("all _questions",all_questions)
            print("request.pOOOOOOOOOOOOOOOOOOOOOST",request.POST)
            if exam_template.question_wise_time or exam_template.marking_system=="question_wise":
                # exam_paper = models.QuestionPaper.objects.get(exam_template=exam_template)
                exam_paper.exam_question_units.all().delete()

                for id in question_ids:
                    question = models.ImageQuestion.objects.get(id=id)
                    print("=================",id)
                    exam_question_unit = models.ImageExamQuestionUnit.objects.create(question=question,template=exam_template.template)
                    if exam_template.marking_system == "question_wise":
                        exam_question_unit.question_mark = all_questions[str(question.id)][0]#marks are stored at index 0
                    if exam_template.question_wise_time:
                        exam_question_unit.question_time = all_questions[str(question.id)][1] # time is stored at index 1
                    exam_question_unit.save()
                    exam_paper.exam_question_units.add(exam_question_unit)

                
            else:
                exam_template.basic_questions.clear()
                exam_template.intermediate_questions.clear()
                exam_template.advanced_questions.clear()
                for id in question_ids:
                    question = models.ImageQuestion.objects.get(id=id)
                    if question.question_level.level_name == "basic":
                        exam_template.basic_questions.add(question)
                    elif question.question_level.level_name == "intermediate":
                        exam_template.intermediate_questions.add(question)
                    else:
                        exam_template.advanced_questions.add(question)

            exam_template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit Image Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Create Image Template",
                                                                    description=description,
                                                                    target_url=header+"://"+current_site.domain+"/company/images_template_view/"+str(exam_template.template.id))


        # del request.session['sub']
        return render(request,"company/ATS/image-exam-edit.html",context)
    else:
        return redirect('company:add_edit_profile')

def image_create_exam(request,pk):
    exam_template = get_object_or_404(models.ImageExamTemplate,id=pk)
    question_paper = models.ImageQuestionPaper.objects.create(exam_template=exam_template,
                                                            company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id))
    # basic_questions = models.Question.objects.filter(question_level__level_name = "Basic")
    # intermediate_questions = models.Question.objects.filter(question_level__level_name = "Intermediate")
    # advanced_questions = models.Question.objects.filter(question_level__level_name = "Advanced")
    if exam_template.exam_type == "custom":
        question_data = json.loads(request.body.decode('UTF-8'))
        question_ids = [i for i in question_data.keys()]
        for id in question_ids:
            question = models.ImageQuestion.objects.get(id=id)
            print("=================",id)
            if exam_template.marking_system == "question_wise" or exam_template.question_wise_time:
                exam_question_unit = models.ImageExamQuestionUnit.objects.create(question=question,template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid'])))
                if exam_template.marking_system == "question_wise":
                    exam_question_unit.question_mark = question_data[str(question.id)][0]#marks are stored at index 0
                if exam_template.question_wise_time:
                    exam_question_unit.question_time = question_data[str(question.id)][1] # time is stored at index 1
                exam_question_unit.save()
                question_paper.exam_question_units.add(exam_question_unit)
            else:
                if question.question_level.level_name == "basic":
                    exam_template.basic_questions.add(question)
                elif question.question_level.level_name == "intermediate":
                    exam_template.intermediate_questions.add(question)
                else:
                    exam_template.advanced_questions.add(question)
        exam_template.save()
    exam_template.template.status = True
    exam_template.template.save()
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
    get_email=[]
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/company/images_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'Image Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
       
    all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
    description = template_name.name+" has been added to your workspace"
    for i in all_internal_users:
        if i.employee_id.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Image Template",
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/company/images_template_view/"+str(exam_template.template.id))
    print("question idsssss",question_ids)
    return HttpResponse("lolwa")


def image_get_basic_count(request):
    data = {}
    if request.method == 'POST':
        get_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='basic')
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        basic_count = models.ImageQuestion.objects.filter(subject=models.ImageSubject.objects.get(id=int(subject_data['subject_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id),question_level=get_type.id)
        print('++++++++++++++++++++++++++++++',len(basic_count))
        data['basic_count'] = len(basic_count)
        data['status'] = True
    else:
        data['basic_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))


def image_get_intermediate_count(request):
    data = {}
    if request.method == 'POST':
        get_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='intermediate')
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        intermediate_count = models.ImageQuestion.objects.filter(subject=models.ImageSubject.objects.get(id=int(subject_data['subject_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id),question_level=get_type.id)
        print('++++++++++++++++++++++++++++++',len(intermediate_count))
        data['intermediate_count'] = len(intermediate_count)
        data['status'] = True
    else:
        data['intermediate_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))


def image_get_advance_count(request):
    data = {}
    if request.method == 'POST':
        get_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='advance')
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        advance_count = models.ImageQuestion.objects.filter(subject=models.ImageSubject.objects.get(id=int(subject_data['subject_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id),question_level=get_type.id)
        print('++++++++++++++++++++++++++++++',len(advance_count))
        data['advance_count'] = len(advance_count)
        data['status'] = True
    else:
        data['advance_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))


# audio-video


def audio_template_view(request,template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if models.AudioExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id)).exists():
            questions = models.AudioExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id))
            exam_name=models.AudioExamTemplate.objects.get(template=models.Template_creation.objects.get(id=template_id))
            # questions = models.Descriptive.objects.filter(subject=subject_obj)
            print('questions',questions)
        else:
            questions = None
        context['questions']=questions
        context['exam_data']=exam_name
        return render(request,'company/ATS/audio_template_view.html',context)
    else:
        return redirect('company:add_edit_profile')

def audio_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        print(subject_name)
        subject_id = models.Audio_subject.objects.create(subject_name=subject_name['subject_name'],
                                                        company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_id.subject_name}
        return HttpResponse(json.dumps(data))


def audio_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.Audio_subject.objects.get(id=int(subject_data['sub_id']),
                                                             company_id=models.Company.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def audio_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.Audio_subject.objects.get(id=int(subject_data['sub_id']),
                                               company_id=models.Company.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def audio_list(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['subject'] = models.Audio_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            return render(request,'company/ATS/audio_all.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def audio_add(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        subject_obj = models.Audio_subject.objects.get(id=id)
        audio_que=models.Audio.objects.filter(subject=subject_obj,
                                                                company_id=models.Company.objects.get(user_id=request.user.id),created_at__date=datetime.datetime.today().date())
        if request.method == 'POST':
            audio_data = json.loads(request.body.decode('UTF-8'))
            audio_obj = models.Audio.objects.create(subject=subject_obj,
                                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                paragraph_description=audio_data['que'])
            data = {'id': audio_obj.id, 'paragraph_description': audio_obj.paragraph_description}
            return HttpResponse(json.dumps(data))
        context['sub_id']=id
        context['audio_que']=audio_que
        return render(request,'company/ATS/audio_add.html', context)
    else:
        return redirect('company:add_edit_profile')

def audio_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Question Bank':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            if models.Audio_subject.objects.filter(id=id).exists():
                subject_obj = models.Audio_subject.objects.get(id=id)
                questions = models.Audio.objects.filter(subject=models.Audio_subject.objects.get(id=id),company_id=models.Company.objects.get(user_id=request.user.id))
                context['questions']=questions
                context['sub_id'] = id
            else:
                questions = None
                context['questions'] = questions
                context['sub_id'] = id
            return render(request,'company/ATS/audio_view.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def delete_audio_question(request):
    if request.method == 'POST':
        desc_data = json.loads(request.body.decode('UTF-8'))
        models.Audio.objects.get(id=desc_data['que_id']).delete()
        return HttpResponse(True)


def audio_exam_template(request,template_id=None):
    # views added after templates
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if template_id:
            template = get_object_or_404(models.Template_creation,id=template_id)
            stage = template.stage
            category=template.category
            context['template_id'] = template_id
            exam_template = models.AudioExamTemplate.objects.filter(template=template)
            if exam_template.exists():
                context['exam_template']= exam_template[0]
        else:
            stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        subject = models.Audio_subject.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['subject'] = subject
        if request.method == "POST":
            if request.POST.get("exam_input_type") == "video":
                is_video = True
                print("is video true")
            else:
                is_video = False
                print("is video false")
            exam_template,update = models.AudioExamTemplate.objects.update_or_create(stage=stage,
                category=category,
                template=template,
                company_id=models.Company.objects.get(user_id=request.user.id),
                defaults={
                'subject':models.Audio_subject.objects.get(id=int(request.POST.get("language_name"))),
                'exam_name':request.POST.get("exam_name"),
                # exam_type=request.POST.get("examtype"),#will be removed
                'exam_type':"custom",#random is removed
                'total_question' :request.POST.get("no_of_total_questions"),
                'total_exam_time' : request.POST.get("total_exam_time") + ":00",
                'is_video' : is_video,
                'user_id':User.objects.get(id=request.user.id),})
            request.session['sub'] = int(request.POST.get("language_name"))
            return redirect('company:audio_exam_view', pk=exam_template.id)
        return render(request, "company/ATS/add-audio_exam.html", context)
    else:
        return redirect('company:add_edit_profile')

def audio_exam_view(request, pk):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.AudioExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        if exam_template.exam_type == "custom":
            audio_questions = models.Audio.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                subject=models.Audio_subject.objects.get(
                                                                    id=int(request.session['sub'])))

        # getting basic qustioons according to page no
        print(audio_questions)
        context["basic_questions"] = audio_questions
        # del request.session['sub']
        return render(request, "company/ATS/audio_exam-view.html", context)
    else:
        return redirect('company:add_edit_profile')
def audio_exam_edit(request, pk):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        exam_template = models.AudioExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        exam_paper = models.AudioQuestionPaper.objects.get(exam_template= exam_template,company_id = models.Company.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        audio_subject = exam_paper.exam_template.subject

        if exam_template.exam_type == "custom":
            audio_questions = models.Audio.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                                subject = audio_subject)

        # getting basic qustioons according to page no
        print(audio_questions)
        context["basic_questions"] = audio_questions
        # del request.session['sub']

        if request.method =="POST":
            all_questions = json.loads(request.body.decode('UTF-8'))
            question_ids = [i for i in all_questions.keys()]
            print("all _questions",all_questions)
            print("request.pOOOOOOOOOOOOOOOOOOOOOST",request.POST)
            # if exam_template.question_wise_time or exam_template.marking_system=="question_wise":
            #     # exam_paper = models.QuestionPaper.objects.get(exam_template=exam_template)
            exam_paper.exam_question_units.all().delete()

            for id in question_ids:
                question = models.Audio.objects.get(id=id)
                print("=================",id)
                exam_question_unit = models.AudioExamQuestionUnit.objects.create(question=question,template=exam_template.template)
                exam_question_unit.question_mark = all_questions[str(question.id)][0]#marks are stored at index 0
                exam_question_unit.question_time = all_questions[str(question.id)][1] # time is stored at index 1
                exam_question_unit.save()
                exam_paper.exam_question_units.add(exam_question_unit)

            exam_template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit Audio Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Edit Audio Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/company/audio_template_view/"+str(exam_template.template.id))

            return redirect('company:template_listing')
        return render(request, "company/ATS/audio_exam-edit.html", context)
    else:
        return redirect('company:add_edit_profile')
    
def audio_create_exam(request, pk):
    exam_template = get_object_or_404(models.AudioExamTemplate, id=pk)
    user = User.objects.get(id=request.user.id)
    question_paper = models.AudioQuestionPaper.objects.create(exam_template=exam_template, company_id=models.Company.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id))
    if exam_template.exam_type == "custom":
        question_data = json.loads(request.body.decode('UTF-8'))
        question_ids = [i for i in question_data.keys()]
        for id in question_ids:
            question = models.Audio.objects.get(id=id)
            exam_question_unit = models.AudioExamQuestionUnit.objects.create(question=question,template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid'])))
            exam_question_unit.question_mark = question_data[str(question.id)][0]  # marks are stored at index 0
            exam_question_unit.question_time = question_data[str(question.id)][1]
            exam_template.audioquestions.add(question)# time is stored at index 1
            exam_question_unit.save()
            question_paper.exam_question_units.add(exam_question_unit)
        exam_template.save()
    exam_template.template.status = True
    exam_template.template.save()
    all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    get_email=[]
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/company/audio_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'Audio Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    description = template_name.name+" has been added to your workspace"
    all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
    for i in all_internal_users:
        if i.employee_id.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Audio Template",
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/company/audio_template_view/"+str(exam_template.template.id))

    return HttpResponse('lolwa')
# end later views




def audio_get_count(request):
    data = {}
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        basic_count = models.Audio.objects.filter(subject=models.Audio_subject.objects.get(id=int(subject_data['subject_id'])),
                                                           company_id=models.Company.objects.get(user_id=request.user.id))
        print('++++++++++++++++++++++++++++++',len(basic_count))
        data['basic_count'] = len(basic_count)
        data['status'] = True
    else:
        data['basic_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))


def request_page(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Accept'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Agency Request':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Accept/Reject':
                    context['Accept'] = True
        if context['Accept']:
            print(request.user.id)
            pending_connections = AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=False,is_rejected=False)#here will be filter query later
            active_connections = AgencyModels.CompanyAgencyConnection.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=True,is_rejected=False)#here will be filter query later
            context['active_connections'] = active_connections
            context['pending_connections'] = pending_connections
            return render(request,'company/ATS/connection_request.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def active_connection_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['accept_job_count']=0
        context['applied_candidate_count']=0
        job_submit_resume={}
        context['company_profile']=models.CompanyProfile.objects.get(company_id=models.Company.objects.get(user_id=request.user.id))
        client_detail = AgencyModels.CompanyAgencyConnection.objects.get(id=id,company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=True,is_rejected=False)#here will be filter query later
        get_agency_type=AgencyModels.AgencyType.objects.get(agency_id=client_detail.agency_id)
        if get_agency_type.is_agency:
            context['agency_profile']=AgencyModels.AgencyProfile.objects.get(agency_id=client_detail.agency_id)
            if AgencyModels.AgencyProfile.objects.filter(agency_id=client_detail.agency_id).exists():
                context['agencyprofile'] = AgencyModels.AgencyProfile.objects.get(agency_id=client_detail.agency_id)
        if get_agency_type.is_freelancer:
            context['agency_profile'] = AgencyModels.FreelancerProfile.objects.get(agency_id=client_detail.agency_id)
            if AgencyModels.FreelancerProfile.objects.filter(agency_id=client_detail.agency_id).exists():
                context['agencyprofile'] = AgencyModels.FreelancerProfile.objects.get(agency_id=client_detail.agency_id)
        if models.AssignExternal.objects.filter(recruiter_id=client_detail.agency_id,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
            context['accept_job']=models.AssignExternal.objects.filter(recruiter_id=client_detail.agency_id,company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=True)
            for jobs in context['accept_job']:
                print(jobs.job_id)
                jobsubmitresume = models.AssociateCandidateAgency.objects.filter(agency_id=client_detail.agency_id,job_id=jobs.job_id,company_id=models.Company.objects.get(user_id=request.user.id))
                job_submit_resume[jobs.job_id] =jobsubmitresume.count()
            context['accept_job_count']=context['accept_job'].count()
        if models.AssociateCandidateAgency.objects.filter(agency_id=client_detail.agency_id,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
            context['applied_candidate']=models.AssociateCandidateAgency.objects.filter(agency_id=client_detail.agency_id,company_id=models.Company.objects.get(user_id=request.user.id)).distinct('candidate_id')
            context['applied_candidate_count']=context['applied_candidate'].count()
        context['job_submit_resume']=job_submit_resume
        print(job_submit_resume)
        context['client_detail'] = client_detail
        return render(request,'company/ATS/all_recruiter_view.html',context)
    else:
        return redirect('company:add_edit_profile')
def request_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        client_detail = AgencyModels.CompanyAgencyConnection.objects.get(id=id,company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=False,is_rejected=False)#here will be filter query later
        context['client_detail'] = client_detail
        return render(request,'company/ATS/agency-connection.html',context)
    else:
        return redirect('company:add_edit_profile')
def request_view(request,id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        client_detail = AgencyModels.CompanyAgencyConnection.objects.get(id=id,company_id=models.Company.objects.get(user_id=request.user.id),is_accepted=False,is_rejected=False)#here will be filter query later
        context['client_detail'] = client_detail
        return render(request,'company/ATS/agency-connection.html',context)
    else:
        return redirect('company:add_edit_profile')

def update_connection(request):
    print(request.GET)
    connection_id = request.GET.get('connection_id')
    status = request.GET.get('status')
    is_rejected = False
    if status == 'true':
        status = True
        
    else:
        is_rejected = True
        status = False
    connection = AgencyModels.CompanyAgencyConnection.objects.get(id=connection_id)
    connection.is_accepted = status
    connection.is_rejected = is_rejected
    connection.save ()
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    if status :
        for i in [connection.agency_id.agency_id.id]:
            description = connection.company_id.company_id.company_name+" has accepted your Connection Request"
            if i != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i),verb="Accept Connect Request",
                                                                    description=description,image="/static/notifications/icon/company/Accept.png",
                                                                    target_url=header+"://"+current_site.domain+"/agency/active_connection_view/" + str(
                                                                        connection.id))
    else:
        for i in [connection.agency_id.agency_id.id]:
            description = connection.company_id.company_id.company_name+" has declined your Connection Request"
            if i != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i),verb="Declined Connect Request",
                                                                    description=description,image="/static/notifications/icon/company/decline.png",
                                                                    target_url=header+"://"+current_site.domain+"/agency/active_connection_view/" + str(
                                                                        connection.id))
    return HttpResponse(True)


# APPLIED CANDIDATES VIEW


def collaboration(request):
    if request.method == 'POST':
        job_obj = models.JobCreation.objects.get(id=request.POST.get('job_id'))
        candidate_obj = User.objects.get(id=request.POST.get('candidate_id'))
        if request.FILES.get('attachfile-box'):
            attachment = request.FILES.get('attachfile-box')
        else:
            attachment = None
        collaboration_obj = models.Collaboration.objects.create(company_id=job_obj.company_id,
                                            candidate_id=candidate_obj,
                                            job_id=job_obj,
                                            user_id=User.objects.get(id=request.user.id),
                                            comment=request.POST.get('msg-box'),
                                            attachment=attachment)
        time = collaboration_obj.create_at.strftime("%Y-%m-%d %I:%M %p")
        if collaboration_obj.attachment:
            file = collaboration_obj.attachment.url
        else:
            file = None
        return HttpResponse(json.dumps({'attachment':file,
                                        'comment':collaboration_obj.comment,
                                        'user':collaboration_obj.user_id.company_name,'time':time},default=str))
    else:
        return HttpResponse(False)


def get_job_stages(request):
    if request.GET.get('job_id'):
        job_obj = models.JobCreation.objects.get(id=request.GET.get('job_id'))
        if models.JobWorkflow.objects.filter(job_id=job_obj).exists():
            job_workflow = models.JobWorkflow.objects.get(job_id=job_obj)
            stages=[]
            if job_workflow.withworkflow:
                main_workflow = models.Workflows.objects.get(id=job_workflow.workflow_id.id)
                workflow_stages = models.WorkflowStages.objects.filter(workflow=main_workflow,display=True).order_by('sequence_number')
                for stage in workflow_stages:
                    data_dict = {'id':stage.stage.id,'text':stage.stage.name}
                    stages.append(data_dict)
            if job_workflow.onthego:
                onthego_stages = models.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')
                for stage in onthego_stages:
                    data_dict = {'id': stage.stage.id, 'text': stage.stage.name}
                    stages.append(data_dict)
            return HttpResponse(json.dumps(stages))
        else:
            return HttpResponse(False)
    else:
        return HttpResponse(False)

def get_job_users(request):
    if request.GET.get('job_id'):
        job_obj = models.JobCreation.objects.get(id=request.GET.get('job_id'))
        if models.CompanyAssignJob.objects.filter(job_id=job_obj).exists():
            get_users = models.CompanyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True)
            users=[]
            if get_users:
                for user in get_users:
                    data_dict = {'id':user.recruiter_id.id,'text':user.recruiter_id.first_name}
                    users.append(data_dict)
            return HttpResponse(json.dumps(users))
        else:
            return HttpResponse(False)
    else:
        return HttpResponse(False)
def dept_add_or_update_view(request):
    print("addddddddddddd viewwwwwwwwwwwwwwwwwwww",request.user.id)
    context = {}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Department':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['departments'] = models.Department.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            if request.method == "POST":
                id= request.POST.get("department_id")
                department_name = request.POST.get("department_name")
                # department,created = models.Department.objects.get_or_create(name=department_name)
                try:
                    department = models.Department.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),name__iexact=department_name)
                    created=False
                except:
                    created = True
                    print("no department with that id found")
                data = {}
                if created == False:
                    data["status"] = created
                    return HttpResponse(json.dumps(data))
                if id == "null":
                    department = models.Department.objects.create(name=department_name,status=True,company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),user_id=User.objects.get(id=request.user.id))
                    operation = "created"
                    role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                    get_admin = models.Employee.objects.filter(role=role_id_get, company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
                    for i in get_admin:
                        description = request.user.first_name + " Create Department"
                        if i != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i), verb="Create Department",
                                        description=description,
                                        target_url=header+"://"+current_site.domain+"/company/dept_add_or_update_view/")
                else:
                    department = models.Department.objects.get(id=int(id))
                    department.name = department_name
                    department.save()
                    operation = "update"
                    role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                    get_admin = models.Employee.objects.filter(role=role_id_get, company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
                    for i in get_admin:
                        description = request.user.first_name + " Update Department"
                        if i != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Department",
                                        description=description,
                                        target_url=header+"://"+current_site.domain+"/company/dept_add_or_update_view/")
                # if
                data["status"] = created
                data['operation'] = operation
                data['department_name'] =department.name
                data['department_id'] =department.id
                return HttpResponse(json.dumps(data))
            return render(request,"company/ATS/add_department.html",context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')
def create_employee_id():
    link = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(9)])
    if models.Employee.objects.filter(unique_id=link).exists():
        return create_employee_id()
    else:
        return link
def user_add_or_update_view(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalUser':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['departments'] = models.Department.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            context['role'] = models.Role.objects.filter(
                company_id=models.Company.objects.get(user_id=request.user.id))
            context['employees'] = models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            if request.method == "POST":
                f_name=request.POST.get("fname")
                l_name=request.POST.get("lname")
                email=request.POST.get("work_email")
                id = request.POST.get("update_id")
                password = get_random_string(length=12)
                x_forwarded_for=None
                if id == "null":
                    operation= "create"
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
                if User.objects.filter(email=email.lower()).exists():
                    operation = "updated"
                    context['message'] = "email already exists"
                    internal_user=models.Employee.objects.get(id=request.POST.get("update_id"),company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)))
                    internal_user.first_name = request.POST.get("fname")
                    internal_user.last_name = request.POST.get("lname")
                    internal_user.department=models.Department.objects.get(id=request.POST.get("department"))
                    internal_user.role=models.Role.objects.get(id=request.POST.get("role"))
                    internal_user.contact_num=request.POST.get("contact_number")
                    if request.FILES.get("profile_pic"):
                        internal_user.profile_pic = request.FILES.get("profile_pic")
                    internal_user.save()
                    user_update=User.objects.get(email=email.lower())
                    user_update.first_name = request.POST.get("fname")
                    user_update.last_name = request.POST.get("lname")
                    user_update.save()
                    data = {}
                    data['employee_id'] = internal_user.id
                    data['employee_name'] = internal_user.first_name+' '+internal_user.last_name
                    data['employee_department'] = internal_user.department.name
                    data['employee_role'] = internal_user.role.name
                    data['employee_work_email'] = email
                    data['employee_contact_num'] = internal_user.contact_num
                    data['operation'] = operation
                    role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                    get_admin = models.Employee.objects.filter(role=role_id_get, company_id=models.Company.objects.get(
                        user_id=request.user)).values_list('employee_id', flat=True)
                    current_site = get_current_site(request)
                    header=request.is_secure() and "https" or "http"    
                    for i in get_admin:
                        description = request.user.first_name + "Update Internal User"
                        if i != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Internal User",
                                        description=description,
                                        target_url=header+"://"+current_site.domain+"/company/user_add_or_update_view/")
                # else:
                #     print('created')
                #     operation="created"
                #     usr = User.objects.create_internal_company(email=email.lower(),first_name=f_name,last_name=l_name,
                #                                         password=password, ip=ip, device_type=device_type,
                #                                         browser_type=browser_type,
                #                                         browser_version=browser_version, os_type=os_type,
                #                                         os_version=os_version)

                #     mail_subject = 'Your Account has been created'
                #     current_site = get_current_site(request)
                #     print('domain----===========',current_site.domain)
                #     html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                #                                                                         'name': f_name + ' ' + l_name,
                #                                                                         'email': email,
                #                                                                         'domain': current_site.domain,
                #                                                                         'password': password, })
                #     to_email = usr.email
                #     from_email = settings.EMAIL_HOST_USER
                #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                #     msg.attach_alternative(html_content, "text/html")
                #     msg.send()
                #     companyidget=models.Company.objects.get(user_id=User.objects.get(id=request.user.id))
                #     companyidget.user_id.add(User.objects.get(email=email.lower()))
                #     profile_pic = None
                #     if request.FILES.get("profile_pic"):
                #         profile_pic = request.FILES.get("profile_pic")
                #     internal_user = models.Employee.objects.create(first_name=f_name, last_name=l_name,
                #                                                 department=models.Department.objects.get(
                #                                                     id=request.POST.get("department")),
                #                                                 role=models.Role.objects.get(
                #                                                     id=request.POST.get("role")),
                #                                                 employee_id=User.objects.get(email=email.lower()),
                #                                                 contact_num=request.POST.get("contact_number"),
                #                                                 company_id=companyidget,
                #                                                 user_id=User.objects.get(id=request.user.id),
                #                                                 unique_id=create_employee_id(),
                #                                                 profile_pic=profile_pic)
                #     data={}
                #     data['employee_id'] =internal_user.id
                #     data['employee_name'] =internal_user.first_name +' '+internal_user.last_name
                #     data['employee_department'] =internal_user.department.name
                #     data['employee_role'] =internal_user.role.id
                #     data['employee_work_email'] =email
                #     data['employee_contact_num'] =internal_user.contact_num
                #     data['operation'] = operation
                #     role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                #                                         name="SuperAdmin")
                #     get_admin = models.Employee.objects.filter(role=role_id_get, company_id=models.Company.objects.get(
                #         user_id=request.user)).values_list('employee_id', flat=True)
                #     all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                #         user_id=request.user)).values_list('employee_id', flat=True)
                #     get_email=[]
                #     for j in all_internaluser:
                #         get_email.append(User.objects.get(id=j).email)
                #     mail_subject = 'New User has been added'
                #     html_content = render_to_string('company/email/new_user_add.html',{'fname':f_name,'lname':l_name,'email':email,'password':password})
                #     from_email = settings.EMAIL_HOST_USER
                #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
                #     msg.attach_alternative(html_content, "text/html")
                #     msg.send()
                #     current_site = get_current_site(request)
                #     header=request.is_secure() and "https" or "http"  
                #     for i in get_admin:
                #         description = "New user "+f_name+" "+l_name+" has been added to your workspace."
                #         if i != request.user.id:
                #             notify.send(request.user, recipient=User.objects.get(id=i), verb="New user Add",
                #                         description=description,image="/static/notifications/icon/company/user_added.png",
                #                         target_url=header+"://"+current_site.domain+"/company/user_add_or_update_view/")
            return render(request,"company/ATS/user_add_view.html",context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')


def delete_department(request):
    dept_id = request.POST.get("department_id")
    department = models.Department.objects.get(id=int(dept_id))
    department.delete()
    return HttpResponse("true")


def delete_employee(request):
    employee_id = request.POST.get("employee_id")
    print("the employeeeee idddddddddd",employee_id)
    employee = models.Employee.objects.get(id=int(employee_id))
    employee.delete()
    return HttpResponse("haha")


def get_employee(request):
    if request.method == "POST":
        id=request.POST.get("employee_id")
        employee = models.Employee.objects.get(id=int(id))
        data={}
        data['employee_id'] = employee.id
        data['employee_fname'] = employee.first_name
        data['employee_lname'] = employee.last_name
        data['employee_department'] = employee.department.id
        data['employee_role'] = employee.role.id
        data['employee_work_email'] = employee.employee_id.email
        data['employee_contact_num'] = employee.contact_num
        if employee.profile_pic:
            data['profile_pic'] = employee.profile_pic.url
        return HttpResponse(json.dumps(data))


def get_department(request):
    if request.method == "POST":
        id=request.POST.get("department_id")
        department = models.Department.objects.get(id=int(id))
        data = {}
        data['department_id'] =department.id
        data['department_name'] =department.name
        return HttpResponse(json.dumps(data))


def applied_candidates_view(request, id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['SalaryView'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Salary':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        job_obj = models.JobCreation.objects.get(id=id)
        job_workflow_obj = models.JobWorkflow.objects.get(job_id=job_obj)
        candidates = models.AppliedCandidate.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            job_id=job_obj)
        
        candidates_array = [i.candidate.id for i in candidates]
        
        agency_submit_candidate=models.AssociateCandidateAgency.objects.filter(job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id)).values_list('candidate_id',flat=True)
        candidates_array=list(chain(candidates_array))

        candidate_job_apply_detail = CandidateModels.candidate_job_apply_detail.objects.filter(
            candidate_id__in=candidates_array)
        candidate_stages_data = []
        secure = False
        candidatetype = ''
        candidate_fname=''
        resume=''
        contactno=''
        requested=''
        header=request.is_secure() and "https" or "http"
        current_site = get_current_site(request)
        # onthego change
        if request.method == 'POST':
            if 'add_stage_submit' in request.POST:
                stage_id = CandidateModels.Stage_list.objects.get(id=request.POST.get('stage'))
                template_id = models.Template_creation.objects.get(id=request.POST.get('template'))

                if models.OnTheGoStages.objects.filter(job_id=job_obj,template=template_id).exists():
                    flag = False
                else:
                    flag = True
                    onthego_stages = models.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')
                    onthego_last_stages = onthego_stages.last()
                    new_created_stage = models.OnTheGoStages.objects.create(job_id=job_obj,
                                                        company_id=job_obj.company_id,
                                                        stage=stage_id,
                                                        stage_name=request.POST.get('stage_name'),
                                                        user_id=request.user,
                                                        template=template_id,
                                                        sequence_number=int(onthego_last_stages.sequence_number) + 1)
                    for candidate in candidates_array:
                        notify.send(request.user, recipient=User.objects.get(id=candidate), verb="New stage",
                                    description="New stage has been added to your profile for the job "+job_obj.job_title+". Please visit to appear for interview round.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/company")
        company_id = models.Company.objects.get(user_id=request.user.id)
        for candidate_id in candidates_array:
            candidate_obj = User.objects.get(id=candidate_id)

            if request.method == 'POST':
                if 'add_stage_submit' in request.POST:
                    if flag:
                        if models.CandidateJobStagesStatus.objects.filter(candidate_id=User.objects.get(id=candidate_id),
                                                                        job_id=job_obj,template=template_id).exists():
                            print('exists')
                        else:
                            candidate_job_stages = models.CandidateJobStagesStatus.objects.filter(company_id=company_id,
                                                                                                candidate_id=candidate_obj,
                                                                                                job_id=job_obj).order_by('sequence_number')
                            candidate_job_last_stage = candidate_job_stages.last()

                            if candidate_job_last_stage.stage.name != 'Job Offer':
                                if candidate_job_last_stage.status != -1:
                                    status = 0
                                    if candidate_job_last_stage.action_performed or candidate_job_last_stage.stage.name == 'Job Applied':
                                        status = 1
                                    models.CandidateJobStagesStatus.objects.create(company_id=company_id,candidate_id=candidate_obj,
                                                                                job_id=job_obj,stage=new_created_stage.stage,
                                                                                template=new_created_stage.template,
                                                                                sequence_number=int(candidate_job_last_stage.sequence_number) + 1,
                                                                                status=status,custom_stage_name=request.POST.get('stage_name'))

            stages = models.CandidateJobStagesStatus.objects.filter(company_id=company_id,
                                                                    candidate_id=candidate_obj,
                                                                    job_id=job_obj).order_by('sequence_number')

            current_stage = ''
            if len(stages.filter(status=1))==0:
                current_stage = 'Waiting For Stage'
            else:
                current_stage = stages.filter(status=1)[0].stage.name
            # secure_resume
            if candidate_id in agency_submit_candidate:
                candidatetype = 'External'
            else:
                candidatetype = 'Internal'
            candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(
                candidate_id=User.objects.get(id=candidate_id))
            if AgencyModels.CandidateSecureData.objects.filter(candidate_id=User.objects.get(id=candidate_id),job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
                data=AgencyModels.CandidateSecureData.objects.get(candidate_id=User.objects.get(id=candidate_id),job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id))
                
                if data.is_accepted:
                    candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(
                        candidate_id=User.objects.get(id=candidate_id))
                    resume = candidate_detail.resume.url
                    contactno=candidate_detail.contact
                    candidate_fname=candidate_detail.candidate_id.first_name+' '+candidate_detail.candidate_id.last_name
                    secure = False
                    requested=False
                elif data.is_request:
                    get_agency=models.AssociateCandidateAgency.objects.get(candidate_id=User.objects.get(id=candidate_id),job_id=job_obj)
                    agency_candidate_detail=AgencyModels.InternalCandidateBasicDetail.objects.get(candidate_id=User.objects.get(id=candidate_id),agency_id=get_agency.agency_id)
                    secure = True
                    requested = True
                    resume = agency_candidate_detail.secure_resume_file.url
                    candidate_fname=agency_candidate_detail.candidate_custom_id
                elif not data.is_request:
                    get_agency = models.AssociateCandidateAgency.objects.get(candidate_id=User.objects.get(id=candidate_id),
                                                                            job_id=job_obj)
                    agency_candidate_detail = AgencyModels.InternalCandidateBasicDetail.objects.get(
                        candidate_id=User.objects.get(id=candidate_id), agency_id=get_agency.agency_id)
                    secure = True
                    requested = False
                    if agency_candidate_detail.secure_resume_file:
                        resume = agency_candidate_detail.secure_resume_file.url
                    else:
                        resume=agency_candidate_detail.resume.url
                    candidate_fname=agency_candidate_detail.candidate_custom_id
            else:
                resume = candidate_detail.resume.url
                contactno = candidate_detail.contact
                candidate_fname = candidate_detail.candidate_id.first_name + ' ' + candidate_detail.candidate_id.last_name
            print("==============================",resume)
            data = {'id': User.objects.get(id=candidate_id), 'current_stage':current_stage,'stages': stages,'requested':requested, 'candidate_detail':candidate_detail,'secure': secure,'candidatetype':candidatetype,'contactno':contactno,'resume':resume,'candidate_fname':candidate_fname}
            candidate_stages_data.append(data)
        context['candidates']= candidate_job_apply_detail
        context['candidate_stages_data']= candidate_stages_data
        context['job_obj']=job_obj
        context['job_id']= job_obj.id
        context['job_workflow_obj']=job_workflow_obj
        return render(request, "company/ATS/applied-candidate-view.html",context)
    else:
        return redirect('company:add_edit_profile')

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.safestring import mark_safe


def company_portal_candidate_tablist(request, candidate_id, job_id):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        SalaryView = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Salary':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    SalaryView = True
        job_obj = models.JobCreation.objects.get(id=job_id)
        candidate_obj = User.objects.get(id=candidate_id)
        company_id = models.Company.objects.get(user_id=request.user.id)
        job_workflow_obj = models.JobWorkflow.objects.get(job_id=job_obj)
        chat=''
        groupmessage=''
        uniquecode=''
        all_assign_users = models.CompanyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True)
        if ChatModels.GroupChat.objects.filter(job_id=job_obj).exists():
            chat = ChatModels.GroupChat.objects.get(job_id=job_obj,candidate_id=candidate_obj)
            groupmessage=ChatModels.Message.objects.filter(chat=chat)
            uniquecode=mark_safe(json.dumps(chat.unique_code))
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{chat.unique_code}",
                {
                    'type': 'chat_activity',
                    'message': json.dumps({'type': "join", 'first_name': request.user.id})
                }
            )
        current_stage = ''
        currentcompleted=False
        next_stage = None
        action_required=''
        reject=False
        schedule_interview=False
        add_stage_submit=False
        withdraw_candidate=False
        hire_candidate=False
        reenter_candidate=False
        shortlist_candidate=False
        reject_candidate=False
        onhold_candidate=False
        id_resume=None
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"
        if request.method == 'POST':
            if 'schedule_interview' in request.POST:
                if request.POST.get('interview_stage'):
                    stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('interview_stage'))
                    print('interviewers', request.POST.getlist('interviewers'))
                    in_time = datetime.datetime.strptime(request.POST.get('interview_time'), "%I:%M %p")
                    out_time = datetime.datetime.strftime(in_time, "%H:%M")
                    meridiem = request.POST.get('interview_time').split(' ')[1]
                    interview_template = models.InterviewTemplate.objects.get(company_id=stage_obj.company_id,
                                                                            template_id=stage_obj.template)
                    schedule_obj, created = models.InterviewSchedule.objects.update_or_create(candidate_id=candidate_obj,
                                                                                            job_id=job_obj,
                                                                                            company_id=stage_obj.company_id,
                                                                                            template=stage_obj.template,
                                                                                            job_stages_id=stage_obj,
                                                                                            interview_template=interview_template,
                                                                                            defaults={
                                                                                                'date': request.POST.get(
                                                                                                    'interview_date'),
                                                                                                'time': out_time,
                                                                                                'user_id': User.objects.get(
                                                                                                    id=request.user.id),
                                                                                                'interview_duration': request.POST.get(
                                                                                                    'interview_duration'),
                                                                                                'meridiem': meridiem,
                                                                                                'status': 1,
                                                                                                'is_accepted': False,
                                                                                            })
                    notify.send(request.user, recipient=candidate_obj, verb="Inteview",
                                    description="You have been invited for live interview on "+request.POST.get('interview_date')+" "+out_time+". Please confirm.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/company")
                    for participant in request.POST.getlist('interviewers'):
                        participant_obj = User.objects.get(id=participant)
                        schedule_obj.participants.add(participant_obj)
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=stage_obj.company_id,defaults={
                                                                    'action_required':'Accept Interview By Candidate','update_at':datetime.datetime.now()})
                else:
                    return HttpResponse('Something Went Wrong')

            elif 'add_stage_submit' in request.POST:
                add_stage_submit=True
                stage_id = CandidateModels.Stage_list.objects.get(id=request.POST.get('stage'))
                template_id = models.Template_creation.objects.get(id=request.POST.get('template'))

                if models.CandidateJobStagesStatus.objects.filter(candidate_id=candidate_obj,job_id=job_obj, template=template_id).exists():
                    print('Template Already assigned to this candidate')
                    messages.error(request, 'Template Already assigned to this candidate.')
                else:
                    candidate_job_stages = models.CandidateJobStagesStatus.objects.filter(company_id=company_id,
                                                                                        candidate_id=candidate_obj,
                                                                                        job_id=job_obj).order_by('sequence_number')
                    candidate_job_last_stage = candidate_job_stages.last()

                    if candidate_job_last_stage.stage.name != 'Job Offer':
                        if candidate_job_last_stage.status != -1:
                            status = 0
                            if candidate_job_last_stage.action_performed or candidate_job_last_stage.stage.name == 'Job Applied':
                                status = 1
                            models.CandidateJobStagesStatus.objects.create(company_id=company_id,
                                                                        candidate_id=candidate_obj,
                                                                        job_id=job_obj, stage=stage_id,
                                                                        template=template_id,
                                                                        sequence_number=int(candidate_job_last_stage.sequence_number) + 1,
                                                                        status=status,custom_stage_name=request.POST.get('stage_name'))
                            notify.send(request.user, recipient=candidate_obj, verb="New stage",
                                    description="New stage has been added to your profile for the job "+job_obj.job_title+". Please visit to appear for interview round.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/company")
            elif 'withdraw_candidate' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=models.Company.objects.get(user_id=request.user.id),
                                                                defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
                models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=company_id,defaults={
                                                                    'withdraw':True,'update_at':datetime.datetime.now()})
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                notify.send(request.user, recipient=candidate_obj, verb="Withdraw",
                                description="You have withdrawn your application from Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/company")
                job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                if not current_stage==None:
                    for i in all_assign_users:
                        if i.recruiter_type_internal:
                            if i.recruiter_id.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Withdraw",
                                                                                    description=candidate_obj.first_name+" "+candidate_obj.last_name+" has been withdrawn your from Job"+str(job_obj.job_title),image="/static/notifications/icon/company/Application_Review.png",
                                                                                    target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                        job_obj.id))
            elif 'hire_candidate' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=company_id,
                                                                defaults={
                                                                    'hire_by': User.objects.get(id=request.user.id),
                                                                    'is_hired': True})
                job_stages = models.CandidateJobStagesStatus.objects.filter(
                    company_id=company_id,
                    candidate_id=candidate_obj,
                    job_id=job_obj).order_by('sequence_number').last()
                job_workflow = models.JobWorkflow.objects.get(job_id=job_obj)
                if job_workflow.withworkflow:
                    job_stages.status = 1
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=company_id,defaults={
                                                                    'current_stage':job_stages.stage,'next_stage':None,
                                                                    'action_required':'By Company','update_at':datetime.datetime.now()})
                    job_stages.save()
                if job_workflow.onthego:
                    job_offer_stage = CandidateModels.Stage_list.objects.get(name='Job Offer')
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=company_id,defaults={
                                                                    'current_stage':job_offer_stage,'next_stage':None,
                                                                    'action_required':'By Company','update_at':datetime.datetime.now()})
                    models.CandidateJobStagesStatus.objects.create(company_id=company_id,candidate_id=candidate_obj,
                        job_id=job_obj,stage=job_offer_stage,sequence_number=int(job_stages.sequence_number) + 1,status=1,custom_stage_name='Job Offer')

            elif 'reenter_candidate' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=models.Company.objects.get(
                                                                    user_id=request.user.id),
                                                                defaults={
                                                                    'withdraw_by': None,
                                                                    'is_withdraw': False})

            else:
                stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
                if 'shortlist' in request.POST:
                    stage_obj.action_performed = True
                    shortlist_candidate=True
                    stage_obj.status = 2
                    current_stage=stage_obj.stage
                    stage_obj.save()
                    notify.send(request.user, recipient=candidate_obj, verb="Application Shortlisted",
                                description="Your profile has been shortlisted, please wait for further instruction.",image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_id)+"/company")

                    new_sequence_no = stage_obj.sequence_number + 1
                    if models.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=candidate_obj,
                                                            sequence_number=new_sequence_no).exists():
                        new_stage_status = models.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=candidate_obj,
                                                                                    sequence_number=new_sequence_no)
                        new_stage_status.status = 1
                        current_stage=new_stage_status.stage
                        if models.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=candidate_obj,
                                                            sequence_number=new_sequence_no+1).exists():
                            stage_status = models.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=candidate_obj,
                                                                                    sequence_number=new_sequence_no+1)
                            next_stage=stage_status.stage

                        if new_stage_status.stage.name=='Interview' :
                            action_required='schedule interview By Company'
                        else:
                            action_required='Perform '+ ' '+'By Candidate'
                        new_stage_status.save()
                        notify.send(request.user, recipient=candidate_obj, verb="Interview Round",
                                description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/company")
                if 'reject' in request.POST:
                    stage_obj.status = -1
                    stage_obj.action_performed = True
                    stage_obj.assessment_done = True
                    reject=True
                    current_stage=stage_obj.stage
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=stage_obj.company_id,defaults={
                                                                    'reject':True,
                                                                    'update_at':datetime.datetime.now()})
                    stage_obj.save()
                    notify.send(request.user, recipient=candidate_obj, verb="Application Rejected",
                                description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/company")
                if 'onhold' in request.POST:
                    stage_obj.status = 3
                    stage_obj.action_performed = False
                    current_stage=stage_obj.stage
                    action_required='OnHold'
                    new_sequence_no = stage_obj.sequence_number + 1
                    if models.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=candidate_obj,
                                                            sequence_number=new_sequence_no).exists():
                        new_stage_status = models.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=candidate_obj,
                                                                                    sequence_number=new_sequence_no)
                        next_stage=new_stage_status.stage
                    stage_obj.save()
                models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,company_id=stage_obj.company_id,defaults={
                                                                    'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,
                                                                    'action_required':action_required,'update_at':datetime.datetime.now()})
        if AgencyModels.CandidateSecureData.objects.filter(candidate_id=candidate_obj,company_id=company_id,job_id=job_obj).exists():
            id_resume=AgencyModels.CandidateSecureData.objects.get(candidate_id=candidate_obj,company_id=company_id,job_id=job_obj)
        candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(candidate_id=candidate_obj)
        internal_users = models.Employee.objects.filter(company_id=company_id)
        stages_status = models.CandidateJobStagesStatus.objects.filter(company_id=company_id,
                                                                    candidate_id=candidate_obj,
                                                                    job_id=job_obj).order_by('sequence_number')
        interview_schedule_data = None
        job_offer_data = None
        custom_stage_template = None
        custom_template_status = False

        stages_data = []
        for stage in stages_status:
            stage_dict = {'stage': stage, 'result': ''}

            if stage.stage.name == 'Interview':
                print('\n\nin Interview')
                interview_schedule_obj = models.InterviewSchedule.objects.filter(candidate_id=candidate_obj,job_id=job_obj,
                                                        company_id=stage.company_id,
                                                        template=stage.template,
                                                        job_stages_id=stage)
                if interview_schedule_obj.exists():
                    interview_schedule_data = interview_schedule_obj[0]
            if stage.stage.name == 'Job Offer':
                print('\n\nin Job Offer')
                job_offer_obj = models.JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
                                                                                company_id=stage.company_id,
                                                                                job_stages_id=stage)
                if job_offer_obj.exists():
                    job_offer_data = job_offer_obj[0]
            if stage.stage.name == 'Custom':
                custom_stage_template = models.CustomTemplate.objects.get(company_id=stage.company_id,
                                                                        template=stage.template)

                print('custom_stage_template', custom_stage_template)
                custom_template_status = models.CustomResult.objects.filter(candidate_id=candidate_obj,
                                                                company_id=stage.company_id,
                                                                custom_template__template=stage.template,
                                                                job_id=job_obj)
                if custom_template_status.exists():
                    custom_template_status = custom_template_status.first()

            if stage.status == 2 or stage.status == -1 or stage.status == 3:
                if stage.stage.name == 'JCR':
                    jcr_result = CandidateModels.JcrRatio.objects.get(company_id=stage.company_id,
                                                                    candidate_id=stage.candidate_id,
                                                                    job_id=job_obj,
                                                                    template=stage.template)
                    stage_dict['result'] = jcr_result

                if stage.stage.name == 'Prerequisites':
                    prerequisites_result = CandidateModels.PreRequisitesFill.objects.get(company_id=stage.company_id,
                                                                                        candidate_id=stage.candidate_id,
                                                                                        job_id=job_obj,
                                                                                        template=stage.template)
                    stage_dict['result'] = prerequisites_result

                if stage.stage.name == 'MCQ Test':
                    if not stage.reject_by_candidate:
                        mcq_test_result = CandidateModels.Mcq_Exam_result.objects.get(company_id=stage.company_id,
                                                                                    candidate_id=stage.candidate_id,
                                                                                    job_id=job_obj,
                                                                                    template=stage.template)
                        stage_dict['result'] = mcq_test_result
                    else:
                        stage_dict['result'] = None

                if stage.stage.name == 'Descriptive Test':
                    if not stage.reject_by_candidate:
                        descriptive_result = CandidateModels.Descriptive_Exam_result.objects.get(company_id=stage.company_id,
                                                                                                candidate_id=stage.candidate_id,
                                                                                                job_id=job_obj,
                                                                                                template=stage.template)
                        stage_dict['result'] = descriptive_result
                    else:
                        stage_dict['result'] = None

                if stage.stage.name == 'Image Test':
                    if not stage.reject_by_candidate:
                        image_result = CandidateModels.Image_Exam_result.objects.get(company_id=stage.company_id,
                                                                                    candidate_id=stage.candidate_id,
                                                                                    job_id=job_obj,
                                                                                    template=stage.template)
                        stage_dict['result'] = image_result
                    else:
                        stage_dict['result'] = None

                    
                if stage.stage.name == 'Audio Test':
                    if not stage.reject_by_candidate:
                        audio_result = CandidateModels.AudioExamAttempt.objects.get(candidate_id=stage.candidate_id,
                                                                                    company_id=stage.company_id,
                                                                                    job_id=stage.job_id,audio_question_paper__exam_template__template=stage.template)
                        stage_dict['result'] = audio_result
                    else:
                        stage_dict['result'] = None


                if stage.stage.name == 'Coding Test':
                    if not stage.reject_by_candidate:
                        exam_config = models.CodingExamConfiguration.objects.get(template_id=stage.template)
                        coding_result = CandidateModels.Coding_Exam_result.objects.get(candidate_id=stage.candidate_id,
                                                                                    company_id=stage.company_id,
                                                                                    template=stage.template,
                                                                                    job_id=stage.job_id)
                        stage_dict['result'] = coding_result
                    else:
                        stage_dict['result'] = None


                if stage.stage.name == 'Custom':
                    custom_results = models.CustomResult.objects.get(candidate_id=stage.candidate_id,company_id=stage.company_id,
                                                                                custom_template__template=stage.template,
                                                                                job_id=stage.job_id)
                    print('custom_results', custom_results.scorecard_results.all())
                    stage_dict['result'] = custom_results

            stages_data.append(stage_dict)

        collaboration_obj = models.Collaboration.objects.filter(company_id=job_obj.company_id, candidate_id=candidate_obj,
                                                                job_id=job_obj)

        candidate_job_status = None
        if models.CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
            candidate_job_status = models.CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)

        candidate_apply_details = None
        if models.AppliedCandidate.objects.filter(candidate=candidate_obj,company_id=job_obj.company_id).exists():
            candidate_apply_details = models.AppliedCandidate.objects.get(candidate_id=candidate_obj, job_id=job_obj)

        candidate_education = CandidateModels.CandidateEducation.objects.filter(candidate_id=candidate_obj)
        candidate_experience = CandidateModels.CandidateExperience.objects.filter(candidate_id=candidate_obj)
        candidate_certification =CandidateModels.CandidateCertificationAttachment.objects.filter(candidate_id=candidate_obj)
        candidate_award=CandidateModels.CandidateAward.objects.filter(candidate_id=candidate_obj)
        candidate_portfolio=CandidateModels.CandidatePortfolio.objects.filter(candidate_id=candidate_obj)
        candidate_preferences=CandidateModels.CandidateJobPreference.objects.filter(candidate_id=candidate_obj)
        if schedule_interview:
            description="Your profile has been shortlisted, please wait for further instruction."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Application Shortlisted",
                        description=description,image="/static/notifications/icon/candidate/Shortlisted.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
        # if add_stage_submit:
        # if withdraw_candidate:
        # if hire_candidate=:
        # if reenter_candidate:
        if shortlist_candidate:
            description="Application Shortlisted: Your profile has been shortlisted, please wait for further instruction."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Application Shortlisted",
                        description=description,image="/static/notifications/icon/candidate/Shortlisted.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
            if not next_stage==None:
                if next_stage.name=="JCR":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="JCR",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
                elif next_stage.name=="Prerequisites":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Prerequisites",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
                elif next_stage.name=="MCQ Test":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="MCQ",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
                elif next_stage.name=="Descriptive Test":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Descriptive",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
                elif next_stage.name=="Image Test":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Image",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
                elif next_stage.name=="Audio Test": 
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Audio",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")   
                elif next_stage.name=="Coding Test": 
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Coding",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
                elif next_stage.name=="Custom":    
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Custom",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")

        if reject_candidate:
            description="Sorry! Your profile has been rejected for the Job "+job_obj.job_title
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Applicationn Rejected:",
                        description=description,image="/static/notifications/icon/candidate/Application_Rejected.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
        if onhold_candidate:
            description="Application Shortlisted: Your profile has been shortlisted, please wait for further instruction."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Candidate submission",
                        description=description,image="/static/notifications/icon/candidate/Shortlisted.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
        if add_stage_submit:
            description="New stage has been added to your profile for the job "+job_obj.job_title+". Please visit to appear for interview round."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="New stage",
                        description=description,image="/static/notifications/icon/candidate/New stage.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/company")
        context['SalaryView']=SalaryView
        context['job_obj']= job_obj
        context['candidate_obj']= candidate_obj
        context['id_resume']=id_resume
        context['candidate_detail']= candidate_detail
        context['interview_schedule_data']= interview_schedule_data
        context['job_offer_data']= job_offer_data
        context['internal_users']= internal_users
        context['all_assign_users']=all_assign_users
        context['stages_status']= stages_status
        context['stages_data']= stages_data
        context['collaboration_obj']= collaboration_obj
        context['candidate_apply_details']=candidate_apply_details
        context['candidate_job_status']=candidate_job_status
        context['job_workflow_obj']=job_workflow_obj
        context['custom_stage_template']=custom_stage_template
        context['custom_template_status']=custom_template_status
        context['candidate_education']=candidate_education
        context['candidate_experience']=candidate_experience
        context['candidate_certification']=candidate_certification
        context['candidate_award']=candidate_award
        context['candidate_portfolio']=candidate_portfolio
        context['candidate_preferences']=candidate_preferences
        context['chatObject']= chat
        context['groupmessage']=groupmessage
        context['chat_id_json']= uniquecode
        return render(request, "company/ATS/company-portal-candidate-tablist.html",context )
    else:
        return redirect('company:add_edit_profile')

def add_internal_candidate_basic_detail(request,int_cand_detail_id=None):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['source']= CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['Add'] = False
        context['permission'] = check_permission(request)
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http"
        edit_internal_candidate=''
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
        if context['Add']:
            if int_cand_detail_id:
                edit_internal_candidate = models.InternalCandidateBasicDetails.objects.get(id=int(int_cand_detail_id))
                print(edit_internal_candidate)
                context['edit_internal_candidate'] = edit_internal_candidate
            if request.method == 'POST':
                fname = request.POST.get('f-name')
                lname = request.POST.get('l-name')
                email = request.POST.get('email')
                gender = request.POST.get('gender')
                if request.FILES.get('resume'):
                    resume =request.FILES.get('resume')
                else:
                    resume=context['edit_internal_candidate'].resume
                contact = request.POST.get('contact_num')
                # source=CandidateModels.Source.objects.get(id=int(request.POST.get('source')))
                designation = request.POST.get('designation-input')
                notice = CandidateModels.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
                ctc = request.POST.get('ctc-input')
                expectedctc = request.POST.get('expected-ctc')
                current_city = CandidateModels.City.objects.get(id=request.POST.get('candidate_current_city'))
                total_exper = request.POST.get('professional-experience-year') +'.'+ request.POST.get(
                    'professional-experience-month')

                # add profile pic
                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES.get('profile_pic')
                else:
                    if 'edit_internal_candidate' in context:
                        profile_pic = context['edit_internal_candidate'].profile_pic
                    else:
                        profile_pic = None

                edit_internal_candidate,created=models.InternalCandidateBasicDetails.objects.update_or_create(email=email,company_id=models.Company.objects.get(user_id=request.user.id),defaults={
                    'user_id':User.objects.get(id=request.user.id),
                    'update_by':User.objects.get(id=request.user.id),
                    'update_at':datetime.datetime.now(),
                    'first_name' : fname,
                    'last_name' : lname,
                    'gender' : gender,
                    'resume' : resume,
                    'profile_pic': profile_pic,
                    'contact' : contact,
                    'designation': designation,
                    'notice' : notice,
                    'ctc' : ctc,
                    # 'source':source,
                    'expectedctc' : expectedctc,
                    'total_exper' : total_exper,
                    'current_city':current_city,
                    'update_at':datetime.datetime.now()
                })
                add_skill=models.InternalCandidateBasicDetails.objects.get(email=email,company_id=models.Company.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_skill.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_skill.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_skill.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,company=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                        add_skill.tags.add(tag_cre)
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                        add_skill.skills.add(main_skill_obj)
                    else:
                        skill_cre=CandidateModels.Skill.objects.create(name=i)
                        add_skill.skills.add(skill_cre)
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = CandidateModels.City.objects.get(id=i)
                        add_skill.prefered_city.add(main_city_obj)

                for i in request.POST.getlist('candidate_category'):
                    if i.isnumeric():
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_skill.categories.add(main_categ_obj)
                if User.objects.filter(email=email.lower()).exists():
                    add_skill.candidate_id=User.objects.get(email=email.lower())
                add_skill.save()
                if int_cand_detail_id:
                    
                    description = edit_internal_candidate.company_id.company_id.company_name + "Edit Candidate Detail"
                    if edit_internal_candidate.user_id.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=edit_internal_candidate.user_id.id),verb="Edit Candidate Detail",
                                                                                    description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                    target_url=header+"://"+current_site.domain+"/company/view_candidate/" + str(
                                                                                        int_cand_detail_id))
                    get_activejob=models.AssociateCandidateInternal.objects.filter(internal_candidate_id=int_cand_detail_id,job_id__close_job_targetdate=False,job_id__close_job=False).values_list('user_id')
                    for user_job in get_activejob:
                        if user_job != request.user.id:
                            description = edit_internal_candidate.company_id.company_id.company_name + "Edit Candidate Detail"
                            notify.send(request.user, recipient=User.objects.get(id=edit_internal_candidate.user_id.id),verb="Edit Candidate Detail",
                                                                                    description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                    target_url=header+"://"+current_site.domain+"/company/view_candidate/" + str(
                                                                                        int_cand_detail_id))
                else:
                    all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
                    for i in all_internal_users:
                        description = "New candidate has been added to your Database by "+fname+" "+lname
                        if i.employee_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="New Candidate Add",
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/view_candidate/"+str(edit_internal_candidate.id))
                return redirect('company:all_candidates')
            return render(request,'company/ATS/add_candidate_basic_form.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')
from django.forms.models import model_to_dict
def check_candidate_email_is_valid(request):
    email = request.POST.get("email")
    data={}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        user_obj = models.InternalCandidateBasicDetails.objects.filter(email=email).exists()
        if user_obj:
            user_data=models.InternalCandidateBasicDetails.objects.get(email=email,company_id = models.Company.objects.get(user_id=User.objects.get(id=request.user.id)))
            # data = serializers.serialize('json', models.InternalCandidateBasicDetail.objects.get(email=email,agency_id = models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))))
            if user_data.candidate_id:
                data['candidate_id']=user_data.candidate_id.id
            else:
                data['candidate_id']=None
            if user_data.first_name:
                data['first_name']=user_data.first_name 
            else:
                data['first_name']=None
            if user_data.last_name:
                data['last_name']=user_data.last_name 
            else:
                data['last_name']=None
            if user_data.gender:
                data['gender']=user_data.gender
            else:
                data['gender']=None
            if user_data.resume:
                data['resume']=user_data.resume.url
            else:
                data['resume']=None
            if user_data.contact:
                data['contact']=user_data.contact
            else:
                data['contact']=None
            if user_data.designation:    
                data['designation']=user_data.designation
            else:
                data['designation']=None
            if user_data.prefered_city.all():
                prefered_city={}
                for i in user_data.prefered_city.all():
                    prefered_city[i.id]=i.city_name
                data['prefered_city']=prefered_city
            else:
                data['prefered_city']=None
            if user_data.current_city:
                data['current_city']={'id':user_data.current_city.id,'name':user_data.current_city.city_name}
            else:
                data['current_city']=None
            if user_data.notice:   
                data['notice']={'id':user_data.notice.id,'name':user_data.notice.notice_period}
            else:
                data['notice']=None
            if user_data.skills.all():    
                skills={}
                for i in user_data.skills.all():
                    skills[i.id]=i.name
                data['skills']=skills
            else:
                data['skills']=None
            if user_data.source:
                data['source']={'id':user_data.source.id,'name':user_data.source.name}
            else:
                data['source']=None
            if user_data.categories.all():    
                categories={}
                for i in user_data.categories.all():
                    categories[i.id]=i.category_name
                data['categories']=categories
            else:
                data['categories']=None
            if user_data.tags.all():     
                tags={}
                for i in user_data.tags.all():
                    tags[i.id]=i.name
                data['tags']=tags
            else:
                data['tags']=None
            if user_data.ctc:    
                data['ctc']=user_data.ctc 
            else:
                data['ctc']=None
            if user_data.expectedctc:    
                data['expectedctc']=user_data.expectedctc
            else:
                data['expectedctc']=None
            if user_data.total_exper:    
                data['total_exper']=user_data.total_exper 
            else:
                data['total_exper']=None
            data['status']=True 
            return JsonResponse({'data':data}, safe=False)
        else:
            data={'status':False}
            return JsonResponse({'data':data}, safe=False)
    else:
        data={'status':'Invalid'}
        return JsonResponse({'data':data}, safe=False)


def generate_referral_code():
    num = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(12)])
    return num


def associate_job(request,candidate_id):
    alert={}
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        internal_candidate = models.InternalCandidateBasicDetails.objects.get(id=candidate_id)
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['categories'] = models.CandidateCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['edit_internal_candidate']=internal_candidate
        if request.method=="POST":
            associate_jon_list=request.POST.get('associate-selector')
            job_id_get=associate_jon_list.split('-')
            if job_id_get[0]=='company':
                context['jobid']=models.JobCreation.objects.get(id=job_id_get[1])
            context['jobtype']=job_id_get[0]
            return render(request,'company/ATS/applied_candidate_detail_form.html',context)
        else:
            return HttpResponseRedirect('/company/view_candidate/'+str(candidate_id))
    else:
        return redirect('company:add_edit_profile')
#interview


def interview_template(request,template_id=None):
    context ={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if template_id:
            template = get_object_or_404(models.Template_creation,id=template_id)
            stage = template.stage
            category=template.category
            context['template_id'] = template_id
            exam_template = models.InterviewTemplate.objects.filter(template=template)
            if exam_template.exists():
                context['exam_template']= exam_template[0]
        else:
            stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        if request.method == 'POST':
            interview_template_obj,update = models.InterviewTemplate.objects.update_or_create(
                company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),
                stage=stage,
                category=category,
                template=template,
                defaults={
                'interview_name':request.POST.get('interview_name'),
                'interview_type':request.POST.get('interview_type')})
            ratings = request.POST.getlist('rate-title')
            for title in ratings:
                models.InterviewScorecard.objects.create(title=title, interview_template=interview_template_obj)
            interview_template_obj.template.status = True
            interview_template_obj.template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                            user_id=request.user)).values_list('employee_id', flat=True)
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            link=header+"://"+current_site.domain+"/company/interview_template_view/"+str(interview_template_obj.id)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Interview Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace"
            all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            for i in all_internal_users:
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="Create Interview Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/interview_template_view/"+str(interview_template_obj.id))

            return redirect('company:template_listing')
        context['template']=template
        return render(request, "company/ATS/interview_template.html",context)
    else:
        return redirect('company:add_edit_profile')

def interview_template_edit(request,interview_temp_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        interview_template = models.InterviewTemplate.objects.get(id=interview_temp_id)  
        score_cards = models.InterviewScorecard.objects.filter(interview_template=interview_template)
        context['interview_template'] = interview_template
        context['score_cards'] = score_cards

        if request.method == 'POST':                    
            interview_template.interview_name=request.POST.get('interview_name')
            interview_template.interview_type=request.POST.get('interview_type')
            interview_template.save()
            ratings = request.POST.getlist('rate-title')
            score_cards.delete()
            for title in ratings:
                models.InterviewScorecard.objects.create(title=title, interview_template=interview_template)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            description = models.Company.objects.get(user_id=request.user.id).company_id.company_name + "Edit Interview Template"
            if interview_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=context['get_template'].user_id.id),verb="Edit Interview Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/company/interview_template_view/"+str(interview_template.id))
            return redirect('company:template_listing')
        return render(request, "company/ATS/interview_template_edit.html",context)
    else:
        return redirect('company:add_edit_profile')

def interview_template_view(request,interview_temp_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        interview_template = models.InterviewTemplate.objects.get(id=interview_temp_id)
        score_cards = models.InterviewScorecard.objects.filter(interview_template=interview_template)
        context['interview_template'] = interview_template
        context['score_cards'] = score_cards

        if request.method == 'POST':
            return redirect('company:template_listing')
        return render(request, "company/ATS/interview_template_view.html",context)
    else:
        return redirect('company:add_edit_profile')
#all question update

def get_mcq_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        que_get=models.mcq_Question.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=que_id)
        print(que_get)
        if que_get:
            data['levelid'] = que_get.question_level.id
            data['question'] =que_get.question_description
            data['option1'] =que_get.option_a
            data['option2'] =que_get.option_b
            data['option3'] =que_get.option_c
            data['option4'] =que_get.option_d
            data['correctans'] = que_get.correct_option
            data['status'] = True
        else:
            data['question'] = ''
            data['status'] = False
        return HttpResponse(json.dumps(data))
def update_mcq_question(request):
    if request.method=='POST':
        queid=request.POST.get('queid')
        level=request.POST.get('question_level')
        question = request.POST.get('question')
        print(request.POST.get('question'))
        print(question)
        option1=request.POST.get('option_1')
        option2=request.POST.get('option_2')
        option3=request.POST.get('option_3')
        option4=request.POST.get('option_4')
        answer=request.POST.get('correct_answer')
        update_que=models.mcq_Question.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=queid)
        update_que.question_description =question
        update_que.question_level =CandidateModels.QuestionDifficultyLevel.objects.get(id=int(level))
        update_que.correct_option =answer
        update_que.option_a =option1
        update_que.option_b =option2
        update_que.option_c =option3
        update_que.option_d =option4
        update_que.save()
        return redirect('company:preview_mcq',id=update_que.mcq_subject.id)

def get_descriptive_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        que_get=models.Descriptive.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=que_id)
        print(que_get)
        if que_get:
            data['question'] =que_get.paragraph_description
            data['status'] = True
        else:
            data['subject'] = ''
            data['status'] = False
        return HttpResponse(json.dumps(data))
def update_descriptive_question(request):
    if request.method=='POST':
        queid=request.POST.get('queid')
        question=request.POST.get('description_textarea_update')
        update_que=models.Descriptive.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=queid)
        update_que.paragraph_description =question
        update_que.save()
        return redirect('company:descriptive_view',id=update_que.subject.id)

def get_coding_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        que_get=models.CodingQuestion.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=que_id)
        print(que_get)
        if que_get:
            data['question'] =que_get.coding_que_description
            data['title'] =que_get.coding_que_title
            data['que_type'] =que_get.question_type
            data['status'] = True
        else:
            data['question'] = ''
            data['status'] = False
        return HttpResponse(json.dumps(data))

def update_coding_question(request):
    if request.method=='POST':
        queid=request.POST.get('queid')
        question = request.POST.get('coding-que-description')
        que_type = request.POST.get('basic_type')
        title = request.POST.get('title')
        update_que=models.CodingQuestion.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=queid)
        update_que.question_type =que_type
        update_que.coding_que_title =title
        update_que.coding_que_description =question
        update_que.save()
        return redirect('company:coding_question_view',id=update_que.category_id.id)

def get_audio_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        get_audiopaper=models.AudioExamQuestionUnit.objects.filter(question=models.Audio.objects.get(id=que_id)).values_list('template')
        get_workflow=models.WorkflowStages.objects.filter(template__in=get_audiopaper).values_list('workflow_id')
        get_job=models.JobWorkflow.objects.filter(workflow_id__in=get_workflow).values_list('job_id')
        job_status=models.JobCreation.objects.filter(id__in=get_job)
        print('template',get_audiopaper)
        print('get_workflow',get_workflow)
        print('get_job',get_job)
        active=''
        for jobstatus in job_status:
            print(jobstatus.status.name)
            if jobstatus.status.name=='In Progress':
                active=True
        print(active)
        if not active:
            que_get=models.Audio.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=que_id)
            if que_get:
                data['question'] =que_get.paragraph_description
                data['status'] = True
            else:
                data['question'] = ''
                data['status'] = False
        else:
            data['question'] = ''
            data['status'] = 'replica'
        return HttpResponse(json.dumps(data))
    
    
def update_audio_question(request):
    if request.method=='POST':
        queid=request.POST.get('queid')
        question = request.POST.get('description_textarea')
        update_que=models.Audio.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=queid)
        update_que.paragraph_description =question
        update_que.save()
        return redirect('company:audio_view',id=update_que.subject.id)
    

def descriptive_assessment(request):
    if request.method == 'POST':
        if 'assess' in request.POST:
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
            questions_obj = CandidateModels.Descriptive_Exam.objects.filter(candidate_id=stage_obj.candidate_id,
                                                            company_id=stage_obj.company_id,
                                                            job_id=stage_obj.job_id,template=stage_obj.template).order_by('id')
            print('questions_obj', questions_obj)
            return render(request, "company/ATS/descriptive_assesment.html", {'questions_obj': questions_obj,'stage_id':stage_obj.id})
        if 'submit_marks' in request.POST:
            print('\n\n\nstggg', request.POST.get('stage'))
            print('\n\n\nmarksssssss', request.POST.getlist('marks_given'))
            marks_given = request.POST.getlist('marks_given')
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage'))
            exam_name = models.DescriptiveExamTemplate.objects.get(company_id=stage_obj.company_id,
                                                             template=stage_obj.template)
            questions_obj = CandidateModels.Descriptive_Exam.objects.filter(candidate_id=stage_obj.candidate_id,
                                                                            company_id=stage_obj.company_id,
                                                                            job_id=stage_obj.job_id,
                                                                            template=stage_obj.template).order_by('id')
            count = 0
            for question in questions_obj:
                question.marks = marks_given[count]
                question.save()
                count += 1
            obain_time = 0
            total_que = 0
            ans_que = 0
            no_ans_que = 0
            for i in questions_obj:

                if i.status == 1:

                    ans_que += 1
                elif i.status == -1:

                    ans_que += 1
                elif i.status == 0:

                    no_ans_que += 1
                total_que += 1
            a = """<div style="background: #fff;">
                    <div style="padding: 10px 15px;">

                        <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                            <thead>
                              <tr style="border-bottom: 1px solid #324670;">
                                <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                                <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+exam_name.exam_name+"""</th>
                                <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr>

                                <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>""" + str(
                ans_que) + """</span></td>
                                <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>""" + str(
                no_ans_que) + """</span></td>
                                <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min""" + str(
                obain_time) + """</span></td>
                              </tr>
                            </tbody>
                        </table>
                        <div>
                """
            count=1
            for i in questions_obj:

                a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                                <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                                    <div style="width: 100%;display: flex;color: #031b4e;">
                                        <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-"""+str(count)+"""</div>
                                        <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.question.paragraph_description + """</div>
                                    </div>
                                    <div style="width: 100%;display: flex;color: #031b4e;">														
                                        <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                                        """
                if i.status == 1:
                    a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">""" + i.ans + """</div>"""
                elif i.status == -1:
                    a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">Skip</div>"""
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
                a += """</div></div>"""
                count+=1
            a += """
                    </div>									
                    </div>"""
            path = settings.MEDIA_ROOT + "{}/{}/Stages/Descriptive/".format(stage_obj.candidate_id.id, stage_obj.job_id.id)
            getresult, created = CandidateModels.Descriptive_Exam_result.objects.update_or_create(candidate_id=stage_obj.candidate_id,
                                                                                         company_id=stage_obj.company_id,
                                                                                         job_id=stage_obj.job_id,
                                                                                         template=stage_obj.template,
                                                                                         defaults={
                                                                                             'total_question': total_que,
                                                                                             'answered': ans_que,
                                                                                             'not_answered': no_ans_que,
                                                                                             'obain_time': 10,
                                                                                             'mcq_pdf': path + stage_obj.candidate_id.first_name + "Descriptive.pdf"})

            pdfkit.from_string(a, output_path=path + stage_obj.candidate_id.first_name + "Descriptive.pdf")
            stage_obj.assessment_done = True
            stage_obj.save()
            models.Tracker.objects.update_or_create(job_id=stage_obj.job_id,candidate_id=stage_obj.candidate_id,company_id=stage_obj.company_id,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
            return redirect('company:company_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,job_id=stage_obj.job_id.id)
    else:
        return HttpResponse(False)


def audio_video_assessment(request):
    if request.method == 'POST':
        if 'assess' in request.POST:
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
            audio_attempt_obj = CandidateModels.AudioExamAttempt.objects.get(candidate_id=stage_obj.candidate_id,
                                                            company_id=stage_obj.company_id,
                                                            job_id=stage_obj.job_id,
                                                            audio_question_paper__exam_template__template=stage_obj.template)
            all_questions_obj = audio_attempt_obj.audio_question_attempts.all().order_by('id')
            return render(request, "company/ATS/audio_video_assessment.html",
                          {'questions_obj': all_questions_obj,'stage_id':stage_obj.id,
                           'is_video':audio_attempt_obj.audio_question_paper.exam_template.is_video})
        if 'submit_marks' in request.POST:

            marks_given = request.POST.getlist('marks_given')
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage'))
            exam_name = models.AudioExamTemplate.objects.get(company_id=stage_obj.company_id,
                                                             template=stage_obj.template)
            audio_attempt_obj = CandidateModels.AudioExamAttempt.objects.get(candidate_id=stage_obj.candidate_id,
                                                                            company_id=stage_obj.company_id,
                                                                            job_id=stage_obj.job_id,
                                                                            audio_question_paper__exam_template__template=stage_obj.template)
            
            all_questions_obj = audio_attempt_obj.audio_question_attempts.all().order_by('id')
            count = 0
            for question in all_questions_obj:
                question.marks = marks_given[count]
                question.save()
                count += 1

            stage_obj.assessment_done = True
            stage_obj.save()
            obain_time =10
            total_que = 0
            ans_que = 0
            no_ans_que = 0
            for i in all_questions_obj:
                if i.answer != '':
                    ans_que += 1
                else:
                    no_ans_que += 1
                total_que += 1
            a = """<div style="background: #fff;">
                                <div style="padding: 10px 15px;">

                                    <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                                        <thead>
                                          <tr style="border-bottom: 1px solid #324670;">
                                            <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                                            <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+exam_name.exam_name+"""</th>
                                            <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          <tr>

                                            <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Answered <br><span>""" + str(
                ans_que) + """</span></td>
                                            <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>""" + str(
                no_ans_que) + """</span></td>
                                            <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min""" + str(
                obain_time) + """</span></td>
                                          </tr>
                                        </tbody>
                                    </table>
                                    <div>
                            """
            count = 1
            for i in all_questions_obj:

                a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                                            <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                                                <div style="width: 100%;display: flex;color: #031b4e;">
                                                    <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-""" + str(
                    count) + """</div>
                                                    <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + i.audio_question.question.paragraph_description + """</div>
                                                </div>
                                                <div style="width: 100%;display: flex;color: #031b4e;">														
                                                    <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                                                    """
                if i.answer != '':
                    a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">Answer</div>"""
                else:
                    a += """<div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #ff5353;">No Answer</div>"""

                a += """</div>
                                            </div>
                            <div style="float: left;width: 7%;">"""
                if i.marks != '':
                    a += """<div style="text-align: center;color: #51bb24;">+""" + str(i.marks) + """</div>"""
                else:
                    a += """<div style="text-align: center;color: #ff5353;">-""" + str(0) + """</div>"""

                a += """</div></div>"""
                count += 1
            a += """
                                </div>									
                                </div>"""
            path = settings.MEDIA_ROOT + "{}/{}/Stages/Descriptive/".format(stage_obj.candidate_id.id,
                                                                            stage_obj.job_id.id)
            getresult, created = CandidateModels.AudioExamAttempt.objects.update_or_create(
                candidate_id=stage_obj.candidate_id,
                company_id=stage_obj.company_id,
                job_id=stage_obj.job_id,audio_question_paper__exam_template__template=stage_obj.template,
                defaults={
                    'mcq_pdf': path + stage_obj.candidate_id.first_name + "Audio.pdf"})

            pdfkit.from_string(a, output_path=path + stage_obj.candidate_id.first_name + "Audio.pdf")
            models.Tracker.objects.update_or_create(job_id=stage_obj.job_id,candidate_id=stage_obj.candidate_id,company_id=stage_obj.company_id,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
            return redirect('company:company_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,job_id=stage_obj.job_id.id)
    else:
        return HttpResponse(False)


import requests


def coding_assessment(request,id):
    stage_id = models.CandidateJobStagesStatus.objects.get(id=id)
    exam_config = models.CodingExamConfiguration.objects.get(template_id=stage_id.template)
    print('\n\nexam_config',exam_config)
    coding_questions = models.CodingExamQuestions.objects.filter(coding_exam_config_id=exam_config).order_by('id')
    questions = []
    for que in coding_questions:
        dict = {'id': que.id, 'title': que.question_id.coding_que_title,
                'description': que.question_id.coding_que_description}
        questions.append(dict)
    print('coding_questions', questions)
    candidate = stage_id.candidate_id
    company = stage_id.company_id
    total_questions = exam_config.total_question
    assignment_type = exam_config.assignment_type
    assessment_done = stage_id.assessment_done
    print('\n\n\nassignment_type', assignment_type)
    if exam_config.technology == 'backend':
        print('\n\nin backend section ')
        context = {}
        all_files = CandidateModels.CodingBackEndExamFill.objects.filter(candidate_id=candidate,job_id=stage_id.job_id,
                                                                         template=stage_id.template,
                                                                         company_id=company).order_by('exam_question_id')
        language = exam_config.coding_subject_id.api_subject_id.name
        context['no_of_questions'] = int(total_questions)
        context['question_no_iterator'] = range(context['no_of_questions'])
        context['language'] = language
        context['id'] = id
        context['coding_questions'] = questions
        context['all_files'] = serializers.serialize("json", all_files)
        context['all_questions'] = all_files
        context['assignment_type'] = assignment_type
        context['assessment_done'] = assessment_done
        if assignment_type == 'rating':
            scorecards = models.CodingScoreCard.objects.filter(coding_exam_config_id=exam_config).order_by('id')
            context['scorecards'] = scorecards

        if request.method == 'POST':
            if 'rating_submit' in request.POST:
                a = """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                        <div style="background: #fff;">
                            <div style="padding: 10px 15px;">
                                <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                                    <thead>
                                      <tr style="border-bottom: 1px solid #324670;">

                                        <th colspan="1" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+exam_config.exam_name+"""</th>
                                        <th colspan="1" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      <tr>
                                        <td  colspan="2" style="padding: 12px;font-size: 12px;text-align: right;">Obtain Time <br><span>1h 20 min</span></td>
                                      </tr>
                                    </tbody>
                                </table>"""
                print('\n\n\n\n\nrating_submit')
                for score in scorecards:
                    print('\n\nscore.id', score.id)
                    rating = request.POST.get('rating'+str(score.id))
                    comment = request.POST.get('comment'+ str(score.id))
                    print('\n\n\nraaaaaaa', rating,'cccccc', comment)
                    CandidateModels.CodingScoreCardFill.objects.update_or_create(candidate_id=candidate,
                                                                                 company_id=company,
                                                                                 user_id=User.objects.get(id=request.user.id),
                                                                                 job_id=stage_id.job_id,
                                                                                 template=stage_id.template,
                                                                                 title=score.title,
                                                                                 defaults={'comment':comment,
                                                                                           'rating':rating})
                    a += """<div>
                                <div style="width: 100%;display: flex;align-items: center;">
                                    <div style="width: 100%;">
        
                                        <div style="width: 100%;color: #031b4e;padding-top: 20px;">														
        
                                            <div style="float: left;width: 100%;">Title :- """+score.title+"""</div>
                                            <div style="float: left;width: 100%;">Reating :- """
                    for i in range(1,6):
                        if i<=int(rating):
                            a+="""<span class="fa fa-star" style="color: orange;"></span>"""
                        else:
                            a+="""<span class="fa fa-star"></span>"""

                    a+="""<div style="float: left;width: 100%;">Comments :- """+comment+"""</div>
                                        </div>
                                    </div>
        
        
                                </div>
                            </div>"""

                stage_id.assessment_done = True
                stage_id.save()

                a+="""</div>									
                        </div>"""
                path = settings.MEDIA_ROOT + "{}/{}/Stages/Coding/".format(candidate.id, stage_id.job_id.id)
                getresult, created = CandidateModels.Coding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                               company_id=company,
                                                                               template=stage_id.template,
                                                                               job_id=stage_id.job_id, defaults={
                        'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                return redirect('company:company_portal_candidate_tablist', candidate.id,stage_id.job_id.id)

            if 'marking_submit' in request.POST:
                coding_result = CandidateModels.Coding_Exam_result.objects.get(candidate_id=candidate,
                                                                               company_id=company,
                                                                               template=stage_id.template,
                                                                               job_id=stage_id.job_id)
                total_obtain_marks = 0
                for question in all_files:

                    if request.POST.get('obtain_marks'+str(question.id)):
                        obtain_mark = request.POST.get('obtain_marks' + str(question.id))
                    else:
                        obtain_mark = 0
                    question.obtain_marks = obtain_mark
                    question.save()
                    total_obtain_marks += int(obtain_mark)

                coding_result.obtain_marks = total_obtain_marks
                coding_result.save()
                a = """<div style="background: #fff;">
                            <div style="padding: 10px 15px;">
    
                                <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                                    <thead>
                                      <tr style="border-bottom: 1px solid #324670;">
                                        <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                                        <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+exam_config.exam_name+"""</th>
                                        <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      <tr>
    
                                        <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Obtain Marks <br><span>""" + str(coding_result.obtain_marks) + """</span></td>
                                        <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>no ans</span></td>
                                        <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min</span></td>
                                      </tr>
                                    </tbody>
                                </table>
                                <div>
                        """
                count=1
                for question in all_files:
                    a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                                                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                                                        <div style="width: 100%;display: flex;color: #031b4e;">
                                                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-""" + str(count) + """</div>
                                                            <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + question.exam_question_id.question_id.coding_que_title + """</div>
                                                        </div>
                                                        <div style="width: 100%;display: flex;color: #031b4e;">														
                                                            <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                                                         <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">""" + question.exam_question_id.question_id.coding_que_description + """</div>"""

                    a += """</div>
                            </div>
                        <div style="float: left;width: 7%;">"""
                    if question.obtain_marks != '':
                        a += """<div style="text-align: center;color: #51bb24;">+""" + str(question.obtain_marks) + """</div>"""

                    a += """</div></div>"""
                    count += 1
                a += """
                                        </div>									
                                        </div>"""
                stage_id.assessment_done = True
                stage_id.save()
                path = settings.MEDIA_ROOT + "{}/{}/Stages/Coding/".format(candidate.id, stage_id.job_id.id)
                getresult, created = CandidateModels.Coding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 company_id=company,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                models.Tracker.objects.update_or_create(job_id=stage_id.job_id,candidate_id=candidate,company_id=company,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
                return redirect('company:company_portal_candidate_tablist', candidate.id, stage_id.job_id.id)
            else:
                data = json.loads(request.body.decode('UTF-8'))
                url = 'https://glot.io/api/run/' + language + '/latest'
                payload = json.dumps(data)
                print("payload", payload)
                headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8',
                           'Authorization': 'Token 6f18027a-2ea7-40cf-8b7b-4b91b49fda0a',
                           'contentType ': 'application/json'}
                r = requests.post(url, data=payload, headers=headers)
                return HttpResponse(r)
        return render(request, "company/ATS/back_end_view_code.html", context)
    else:
        print('\n\nin front section ')
        context={}
        context['no_of_questions'] = int(total_questions)
        context['coding_questions'] = questions
        context['question_list'] = range(context['no_of_questions'])
        context['assignment_type'] = assignment_type
        context['assessment_done'] = assessment_done
        if assignment_type == 'rating':
            scorecards = models.CodingScoreCard.objects.filter(coding_exam_config_id=exam_config).order_by('id')
            context['scorecards'] = scorecards
        all_front_end_codes = CandidateModels.CodingFrontEndExamFill.objects.filter(candidate_id=candidate,
                                                                                    job_id=stage_id.job_id,
                                                                                    template=stage_id.template,
                                                                                    company_id=company).order_by('exam_question_id')
        context['all_front_end_codes'] = serializers.serialize("json", all_front_end_codes)
        context['all_questions'] = all_front_end_codes
        if request.method == 'POST':
            if 'rating_submit' in request.POST:
                a = """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                        <div style="background: #fff;">
                            <div style="padding: 10px 15px;">
                                <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                                    <thead>
                                      <tr style="border-bottom: 1px solid #324670;">

                                        <th colspan="1" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+exam_config.exam_name+"""</th>
                                        <th colspan="1" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      <tr>
                                        <td  colspan="2" style="padding: 12px;font-size: 12px;text-align: right;">Obtain Time <br><span>1h 20 min</span></td>
                                      </tr>
                                    </tbody>
                                </table>"""
                print('\n\n\n\n\nrating_submit')
                for score in scorecards:
                    print('\n\nscore.id', score.id)
                    rating = request.POST.get('rating'+str(score.id))
                    comment = request.POST.get('comment'+ str(score.id))
                    print('\n\n\nraaaaaaa', rating,'cccccc', comment)
                    CandidateModels.CodingScoreCardFill.objects.update_or_create(candidate_id=candidate,
                                                                                 company_id=company,
                                                                                 user_id=User.objects.get(id=request.user.id),
                                                                                 job_id=stage_id.job_id,
                                                                                 template=stage_id.template,
                                                                                 title=score.title,
                                                                                 defaults={'comment':comment,
                                                                                           'rating':rating})
                    a += """<div>
                                                    <div style="width: 100%;display: flex;align-items: center;">
                                                        <div style="width: 100%;">

                                                            <div style="width: 100%;color: #031b4e;padding-top: 20px;">														

                                                                <div style="float: left;width: 100%;">Title :- """ + score.title + """</div>
                                                                <div style="float: left;width: 100%;">Reating :- """
                    for i in range(1, 6):
                        if i <= int(rating):
                            a += """<span class="fa fa-star" style="color: orange;"></span>"""
                        else:
                            a += """<span class="fa fa-star"></span>"""

                    a += """<div style="float: left;width: 100%;">Comments :- """ + comment + """</div>
                                                            </div>
                                                        </div>


                                                    </div>
                                                </div>"""
                stage_id.assessment_done = True
                stage_id.save()
                a += """</div>									
                                        </div>"""
                path = settings.MEDIA_ROOT + "{}/{}/Stages/Coding/".format(candidate.id, stage_id.job_id.id)
                getresult, created = CandidateModels.Coding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 company_id=company,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                return redirect('company:company_portal_candidate_tablist', candidate.id,stage_id.job_id.id)

            if 'marking_submit' in request.POST:
                print('\n\nin marking_submit section ')
                coding_result = CandidateModels.Coding_Exam_result.objects.get(candidate_id=candidate,
                                                                               company_id=company,
                                                                               template=stage_id.template,
                                                                               job_id=stage_id.job_id)
                total_obtain_marks = 0
                for question in all_front_end_codes:

                    if request.POST.get('obtain_marks'+str(question.id)):
                        obtain_mark = request.POST.get('obtain_marks' + str(question.id))
                    else:
                        obtain_mark = 0
                    question.obtain_marks = obtain_mark
                    question.save()
                    total_obtain_marks += int(obtain_mark)

                coding_result.obtain_marks = total_obtain_marks
                coding_result.save()
                a = """<div style="background: #fff;">
                        <div style="padding: 10px 15px;">

                            <table width="100" style="width: 100%;background-color: #031b4e;color: #fff;">
                                <thead>
                                  <tr style="border-bottom: 1px solid #324670;">
                                    <th colspan="2" style="font-size: 12px;padding: 12px;">Total Marks :- 100</th>
                                    <th colspan="2" style="font-size: 14px;text-align: center;padding: 12px;">Exam Name :- """+exam_config.exam_name+"""</th>
                                    <th colspan="2" style="font-size: 12px;text-align: right;padding: 12px;">Total Time :- 1h 30min</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  <tr>

                                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;"> Obtain Marks <br><span>""" + str(coding_result.obtain_marks) + """</span></td>
                                    <td style="padding: 12px;border-right: 1px solid #324670;font-size: 12px;text-align: center;">Not Answered <br><span>no ans</span></td>
                                    <td style="padding: 12px;font-size: 12px;text-align: center;">Obtain Time <br><span>1h 20 min</span></td>
                                  </tr>
                                </tbody>
                            </table>
                            <div>
                    """
                count = 1
                for question in all_front_end_codes:
                    a += """<div style="width: 100%;display: flex;align-items: center;border: 2px solid #eef4fa;border-top: 0;">
                                    <div style="width: 93%;float: left;border-right: 2px solid #eef4fa;">
                                        <div style="width: 100%;display: flex;color: #031b4e;">
                                            <div style="float: left;width: 10%;padding: 12px 12px 0;text-align: center;">Q-""" + str(count) + """</div>
                                    <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px 12px 0;">""" + question.exam_question_id.question_id.coding_que_title + """</div>
                                </div>
                                <div style="width: 100%;display: flex;color: #031b4e;">														
                                    <div style="float: left;width: 10%;padding: 12px;text-align: center;">Ans</div>
                                 <div style="float: left;width: 90%;border-left: 2px solid #eef4fa; padding: 12px;color: #51bb24;">""" + question.exam_question_id.question_id.coding_que_description + """</div>"""

                    a += """</div>
                            </div>
                        <div style="float: left;width: 7%;">"""
                    if question.obtain_marks != '':
                        a += """<div style="text-align: center;color: #51bb24;">+""" + str(question.obtain_marks) + """</div>"""

                    a += """</div></div>"""
                    count += 1
                a += """
                        </div>									
                        </div>"""
                stage_id.assessment_done = True
                stage_id.save()
                path = settings.MEDIA_ROOT + "{}/{}/Stages/Coding/".format(candidate.id, stage_id.job_id.id)
                getresult, created = CandidateModels.Coding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 company_id=company,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                models.Tracker.objects.update_or_create(job_id=stage_id.job_id,candidate_id=candidate,company_id=company,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
                return redirect('company:company_portal_candidate_tablist', candidate.id, stage_id.job_id.id)
        return render(request, "company/ATS/front_end_code_view.html", context)


def candidate_negotiate_offer(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):

        if request.method == 'POST':
            print('aaaaaa', request.POST.get('designation'))

            old_offer = models.OfferNegotiation.objects.get(id=request.POST.get('negotiation_id'))
            stage_status = models.CandidateJobStagesStatus.objects.get(id=id)
            job_offer_obj = models.JobOffer.objects.get(job_stages_id=stage_status)
            job_offer_obj.candidate_name = request.POST.get('candidate_name')
            job_offer_obj.bond = request.POST.get('bond')
            if request.POST.get('offer_letter_checked') == 'offer_letter_checked':
                job_offer_obj.offer_letter = request.FILES.get('offer_letter')
            job_offer_obj.NDA = request.POST.get('nda')

            if 'resend_offer' in request.POST:
                job_offer_obj.rejected_by_candidate = False
                stage_status.status = 1
                stage_status.save()
            job_offer_obj.save()
            negotiation_obj = models.OfferNegotiation.objects.create(designation=request.POST.get('designation'),
                                                                    annual_ctc=request.POST.get('negotiate_salary'),
                                                                    notice_period=request.POST.get('notice_period'),
                                                                    joining_date=request.POST.get('join_date'),
                                                                    other_details=request.POST.get('other_details'),
                                                                    from_company=True)
            job_offer_obj.negotiations.add(negotiation_obj)
            old_offer.action_performed = True
            old_offer.save()

        stage_status = models.CandidateJobStagesStatus.objects.get(id=id)
        job_offer_obj = models.JobOffer.objects.get(job_stages_id=stage_status)
        context['job_offer_obj']=job_offer_obj
        context['negotiations']=job_offer_obj.negotiations.all().order_by('-id')
        return render(request, 'company/ATS/candidate_negotiate_offer.html',context )
    else:
        return redirect('company:add_edit_profile')

def send_offer(request,id):
    if request.method == 'POST':
        if models.CandidateJobStagesStatus.objects.filter(id=id).exists():
            print('request.POST)',request.POST.get('offer-letter'))
            print('request.files)',request.FILES.get('offer-letter'))
            user_obj = User.objects.get(id=request.user.id)
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=id)
            job_offer_obj = models.JobOffer.objects.update_or_create(company_id=stage_obj.company_id,
                                                            candidate_id=stage_obj.candidate_id,job_id=stage_obj.job_id,
                                                            defaults={
                                                                'user_id':user_obj,
                                                                'job_stages_id': stage_obj,
                                                                'candidate_name':request.POST.get('candidate-name'),
                                                                'bond':request.POST.get('bond'),
                                                                'NDA':request.POST.get('nda'),
                                                                'offer_letter':request.FILES.get('offer-letter')
                                                            })
                                                           
            negotiation_obj = models.OfferNegotiation.objects.create(designation=request.POST.get('designation'),
                                                                     annual_ctc=request.POST.get('annual-ctc'),
                                                                     notice_period=request.POST.get('notice-period'),
                                                                     joining_date=request.POST.get('joining-date'),
                                                                     other_details=request.POST.get('offer-other-details'),
                                                                     from_company=True)
            job_offer_obj.negotiations.add(negotiation_obj)
            stage_obj.assessment_done = True
            stage_obj.save()
            models.Tracker.objects.update_or_create(job_id=job_offer_obj.job_id,candidate_id=job_offer_obj.candidate_id,company_id=job_offer_obj.company_id,defaults={
                                                                'action_required':'Negotiation By Company/Candidate','update_at':datetime.datetime.now()})
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http" 
            notify.send(request.user, recipient=User.objects.get(id=job_offer_obj.candidate_id.id), verb="Hire",
                            description="Congratulation! You have been Hired for Job "+job_offer_obj.job_id.job_title+". Please accept the offer Letter.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_offer_obj.job_id)+"/company")
            return redirect('company:company_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,
                            job_id=stage_obj.job_id.id)
        else:
            return HttpResponse('False')
    else:
        return HttpResponse(False)


def role_list(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Role':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['Add'] or context['Edit'] or context['Delete']:
            context['role']=models.Role.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            return render(request, "company/ATS/role_list.html",context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')

def role_permission(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        check_permission(request)

        context['role_model']=CandidateModels.PermissionsModel.objects.filter(is_company=True)
        context['role_data']=CandidateModels.Permissions.objects.filter(is_company=True)
        if request.method=='POST':
            role_name=request.POST.get('role-name')
            role_description=request.POST.get('role-description')
            role_create=models.Role.objects.create(name=role_name,description=role_description,status=True,company_id=models.Company.objects.get(user_id=request.user.id),user_id=request.user)
            permissions=models.RolePermissions.objects.create(role=role_create,company_id=models.Company.objects.get(user_id=request.user.id),user_id=request.user)
            for per_id in request.POST.getlist('permissionname'):
                permissions.permission.add(CandidateModels.Permissions.objects.get(id=per_id))
            role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                name="SuperAdmin")
            get_admin = models.Employee.objects.filter(role=role_id_get, company_id=models.Company.objects.get(
                user_id=request.user)).values_list('employee_id', flat=True)
            for i in get_admin:
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"  
                description = request.user.first_name + "Create Role"
                if i != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i), verb="Create Role",
                                description=description,
                                target_url=header+"://"+current_site.domain+"/company/role_list/")
            return redirect('company:role_list')
        return render(request, "company/ATS/role_permission.html",context)
    else:
        return redirect('company:add_edit_profile')


def role_permission_update(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        check_permission(request)
        context['role_model']=CandidateModels.PermissionsModel.objects.filter(is_company=True)
        role_model=CandidateModels.PermissionsModel.objects.filter(is_company=True).values_list('id')
        context['role_data']=CandidateModels.Permissions.objects.filter(permissionsmodel__in=role_model,is_company=True)
        context['agency_role'] = models.Role.objects.get(id=id)
        company_permission = models.RolePermissions.objects.get(role=context['agency_role'])
        company_permission = company_permission.permission.all()
        context['agency_permission']=[i.id for i in company_permission]
        if request.method=='POST':
            role_name=request.POST.get('role-name')
            role_description=request.POST.get('role-description')
            role_create,update=models.Role.objects.update_or_create(id=id,company_id=models.Company.objects.get(user_id=request.user.id),defaults={'name':role_name,'description':role_description,'user_id':request.user})
            permissions=models.RolePermissions.objects.get(role=id,company_id=models.Company.objects.get(user_id=request.user.id))
            permissions.permission.clear()
            # return HttpResponse(True)
            for per_id in request.POST.getlist('permissionname'):
                permissions.permission.add(CandidateModels.Permissions.objects.get(id=per_id))
            role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                name="SuperAdmin")
            get_admin = models.Employee.objects.filter(role=role_id_get, company_id=models.Company.objects.get(
                user_id=request.user)).values_list('employee_id', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http" 
            for i in get_admin:
                description = request.user.first_name + "Update Role"
                if i != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Role",
                                description=description,
                                target_url=header+"://"+current_site.domain+"/company/role_list/")
            return redirect('company:role_list')
        return render(request, "company/ATS/role_permission_update.html",context)
    else:
        return redirect('company:add_edit_profile')

def interview_assessment(request,id):
    stage_id = models.CandidateJobStagesStatus.objects.get(id=id)
    interview_template = models.InterviewTemplate.objects.get(company_id=stage_id.company_id,template=stage_id.template)
    scorecards = models.InterviewScorecard.objects.filter(interview_template=interview_template)
    if request.method == 'POST':
        interview_result, created = models.InterviewResult.objects.update_or_create(
            candidate_id=stage_id.candidate_id,
            company_id=stage_id.company_id,
            user_id=User.objects.get(
                id=request.user.id),
            job_id=stage_id.job_id,
            interview_template=interview_template)
        for score in scorecards:
            rating = request.POST.get('rating' + str(score.id))
            comment = request.POST.get('comment' + str(score.id))
            interview_result.scorecard_results.add(
                models.InterviewScorecardResult.objects.create(title=score.title, comment=comment, rating=rating))
        stage_id.assessment_done = True
        stage_id.save()
        return redirect('company:company_portal_candidate_tablist', candidate_id=stage_id.candidate_id.id,
                        job_id=stage_id.job_id.id)
    return render(request, "company/ATS/interview_assessment.html",{'scorecards':scorecards})


def job_close(request,jobid):
    job_obj=models.JobCreation.objects.get(id=jobid,company_id=models.Company.objects.get(user_id=request.user.id))
    job_obj.close_job=True
    job_obj.close_job_targetdate=True
    job_obj.close_job_at=datetime.datetime.now()
    job_obj.save()
    # Notification
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    to_email=[]
    job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
    description = "This Job "+job_obj.job_title+" has been closed. No more action required!"
    to_email.append(job_obj.contact_name.email)
    to_email.append(job_obj.job_owner.email)
    if job_obj.contact_name.id != request.user.id:
        
        notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                        job_obj.id))
    if job_obj.job_owner.id != request.user.id:
        notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                        job_obj.id))
    all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
    for i in all_assign_users:
        to_email.append(i.recruiter_id.email)
        if i.recruiter_type_internal:
            if i.recruiter_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/company/created_job_view/" + str(
                                                                        job_obj.id))
        if i.recruiter_type_external :
            if i.recruiter_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Close Job",
                                                                    description=description,image="/static/notifications/icon/company/Close_Job.png",
                                                                    target_url=header+"://"+current_site.domain+"/agency/job_view/" + str(
                                                                        job_obj.id))
    applied_candidates=models.AppliedCandidate.objects.filter(company_id=job_obj.company_id,job_id=job_obj)
    for applied_candidate in applied_candidates:
        to_email.append(applied_candidate.candidate.email)
    to_email=list(set(to_email))
    mail_subject = job_obj.job_title + " has been closed"
    html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"The job you are working with is been closed by "+job_obj.company_id.company_id.company_name+". No action required from your end."})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
    msg.attach_alternative(html_content, "text/html")
    # try:
    msg.send()
    getjob=Scheduler.get_jobs()
    for job in getjob:
        if job.id=='company_jobid_'+str(job_obj.id):
            Scheduler.remove_job(id='company_jobid_'+str(job_obj.id))
    return redirect('company:applied_candidates_view',id=jobid)



def unassign_recruiter(request):
    if request.method=='POST':
        getUserId = request.POST.get("getUserId")
        job_id = request.POST.get("job_id")
        getUsertype = request.POST.get("getUsertype")
        job_obj=models.JobCreation.objects.get(id=job_id)
        models.CompanyAssignJob.objects.filter(job_id=job_obj,
                                               company_id=models.Company.objects.get(user_id=request.user.id),
                                               recruiter_id=User.objects.get(id=getUserId)).delete()
        if getUsertype=='internal':
            models.AssignInternal.objects.filter(
                company_id=models.Company.objects.get(user_id=request.user.id), job_id=job_obj,
                recruiter_id=User.objects.get(id=getUserId)).delete()
        if getUsertype=='external':
            models.AssignExternal.objects.filter(
                company_id=models.Company.objects.get(user_id=request.user.id), job_id=job_obj,
                recruiter_id=AgencyModels.Agency.objects.get(user_id=getUserId)).delete()

        return HttpResponse(True)
    else:
        return HttpResponse(False)


def change_employee_status(request):
    if request.method == "POST":
        print('employee id', request.POST.get('employee_id'))
        employee_obj = models.Employee.objects.get(id=request.POST.get('employee_id'))
        employee_obj.employee_id.is_active = not employee_obj.employee_id.is_active
        employee_obj.employee_id.save()
        return HttpResponse(True)

def change_role_status(request):
    if request.method == "POST":
        role_obj = models.Role.objects.get(id=request.POST.get('role_id'))
        role_obj.status = not role_obj.status
        role_obj.save()
        return HttpResponse(True)

def change_department_obj_status(request):
    if request.method == "POST":
        department_obj = models.Department.objects.get(id=request.POST.get('department_id'))
        department_obj.status = not department_obj.status
        department_obj.save()
        return HttpResponse(True)

def start_interview(request,id):
    interview_schedule_obj = models.InterviewSchedule.objects.get(id=id)
    scorecards = models.InterviewScorecard.objects.filter(interview_template=interview_schedule_obj.interview_template)
    if request.method == 'POST':
        interview_result, created = models.InterviewResult.objects.update_or_create(
            candidate_id=interview_schedule_obj.job_stages_id.candidate_id,
            company_id=interview_schedule_obj.job_stages_id.company_id,
            user_id=User.objects.get(
                id=request.user.id),
            job_id=interview_schedule_obj.job_stages_id.job_id,
            interview_template=interview_schedule_obj.interview_template)
        for score in scorecards:
            rating = request.POST.get('rating' + str(score.id))
            comment = request.POST.get('comment' + str(score.id))
            interview_result.scorecard_results.add(
                models.InterviewScorecardResult.objects.create(title=score.title, comment=comment, rating=rating))

        interview_schedule_obj.job_stages_id.assessment_done = True
        interview_schedule_obj.job_stages_id.status = 2
        interview_schedule_obj.job_stages_id.save()

        interview_schedule_obj.is_completed = True
        interview_schedule_obj.save()

    return render(request, "company/ATS/start_interview.html",{'scorecards': scorecards,
                                                               'interview_schedule_obj':interview_schedule_obj})


def request_for_detail(request):
    if request.method=='POST':
        job_obj=models.JobCreation.objects.get(id=request.POST.get('job_id'))
        agency_candidate=AgencyModels.CandidateSecureData.objects.filter(job_id = job_obj,
                                                    company_id =job_obj.company_id,
                                                    candidate_id =User.objects.get(id=request.POST.get('candidate_id'))).update(is_request=True,update_at=datetime.datetime.now())
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def custom_template(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
        category = models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
        template = models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        if request.method == 'POST':
            enable_file_input = False
            file_input = None
            # if request.POST.get('enable_file_input') == 'on':
            #     enable_file_input = True
            # if request.FILES.get('file_input'):
            #     file_input = request.FILES.get('file_input')
            custom_template_obj, update = models.CustomTemplate.objects.update_or_create(
                company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),
                stage=stage,
                category=category,
                template=template,
                defaults={})
            ratings = request.POST.getlist('rate-title')
            for title in ratings:
                scorecard = models.CustomTemplateScorecard.objects.create(title=title)
                custom_template_obj.scorecards.add(scorecard)
            custom_template_obj.template.status = True
            custom_template_obj.template.save()


            current_site = get_current_site(request)
            header = request.is_secure() and "https" or "http"
            all_internaluser = models.Employee.objects.filter(company_id=models.Company.objects.get(
                user_id=request.user)).values_list('employee_id', flat=True)
            get_email = []
            template_name = models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            # link=header+"://"+current_site.domain+"/company/view_pre_requisites/"+str(pre_requisite.id)
            link = ''
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html', {'template_type': 'Custom Template',
                                                                                'username': request.user.first_name + ' ' + request.user.last_name,
                                                                                'templatename': template_name.name,
                                                                                'link': link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name + " has been added to your workspace"
            all_internal_users = models.Employee.objects.filter(
                company_id=models.Company.objects.get(user_id=request.user.id), employee_id__is_active=True)
            for i in all_internal_users:
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),
                                verb="Create Custom Template",
                                description=description, image="/static/notifications/icon/company/Template.png",
                                target_url="#")
            return redirect('company:template_listing')
        return render(request, "company/ATS/custom_template.html",context)
    else:
        return redirect('company:add_edit_profile')

def custom_stage(request, id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        stage_obj = models.CandidateJobStagesStatus.objects.get(id=id)
        custom_round_obj = models.CustomTemplate.objects.filter(company_id=stage_obj.company_id,
                                                                template=stage_obj.template)
        custom_result_data = None
        if custom_round_obj.exists():
            custom_round_data = custom_round_obj[0]
            custom_result = models.CustomResult.objects.filter(candidate_id=stage_obj.candidate_id,
                                                            company_id=stage_obj.company_id,
                                                            custom_template__template=stage_obj.template,
                                                            job_id=stage_obj.job_id)
            if custom_result.exists():
                custom_result_data = custom_result[0]
            scorecards = custom_round_data.scorecards.all()
            print('id>>', custom_stage)
            if request.method == 'POST':
                description = request.POST.get('description')
                custom_result, created = models.CustomResult.objects.update_or_create(candidate_id=stage_obj.candidate_id,
                                                                                    company_id=stage_obj.company_id,
                                                                                    job_id=stage_obj.job_id,
                                                                                    custom_template=custom_round_data,
                                                                                    defaults={
                                                                                        'user_id': request.user,
                                                                                    })
                for scorecard in scorecards:
                    rating = request.POST.get('rating' + str(scorecard.id))
                    comment = request.POST.get('comment' + str(scorecard.id))
                    custom_result.scorecard_results.add(
                        models.CustomScorecardResult.objects.create(title=scorecard.title, comment=comment, rating=rating))

                stage_obj.assessment_done = True
                stage_obj.status = 2
                stage_obj.save()
                return redirect('company:company_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,
                                job_id=stage_obj.job_id.id)
            context['custom_round_data']=custom_round_data
            context['custom_result_data']=custom_result_data
            context['scorecards']=scorecards
            return render(request, "company/ATS/custom_stage.html",context)
        else:
            return HttpResponse(False)
    else:
        return redirect('company:add_edit_profile')

def get_candidate_categories(request):
    term = request.GET.get('term')
    categories = models.CandidateCategories.objects.filter(category_name__istartswith=term,
                                                       company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)))
    categories_list = []
    for i in categories:
        data = {}
        data['id'] = i.id
        data['name'] = i.category_name
        categories_list.append(data)
    return JsonResponse(categories_list, safe=False)


def tracker(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        jobwise=[]
        candidatewise=[]

        job_list=models.Tracker.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('job_id')
        
        for i in job_list:
            jobdetail={'job_id':i.job_id.id,'job_title':i.job_id.job_title,'company':i.job_id.company_id.company_id.company_name,'remote_job':i.job_id.remote_job,
                        'exp':i.job_id.experience_year_max,'opening_date':i.job_id.publish_at,'job_type':i.job_id.job_type.name}

            count = models.AppliedCandidate.objects.filter(job_id=i.job_id).count()
            jobdetail['qpplicant']=count
            if i.job_id.salary_as_per_market:
                jobdetail['salary_range']='As per market' 
            else:
                jobdetail['salary_range']=i.job_id.min_salary+' LAP to ' +i.job_id.max_salary+' LAP'
            jobdetail['candidates']=[]
            jobwise_tracker = models.Tracker.objects.filter(job_id=i.job_id,company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id))).order_by('-update_at')
            for job in jobwise_tracker:
                if models.JobOffer.objects.filter(job_id=job.job_id,candidate_id=job.candidate_id,is_accepted=True).exists():
                    pass
                else:
                    jobdetail['candidates'].append({'candidatefname':job.candidate_id.first_name,'candidatelname':job.candidate_id.last_name,'current':job.current_stage,'candidateid':job.candidate_id.id,
                                                    'next':job.next_stage,'action':job.action_required,'currentcompleted':job.currentcompleted,'reject':job.reject,'withdraw':job.withdraw})
            jobwise.append(jobdetail)
            print("=========",jobdetail)
        context['job_tracker']=jobwise
        
        candidate_list=models.Tracker.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('candidate_id')
        for i in candidate_list:
            getprofile=CandidateModels.candidate_job_apply_detail.objects.get(candidate_id=i.candidate_id)
            if models.JobOffer.objects.filter(job_id=i.job_id,candidate_id=i.candidate_id,is_accepted=True).exists():
                pass
            else:
                candidatedetail={'candidatefname':i.candidate_id.first_name,'candidatelname':i.candidate_id.last_name,'designation':getprofile.designation,
                            'email':i.candidate_id.email,'contact':getprofile.contact,'total_exper':getprofile.total_exper,'notice':getprofile.notice.notice_period,
                            'current':str(getprofile.ctc)+' LAP','expectedctc':str(getprofile.expectedctc)+' LAP'}
                candidatedetail['jobs']=[]
                candidatewise_tracker = models.Tracker.objects.filter(candidate_id=i.candidate_id,company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id))).order_by('-update_at')
                for job in candidatewise_tracker:
                    candidatedetail['jobs'].append({'job_id':job.job_id.id,'job_title':job.job_id.job_title,'company':job.job_id.company_id.company_id.company_name,'current':job.current_stage,
                                                    'next':job.next_stage,'action':job.action_required,'currentcompleted':job.currentcompleted,'reject':job.reject,'withdraw':job.withdraw})
                candidatewise.append(candidatedetail)
        context['candidate_tracker']=candidatewise
        return render(request,'company/ATS/job-tracker.html',context)
    else:
        return redirect('company:add_edit_profile')

def submit_candidate(request, id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['job_id']= id
        candidates = models.InternalCandidateBasicDetails.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['candidates'] = candidates
        context['SalaryView'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Salary':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        internal_candidate=''
        if request.method == 'POST':
            print('post>>>', request.POST.get('selected_candidate'))
            context['source']=CandidateModels.Source.objects.all()
            context['notice_period']= CandidateModels.NoticePeriod.objects.all()
            context['countries']= CandidateModels.Country.objects.all()
            context['categories'] = models.CandidateCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
            context['jobtype']='company'
            job_obj = models.JobCreation.objects.get(id=int(id))
            context['jobid']=job_obj
            internal_candidate = models.InternalCandidateBasicDetails.objects.get(id=request.POST.get('selected_candidate'))
            context['edit_internal_candidate']=internal_candidate
            return render(request,'company/ATS/applied_candidate_detail_form.html',context)
            # fname = internal_candidate.first_name
            # lname = internal_candidate.last_name
            # email = internal_candidate.email
            # gender = internal_candidate.gender
            # resume = internal_candidate.resume
            # contact = internal_candidate.contact
            # designation = internal_candidate.designation
            # notice = internal_candidate.notice
            # ctc = internal_candidate.ctc
            # expectedctc = internal_candidate.expectedctc
            # total_exper = internal_candidate.total_exper
            # password = get_random_string(length=12)
            # if not User.objects.filter(email=internal_candidate.email.lower()).exists():

            #     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            #     if x_forwarded_for:
            #         ip = x_forwarded_for.split(',')[0]
            #     else:
            #         ip = request.META.get('REMOTE_ADDR')
            #     device_type = ""
            #     if request.user_agent.is_mobile:
            #         device_type = "Mobile"
            #     if request.user_agent.is_tablet:
            #         device_type = "Tablet"
            #     if request.user_agent.is_pc:
            #         device_type = "PC"
            #     browser_type = request.user_agent.browser.family
            #     browser_version = request.user_agent.browser.version_string
            #     os_type = request.user_agent.os.family
            #     os_version = request.user_agent.os.version_string
            #     usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
            #                                     password=password, ip=ip, device_type=device_type,
            #                                     browser_type=browser_type,
            #                                     browser_version=browser_version, os_type=os_type,
            #                                     os_version=os_version,
            #                                     referral_number=generate_referral_code())

            #     mail_subject = 'Activate your account'
            #     current_site = get_current_site(request)
            #     header=request.is_secure() and "https" or "http"
            #     # print('domain----===========',current_site.domain)
            #     html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
            #                                                                     'name': fname + ' ' + lname,
            #                                                                     'email': email,
            #                                                                     'domain': current_site.domain,
            #                                                                     'password': password, 
            #                                                                     'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id)
            #                                                                     })
            #     to_email = usr.email
            #     from_email = settings.EMAIL_HOST_USER
            #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            #     msg.attach_alternative(html_content, "text/html")
            #     # try:
            #     msg.send()
            #     internal_candidate.candidate_id = User.objects.get(email=email.lower())
            #     internal_candidate.save()
            #     add_candidate, create = CandidateModels.candidate_job_apply_detail.objects.update_or_create(
            #         candidate_id=internal_candidate.candidate_id, defaults={
            #             'gender': gender,
            #             'resume': resume,
            #             'contact': contact,
            #             'designation': designation,
            #             'notice': notice,
            #             'ctc': ctc,
            #             'expectedctc': expectedctc,
            #             'total_exper': total_exper})

            #     for i in internal_candidate.skills.all():
            #         print(type(int(i.id)))
            #         main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
            #         add_candidate.skills.add(main_skill_obj.id)
            #     for i in internal_candidate.prefered_city.all():
            #         main_city_obj = CandidateModels.City.objects.get(id=i.id)
            #         add_candidate.prefered_city.add(main_city_obj.id)
            #     add_candidate.save()
            # else:
            #     if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = internal_candidate.candidate_id).exists():
            #         add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id =internal_candidate.candidate_id,defaults={
            #                                                                         'gender' :gender,
            #                                                                         'resume' : resume,
            #                                                                         'contact' : contact,
            #                                                                         'designation' : designation,
            #                                                                         'notice' : notice,
            #                                                                         'ctc' : ctc,
            #                                                                         'expectedctc' : expectedctc,
            #                                                                         'total_exper' :  total_exper})
            #         for i in internal_candidate.skills.all():
            #             print(type(int(i.id)))
            #             main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
            #             add_candidate.skills.add(main_skill_obj.id)
            #         for i in internal_candidate.prefered_city.all():
            #             main_city_obj = CandidateModels.City.objects.get(id=i.id)
            #             add_candidate.prefered_city.add(main_city_obj.id)
            #         add_candidate.save()
            #     toemail=[internal_candidate.candidate_id.email]
            #     mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
            #     html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
            #     from_email = settings.EMAIL_HOST_USER
            #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
            #     msg.attach_alternative(html_content, "text/html")
            #     # try:
            #     msg.send()    
            # models.AssociateCandidateInternal.objects.update_or_create(company_id=job_obj.company_id,
            #                                                             job_id=job_obj,candidate_id=internal_candidate.candidate_id,
            #                                                             defaults={
            #                                                                 'internal_candidate_id':internal_candidate
            #                                                             })

            # models.AppliedCandidate.objects.update_or_create(
            #     company_id=job_obj.company_id, job_id=job_obj,
            #     candidate=internal_candidate.candidate_id, defaults={
            #         'user_id': User.objects.get(id=request.user.id),'submit_type':'Company'
            #     })

            # workflow = models.JobWorkflow.objects.get(job_id=job_obj)
            # current_stage=None
            # currentcompleted=False
            # next_stage = None
            # next_stage_sequance=0
            # # onthego change
            # if workflow.withworkflow:
            #     print("==========================withworkflow================================")
            #     workflow_stages = models.WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
            #     if workflow.is_application_review:
            #         print("==========================is_application_review================================")
            #         print('\n\n is_application_review')
            #         for stage in workflow_stages:
            #             if stage.sequence_number == 1:
            #                 status = 2
            #                 sequence_number = stage.sequence_number
            #             elif stage.sequence_number == 2:
            #                 print("==========================Application Review================================")
            #                 status = 1
            #                 stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
            #                 current_stage = stage_list_obj
            #                 next_stage_sequance=stage.sequence_number+1
            #                 models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                         candidate_id=internal_candidate.candidate_id,
            #                                                         job_id=job_obj, stage=stage_list_obj,
            #                                                         sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
            #                 sequence_number = stage.sequence_number + 1
            #                 status = 0
            #             else:
            #                 status = 0
            #                 sequence_number = stage.sequence_number + 1
            #                 next_stage = stage.stage
            #             models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                     candidate_id=internal_candidate.candidate_id,
            #                                                     job_id=job_obj, stage=stage.stage,
            #                                                     template=stage.template,
            #                                                     sequence_number=sequence_number,status=status,custom_stage_name=stage.stage_name)
            #     else:
            #         for stage in workflow_stages:
            #             if stage.sequence_number == 1:
            #                 status = 2
            #                 current_stage = stage.stage
            #             elif stage.sequence_number == 2:
            #                 status = 1
            #                 next_stage = stage.stage
            #             else:
            #                 status = 0
            #             models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                     candidate_id=internal_candidate.candidate_id,
            #                                                     job_id=job_obj, stage=stage.stage,
            #                                                     template=stage.template,
            #                                                     sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
            # if workflow.onthego:
            #     print("==========================onthego================================")
            #     onthego_stages = models.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

            #     if workflow.is_application_review:
            #         for stage in onthego_stages:
            #             if stage.sequence_number == 1:
            #                 status = 2
            #                 sequence_number = stage.sequence_number
            #                 models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                         candidate_id=internal_candidate.candidate_id,
            #                                                         job_id=job_obj, stage=stage.stage,
            #                                                         template=stage.template,
            #                                                         sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

            #                 status = 1
            #                 sequence_number = stage.sequence_number + 1
            #                 stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
            #                 current_stage = stage_list_obj
            #                 next_stage_sequance=stage.sequence_number+1
            #                 models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                         candidate_id=internal_candidate.candidate_id,
            #                                                         job_id=job_obj, stage=stage_list_obj,
            #                                                         sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
            #             else:
            #                 status = 0
            #                 sequence_number = stage.sequence_number + 1
            #                 current_stage = stage_list_obj
            #                 models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                         candidate_id=internal_candidate.candidate_id,
            #                                                         job_id=job_obj, stage=stage.stage,
            #                                                         template=stage.template,
            #                                                         sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)
            #     else:
            #         for stage in onthego_stages:
            #             if stage.sequence_number == 1:
            #                 status = 2
            #                 current_stage = stage.stage
            #             elif stage.sequence_number == 2:
            #                 status = 1
            #                 next_stage = stage.stage
            #             else:
            #                 status = 0
            #             models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
            #                                                     candidate_id=internal_candidate.candidate_id,
            #                                                     job_id=job_obj, stage=stage.stage,
            #                                                     template=stage.template,
            #                                                     sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
            # action_required=''
            # if next_stage_sequance!=0:
            #     if models.CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
            #                                                     candidate_id=internal_candidate.candidate_id,
            #                                                     job_id=job_obj,
            #                                                     sequence_number=next_stage_sequance).exists():
            #         next_stage=models.CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
            #                                                     candidate_id=internal_candidate.candidate_id,
            #                                                     job_id=job_obj,
            #                                                     sequence_number=next_stage_sequance).stage
            # if not current_stage==None:
            #     if current_stage.name=='Interview' :
            #         action_required='By Company/Agency'
            #     elif current_stage.name=='Application Review' :
            #         print('===========================onthe go action required')
            #         action_required='By Company'
            #     else:
            #         action_required='By Candidate'
            # if current_stage!='':
            #     print("==========================Tracker================================")
            #     models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=internal_candidate.candidate_id,company_id=job_obj.company_id,defaults={
            #                                             'current_stage':current_stage,'next_stage':next_stage,
            #                                             'action_required':action_required,'update_at':datetime.datetime.now()})
            # assign_job_internal = list(
            #     models.CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
            #                                     company_id=job_obj.company_id).values_list(
            #         'recruiter_id', flat=True))
            # assign_job_internal.append(job_obj.job_owner.id)
            # assign_job_internal.append(job_obj.contact_name.id)
            # assign_job_internal = list(set(assign_job_internal))
            # title = job_obj.job_title
            # chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(id=request.user.id).id, title=title,candidate_id=User.objects.get(id=internal_candidate.candidate_id.id))
            # print(assign_job_internal)
            # ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=internal_candidate.candidate_id.id).id)
            # for i in assign_job_internal:
            #     ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
            # ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
            # job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
            # description = "New candidate "+internal_candidate.candidate_id.first_name+" "+internal_candidate.candidate_id.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
            # current_site = get_current_site(request)
            # header=request.is_secure() and "https" or "http"
            # to_email=[]
            # to_email.append(job_obj.contact_name.email)
            # to_email.append(job_obj.job_owner.email)
            # candidate_email=User.objects.get(email=email.lower())
            # if job_obj.contact_name.id != request.user.id:
            #     notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission",
            #                                                                 description=description,image="/static/notifications/icon/company/Candidate_submission.png",
            #                                                                 target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(internal_candidate.candidate_id.id)+"/" + str(
            #                                                                     job_obj.id))
            # if job_obj.job_owner.id != request.user.id:
            #     notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission",
            #                                                                 description=description,image="/static/notifications/icon/company/Candidate_submission.png",
            #                                                                 target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(internal_candidate.candidate_id.id)+"/" + str(
            #                                                                     job_obj.id))
            # all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
            # for i in all_assign_users:
            #     if i.recruiter_type_internal:
            #         to_email.append(i.recruiter_id.email)
            #         if i.recruiter_id.id != request.user.id:
            #             notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
            #                                                                 description=description,image="/static/notifications/icon/company/Candidate_submission.png",
            #                                                                 target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(internal_candidate.candidate_id.id)+"/" + str(
            #                                                                     job_obj.id))

            # all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
            # stage_detail=''
            
            # if not current_stage==None:
            #     if current_stage.name=='Interview' :
            #         stage_detail='Interview'
            #         description="You have one application to review for the job "+job_obj.job_title
            #         for i in all_assign_users:
            #             if i.recruiter_type_internal:
            #                 if i.recruiter_id.id != request.user.id:
            #                     notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
            #                                                                         description=description,image="/static/notifications/icon/company/Candidate_submission.png",
            #                                                                         target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(internal_candidate.candidate_id.id)+"/" + str(
            #                                                                             job_obj.id))
            #     elif current_stage.name=='Application Review':
            #         stage_detail='Application Review'
            #         description="You have one application to review for the job "+job_obj.job_title
            #         for i in all_assign_users:
            #             if i.recruiter_type_internal:
            #                 if i.recruiter_id.id != request.user.id:
            #                     notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
            #                                                                         description=description,image="/static/notifications/icon/company/Candidate_submission.png",
            #                                                                         target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(internal_candidate.candidate_id.id)+"/" + str(
            #                                                                             job_obj.id))
            # to_email=list(set(to_email))
            # mail_subject = "New Candidate submission"
            # html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"New candidate has been submitted by "+request.user.first_name+" "+request.user.last_name+" – <a href="+header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(internal_candidate.candidate_id.id)+"/" + str(job_obj.id)+" >Applicant profile link.</a> Please login to review"})
            # from_email = settings.EMAIL_HOST_USER
            # msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
            # msg.attach_alternative(html_content, "text/html")
            # # try:
            # msg.send()
            
            # return redirect('company:created_job_view', id=job_obj.id)
        return render(request, "company/ATS/submit_candidate.html", context)
    else:
        return redirect('company:add_edit_profile')

def pre_requisites_edit(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        return render(request,'company/ATS/prerequisites-edit.html',context)
    else:
        return redirect('company:add_edit_profile')


def candidate_invite(request,id):
    if models.Employee.objects.filter(unique_id=id).exists():
        context = {'notice_period': CandidateModels.NoticePeriod.objects.all()}
        employee_obj = models.Employee.objects.get(unique_id=id)
        if request.method == 'POST':
            fname = request.POST.get('f-name')
            lname = request.POST.get('l-name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            if request.FILES.get('resume'):
                resume = request.FILES.get('resume')
            else:
                resume = None
            contact = request.POST.get('contact_num')
            designation = request.POST.get('designation-input')
            notice = CandidateModels.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
            ctc = request.POST.get('ctc-input')
            expectedctc = request.POST.get('expected-ctc')
            current_city = CandidateModels.City.objects.get(id=request.POST.get('candidate_current_city'))
            total_exper = request.POST.get('professional-experience-year') + '.' + request.POST.get(
                'professional-experience-month')

            # add profile pic
            if request.FILES.get('profile_pic'):
                profile_pic = request.FILES.get('profile_pic')
            else:
                profile_pic = None

            temp_obj,created = models.CandidateTempDatabase.objects.update_or_create(email=email,
                                                                    company_id=employee_obj.company_id, defaults={
                    'user_id': employee_obj.employee_id,
                    'first_name': fname,
                    'last_name': lname,
                    'gender': gender,
                    'resume': resume,
                    'profile_pic': profile_pic,
                    'contact': contact,
                    'designation': designation,
                    'notice': notice,
                    'ctc': ctc,
                    'expectedctc': expectedctc,
                    'total_exper': total_exper,
                    'current_city': current_city,
                })

            for i in request.POST.getlist('professional_skills'):
                if i.isnumeric():
                    main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                    temp_obj.skills.add(main_skill_obj)
                else:
                    skill_cre = CandidateModels.Skill.objects.create(name=i)
                    temp_obj.skills.add(skill_cre)
            for i in request.POST.getlist('candidate_search_city'):
                if i.isnumeric():
                    main_city_obj = CandidateModels.City.objects.get(id=i)
                    temp_obj.prefered_city.add(main_city_obj)

            if User.objects.filter(email=email.lower()).exists():
                temp_obj.candidate_id = User.objects.get(email=email.lower())
            temp_obj.save()

            if request.POST.get('create_account') == 'create_account':
                password = request.POST.get('password')
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

                usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
                                                        password=password, ip=ip, device_type=device_type,
                                                        browser_type=browser_type,
                                                        browser_version=browser_version, os_type=os_type,
                                                        os_version=os_version,
                                                        referral_number=generate_referral_code())
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

                    add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                                                                                    'gender' :gender,
                                                                                    'resume' : resume,
                                                                                    'contact' : contact,
                                                                                    'designation' : designation,
                                                                                    'notice' : notice,
                                                                                    'ctc' : ctc,
                                                                                    'expectedctc' : expectedctc,
                                                                                    'total_exper' :  total_exper})
                except BadHeaderError:
                    new_registered_usr = User.objects.get(email__exact=email).delete()
                    context['message'] = "email not send"


            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            description = fname+" "+ lname +" filled their detail via shared link please review"
            notify.send(request.user, recipient=User.objects.get(id=employee_obj.employee_id.id), verb="Candidate(In review)",
                        description=description,image="/static/notifications/icon/company/Application_Review.png",
                        target_url=header+"://"+current_site.domain+"/company/verify_candidate/" + str(
                                temp_obj.id))
            return render(request,'company/ATS/thankyou.html',context)
        return render(request,'company/ATS/candidate_invite.html',context)
    else:
        return render(request, 'accounts/404.html')


def verify_candidate(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        candid_data = models.CandidateTempDatabase.objects.get(id=id)
        context['candid_data'] = candid_data
        if request.method == 'POST':
            fname = request.POST.get('f-name')
            lname = request.POST.get('l-name')
            gender = request.POST.get('gender')
            
            if request.FILES.get('resume'):
                resume = request.FILES.get('resume')
            else:
                resume = candid_data.resume

            contact = request.POST.get('contact_num')
            designation = request.POST.get('designation-input')
            notice = CandidateModels.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
            ctc = request.POST.get('ctc-input')
            expectedctc = request.POST.get('expected-ctc')
            current_city = CandidateModels.City.objects.get(id=request.POST.get('candidate_current_city'))
            total_exper = request.POST.get('professional-experience-year') + '.' + request.POST.get(
                'professional-experience-month')

            # add profile pic
            if request.FILES.get('profile_pic'):
                profile_pic = request.FILES.get('profile_pic')
            else:
                profile_pic = candid_data.profile_pic

            candidate_obj, created = models.InternalCandidateBasicDetails.objects.update_or_create(email=candid_data.email,
                                                                            company_id=candid_data.company_id,
                                                                            defaults={
                                                                                'user_id': candid_data.user_id,
                                                                                'first_name': fname,
                                                                                'last_name': lname,
                                                                                'gender': gender,
                                                                                'resume': resume,
                                                                                'profile_pic': profile_pic,
                                                                                'contact': contact,
                                                                                'designation': designation,
                                                                                'notice': notice,
                                                                                'ctc': ctc,
                                                                                'expectedctc': expectedctc,
                                                                                'total_exper': total_exper,
                                                                                'current_city': current_city,
                                                                                'update_at': datetime.datetime.now()
                                                                            })


            if request.POST.getlist('professional_skills'):
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                        candidate_obj.skills.add(main_skill_obj)
                    else:
                        skill_cre = CandidateModels.Skill.objects.create(name=i)
                        candidate_obj.skills.add(skill_cre)
            else:
                for i in candid_data.prefered_city.all():
                    candidate_obj.prefered_city.add(i)


            if request.POST.getlist('candidate_search_city'):
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = CandidateModels.City.objects.get(id=i)
                        candidate_obj.prefered_city.add(main_city_obj)
            else:
                for i in candid_data.skills.all():
                    candidate_obj.skills.add(i)


            for i in request.POST.getlist('source'):
                if i.isnumeric():
                    main_source_obj = CandidateModels.Source.objects.get(id=i)
                    candidate_obj.source = main_source_obj
                else:
                    source_cre = CandidateModels.Source.objects.create(name=i)
                    candidate_obj.source = source_cre

            for i in request.POST.getlist('tags'):
                if i.isnumeric():
                    main_skill_obj = models.Tags.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                    candidate_obj.tags.add(main_skill_obj)
                else:
                    tag_cre = models.Tags.objects.create(name=i,company_id=candid_data.company_id.id,user_id= candid_data.user_id)
                    candidate_obj.tags.add(tag_cre)

            for i in request.POST.getlist('candidate_category'):
                if i.isnumeric():
                    main_categ_obj = models.CandidateCategories.objects.get(id=i)
                    candidate_obj.categories.add(main_categ_obj)
                else:
                    categ_create = models.CandidateCategories.objects.create(
                        company_id=models.Company.objects.get(user_id=request.user.id), user_id=request.user,
                        category_name=i)
                    candidate_obj.categories.add(categ_create)

            if User.objects.filter(email=candid_data.email.lower()).exists():
                candidate_obj.candidate_id = User.objects.get(email=candid_data.email)
            candidate_obj.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            all_internal_users=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),employee_id__is_active=True)
            for i in all_internal_users:
                description = "New candidate has been added to your Database by "+candid_data.first_name+" "+candid_data.last_name
                if i.employee_id.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.employee_id.id),verb="New Candidate",
                                                                        description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                        target_url=header+"://"+current_site.domain+"/company/view_candidate/"+str(candidate_obj.id))
            models.CandidateTempDatabase.objects.get(id=id).delete()
            return redirect('company:all_candidates')
        return render(request, 'company/ATS/verify_candidate.html', context)
    else:
        return redirect('company:add_edit_profile')




def category_add_or_update_view(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        # context['Add'] = False
        # context['Edit'] = False
        # context['Delete'] = False
        # context['permission'] = check_permission(request)
        # for permissions in context['permission']:
        #     if permissions.permissionsmodel.modelname == 'Department':
        #         print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
        #         if permissions.permissionname == 'Add':
        #             context['Add'] = True
        #         if permissions.permissionname == 'Edit':
        #             context['Edit'] = True
        #         if permissions.permissionname == 'Delete':
        #             context['Delete'] = True
        # if context['Add'] or context['Edit'] or context['Delete']:
        context['categories'] = models.CandidateCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        if request.method == "POST":
            id= request.POST.get("category_id")
            category_name = request.POST.get("category_name")
            # department,created = models.Department.objects.get_or_create(name=department_name)
            try:
                category = models.CandidateCategories.objects.get(category_name__iexact=category_name,company_id=models.Company.objects.get(user_id=request.user.id))
                created=False
            except:
                created = True
                print("no category with that id found")
            data = {}
            if created == False:
                data["status"] = created
                return HttpResponse(json.dumps(data))
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            if id == "null":
                category = models.CandidateCategories.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),category_name=category_name)
                operation = "created"
                role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                get_admin = models.Employee.objects.filter(role=role_id_get,
                                                                        company_id=models.Company.objects.get(
                                                                            user_id=request.user)).values_list(
                    'employee_id', flat=True)
                    
                for i in get_admin:
                    description = request.user.first_name + "Add Categories"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Add Categories",
                                    description=description,
                                    target_url="#")
            else:
                category = models.CandidateCategories.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=int(id))
                category.category_name = category_name
                category.save()
                operation = "update"
                role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                get_admin = models.Employee.objects.filter(role=role_id_get,
                                                                        company_id=models.Company.objects.get(
                                                                            user_id=request.user)).values_list(
                    'employee_id', flat=True)
                for i in get_admin:
                    description = request.user.first_name + "Update category"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Update category",
                                    description=description,
                                    target_url="#")
            # if
            data["status"] = created
            data['operation'] = operation
            data['category_name'] =category.category_name
            data['category_id'] =category.id
            return HttpResponse(json.dumps(data))
        return render(request,"company/ATS/add_category.html",context)
    else:
        return redirect('company:add_edit_profile')
def delete_candidatecategory(request):
    dept_id = request.POST.get("category_id")
    category = models.CandidateCategories.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=int(dept_id))
    category.delete()
    return HttpResponse("true")


def coding_total_questions(request,id):
    categ = models.CodingSubjectCategory.objects.get(subject_id=id)
    count = models.CodingQuestion.objects.filter(category_id=categ).count()
    return HttpResponse(str(count))


def mcq_total_questions(request,id):
    if request.method=='POST':
        mcq_subject_id = models.MCQ_subject.objects.get(id=int(id))

        basic_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='basic')
        advance_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='advance')
        intermediate_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='intermediate')

        total_que = models.mcq_Question.objects.filter(mcq_subject=mcq_subject_id)
        basic_count = total_que.filter(question_level=basic_type.id).count()
        advance_count = total_que.filter(question_level=advance_type.id).count()
        intermediate_count = total_que.filter(question_level=intermediate_type.id).count()
        data={'status':True,'total':total_que.count(),'basic_count':basic_count,'advance_count':advance_count,'intermediate_count':intermediate_count}
        return HttpResponse(json.dumps(data))


def image_total_questions(request,id):
    if request.method=='POST':
        img_subject_id = models.ImageSubject.objects.get(id=int(id))

        basic_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='basic')
        advance_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='advance')
        intermediate_type=CandidateModels.QuestionDifficultyLevel.objects.get(level_name='intermediate')

        total_que = models.ImageQuestion.objects.filter(subject=img_subject_id)
        basic_count = total_que.filter(question_level=basic_type.id).count()
        advance_count = total_que.filter(question_level=advance_type.id).count()
        intermediate_count = total_que.filter(question_level=intermediate_type.id).count()
        data={'status':True,'total':total_que.count(),'basic_count':basic_count,'advance_count':advance_count,'intermediate_count':intermediate_count}
        return HttpResponse(json.dumps(data))


def category_all(request):
    if 'term' in request.GET:
        qs = models.CandidateCategories.objects.filter(category_name__icontains=request.GET.get('term'),company_id=models.Company.objects.get(user_id=request.user.id))
        titles = list()
        for category in qs:
            titles.append(category.category_name)
        # titles = [product.title for product in qs]
        return JsonResponse(titles, safe=False)



def notification_list(request):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        return render(request,"company/ATS/notification_list.html",context)
    else:
        return redirect('company:add_edit_profile')

def test_devices(request):
    return render(request,"company/ATS/test_devices.html")



def add_custom_stage_detail(request,id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        stage_obj = models.CandidateJobStagesStatus.objects.get(id=id)
        if request.method == 'POST':
            if 'submit_details' in request.POST:
                print('\n\n\n\n\n\nstage obj > custom', stage_obj)
                custom_template_obj = models.CustomTemplate.objects.filter(company_id=stage_obj.company_id,
                                                                        template=stage_obj.template)
                if custom_template_obj.exists():
                    custom_template_obj = custom_template_obj.first()
                    enable_file_input = False
                    file_input = None
                    enable_response = False
                    if request.POST.get('enable_file_input') == 'on':
                        enable_file_input = True
                    if request.POST.get('enable_response') == 'on':
                        enable_response = True
                    if request.FILES.get('file_input'):
                        file_input = request.FILES.get('file_input')
                    custom_result, created = models.CustomResult.objects.update_or_create(candidate_id=stage_obj.candidate_id,
                                                                                        company_id=stage_obj.company_id,
                                                                                        job_id=stage_obj.job_id,
                                                                                        custom_template=custom_template_obj,
                                                                                        defaults={
                                                                                            'title':request.POST.get('title'),
                                                                                            'description':request.POST.get('description'),
                                                                                            'enable_file_input':enable_file_input,
                                                                                            'enable_response':enable_response,
                                                                                            'file_input': file_input,
                                                                                        })

                    return redirect('company:company_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,
                                    job_id=stage_obj.job_id.id)
                else:
                    return HttpResponse('Template does not exists !!')
        return render(request, "company/ATS/add_custom_stage_detail.html",context)
    else:
        return redirect('company:add_edit_profile')


def custom_template_view(request,template_id):
    context={}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        custom_template = models.CustomTemplate.objects.get(template__id=template_id)
        context['custom_template'] = custom_template
        return render(request, "company/ATS/custom_template_view.html",context)
    else:
        return redirect('company:add_edit_profile')



def daily_submission(request,duration=None):
    context={}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        if duration=='yesterday':
            daily_submit_candidate= models.DailySubmission.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),company_job_id__close_job=False,company_job_id__is_publish=True,create_at__startswith=datetime.date.today()-datetime.timedelta(days=1))
        elif duration=='this_week':
            daily_submit_candidate= models.DailySubmission.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),company_job_id__close_job=False,company_job_id__is_publish=True,create_at__gte=datetime.date.today()-datetime.timedelta(days=2))
        elif duration=='this_month':
            daily_submit_candidate= models.DailySubmission.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),company_job_id__close_job=False,company_job_id__is_publish=True,create_at__month=datetime.datetime.now().month)
        elif duration=='custom':
            to_date=request.GET.get('to')
            from_date=request.GET.get('from')
            
            daily_submit_candidate= models.DailySubmission.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),company_job_id__close_job=False,company_job_id__is_publish=True,create_at__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d'),create_at__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d'))
        else:
            daily_submit_candidate= models.DailySubmission.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),company_job_id__close_job=False,company_job_id__is_publish=True,create_at__startswith=datetime.date.today())
        
        candidate=[]
        
        for i in daily_submit_candidate:
            get_job=models.JobWorkflow.objects.get(job_id=i.company_job_id)
            candidate_stage=models.CandidateJobStagesStatus.objects.filter(job_id=i.company_job_id,candidate_id=i.candidate_id)
            data={'candidate':i,'get_job':get_job,'candidate_stage':candidate_stage}
            candidate.append(data)
        context['candidates']=candidate
        if request.method=='POST':
            candidate_obj=User.objects.get(id=request.POST.get('candidateid'))
            job_obj=models.JobCreation.objects.get(id=request.POST.get('jobid'))
            if 'withdraw' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=job_obj.company_id,
                                                                defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
            
            else:
                
                stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
                if 'shortlist' in request.POST:
                    stage_obj.action_performed = True
                    stage_obj.status = 2
                    stage_obj.save()
                    new_sequence_no = stage_obj.sequence_number + 1
                    if models.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=candidate_obj,
                                                            sequence_number=new_sequence_no).exists():
                        new_stage_status = models.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=candidate_obj,
                                                                                    sequence_number=new_sequence_no)
                        new_stage_status.status = 1
                        new_stage_status.save()
                        return HttpResponse(True)
                if 'reject' in request.POST:
                    stage_obj.status = -1
                    stage_obj.action_performed = True
                    stage_obj.assessment_done = True
                    stage_obj.save()
        return render(request,"company/ATS/daily_submission.html",context)
    else:
        return redirect('company:add_edit_profile')



def internal_candidate_basic_detail(request,int_cand_detail_id=None):
    context={}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['Add'] = False
        context['Edit'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        context['categories'] = models.CandidateCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        # if models.JobCreation.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),is_publish=True,close_job=False).exists():
        #     context['agency']=models.Agency.objects.get(user_id=request.user.id)
        edit_internal_candidate=''
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
        if context['Add'] or context['Edit'] :
            if request.method == 'POST':
                verify = request.POST.get('verify')
                if verify=="verify":
                    verifydata=True
                else:
                    verifydata=False
                secure_resume_get = request.POST.get('secure-resume')
                if secure_resume_get=="Secure-Resume":
                    secure_resume=True
                else:
                    secure_resume=False
                fname = request.POST.get('f-name')
                lname = request.POST.get('l-name')
                email = request.POST.get('email')
                gender = request.POST.get('gender')
                resume = request.FILES.get('resume')
                if models.InternalCandidateBasicDetails.objects.filter(email=email).exists():
                    edit_internal_candidate=models.InternalCandidateBasicDetails.objects.get(email=email,company_id=models.Company.objects.get(user_id=request.user.id))
                if resume == None:
                    if edit_internal_candidate:
                        resume = edit_internal_candidate.resume
                contact = request.POST.get('contact-num')
                employee_id = request.POST.get('candidate_c_id')
                designation = request.POST.get('designation-input')
                notice = CandidateModels.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
                current_city = CandidateModels.City.objects.get(id=request.POST.get('candidate_current_city'))
                ctc = request.POST.get('ctc-input')
                expectedctc = request.POST.get('expected-ctc')
                total_exper = request.POST.get('professional-experience-year') +'.'+ request.POST.get(
                    'professional-experience-month')
                # source=CandidateModels.Source.objects.get(id=request.POST.get('source'))

                models.InternalCandidateBasicDetails.objects.update_or_create(email=email,company_id = models.Company.objects.get(user_id=request.user.id),defaults={
                    'user_id' : User.objects.get(id=request.user.id),
                    'first_name' : fname,
                    'last_name' : lname,
                    'gender' : gender,
                    'resume' : resume,
                    'contact' : contact,
                    'designation': designation,
                    'notice' : notice,
                    'ctc' : ctc,
                    'current_city':current_city,
                    'expectedctc' : expectedctc,
                    'total_exper' : total_exper,
                    'update_at':datetime.datetime.now()
                })
                add_skill=models.InternalCandidateBasicDetails.objects.get(email=email,company_id = models.Company.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_skill.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_skill.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_skill.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                        add_skill.tags.add(tag_cre)
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                        add_skill.skills.add(main_skill_obj)
                    else:
                        main_skill_obj=CandidateModels.Skill.objects.create(name=i)
                        add_skill.skills.add(main_skill_obj)
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = CandidateModels.City.objects.get(id=i)
                        add_skill.prefered_city.add(main_city_obj)
                for i in request.POST.getlist('candidate_category'):
                    if i.isnumeric():
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_skill.categories.add(main_categ_obj)
                if User.objects.filter(email=email.lower()).exists():
                    add_skill.candidate_id=User.objects.get(email=email.lower())
                add_skill.save()
                job_id=request.POST.get('job').split('-')
                jobid=job_id[1]
                jobtype=job_id[0]
                if not User.objects.filter(email=email.lower()).exists():
                    print('============created')
                    usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
                                                        password=password, ip=ip, device_type=device_type,
                                                        browser_type=browser_type,
                                                        browser_version=browser_version, os_type=os_type,
                                                        os_version=os_version,
                                                        referral_number=generate_referral_code())
                    mail_subject = 'Activate your account'
                    current_site = get_current_site(request)
                    # print('domain----===========',current_site.domain)
                    html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                                                                                        'name': fname + ' ' + lname,
                                                                                        'email': email,
                                                                                        'domain': current_site.domain,
                                                                                        'password': password,
                                                                                        'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id) })
                    to_email = usr.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    # try:
                    msg.send()
                    get_internalcandidate.candidate_id = User.objects.get(email=email.lower())
                    get_internalcandidate.save()
                    add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                                                                                        'gender' :gender,
                                                                                        'resume' : resume,
                                                                                        'contact' : contact,
                                                                                        'designation' : designation,
                                                                                        'notice' : notice,
                                                                                        'ctc' : ctc,
                                                                                        'expectedctc' : expectedctc,
                                                                                        'total_exper' :  total_exper})

                    for i in get_internalcandidate.skills.all():
                        print(type(int(i.id)))
                        main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                        add_candidate.skills.add(main_skill_obj.id)
                    for i in get_internalcandidate.prefered_city.all():
                        main_city_obj = CandidateModels.City.objects.get(id=i.id)
                        add_candidate.prefered_city.add(main_city_obj.id)
                    add_candidate.save()
                else:

                    if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = User.objects.get(email=email.lower())).exists():
                        add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                                                                                        'gender' :gender,
                                                                                        'resume' : resume,
                                                                                        'contact' : contact,
                                                                                        'designation' : designation,
                                                                                        'notice' : notice,
                                                                                        'ctc' : ctc,
                                                                                        'expectedctc' : expectedctc,
                                                                                        'total_exper' :  total_exper})
                        for i in get_internalcandidate.skills.all():
                            print(type(int(i.id)))
                            main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                            add_candidate.skills.add(main_skill_obj.id)
                        for i in get_internalcandidate.prefered_city.all():
                            main_city_obj = CandidateModels.City.objects.get(id=i.id)
                            add_candidate.prefered_city.add(main_city_obj.id)
                        add_candidate.save()
                models.DailySubmission.objects.update_or_create(email=email.lower(),company_job_id=models.JobCreation.objects.get(id=jobid),internal_candidate_id_company=add_skill,company_id = models.Company.objects.get(user_id=request.user.id),defaults={
                    'candidate_id':User.objects.get(email=email.lower()),
                    'job_type':'company',
                    'internal_user_company' : models.Employee.objects.get(employee_id=User.objects.get(id=request.user.id)),
                    'first_name' : fname,
                    'last_name' : lname,
                    'gender' : gender,
                    'resume' : resume,
                    'contact' : contact,
                    'designation': designation,
                    'notice' : notice,
                    'ctc' : ctc,
                    'verify':verifydata,
                    'current_city':current_city,
                    'expectedctc' : expectedctc,
                    'total_exper' : total_exper,
                    'update_at':datetime.datetime.now()
                })
                add_deatil=models.DailySubmission.objects.get(email=email,company_job_id=models.JobCreation.objects.get(id=jobid),internal_candidate_id_company=add_skill,company_id = models.Company.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_deatil.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_deatil.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_deatil.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                        add_deatil.tags.add(tag_cre)
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                        add_deatil.skills.add(main_skill_obj)
                    else:
                        main_skill_obj=CandidateModels.Skill.objects.create(name=i)
                        add_deatil.skills.add(main_skill_obj)
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = CandidateModels.City.objects.get(id=i)
                        add_deatil.prefered_city.add(main_city_obj)
                for i in request.POST.getlist('candidate_category'):
                    if i.isnumeric():
                        main_categ_obj = models.CandidateCategories.objects.get(category_name=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_deatil.categories.add(main_categ_obj)
                    else:
                        main_categ_obj = models.CandidateCategories.objects.create(id=i,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                        add_deatil.categories.add(main_categ_obj)
                if not verifydata:
                    add_deatil.verified=True
                    add_deatil.applied=True
                add_deatil.save()
                if verifydata:
                    mail_subject = '"VErify Detail" from Bidcruit'
                    current_site = get_current_site(request)
                    html_content = render_to_string('accounts/verify_detail.html', {'user': add_deatil,
                                                                                        'url':'candidate_verify',
                                                                                        'email': email,
                                                                                        'domain': current_site.domain,
                                                                                        'uid': urlsafe_base64_encode(
                                                                                            force_bytes(add_deatil.pk))})
                    to_email = add_deatil.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                else:
                    add_deatil.applied=True
                    add_deatil.save()
                    get_internalcandidate=models.InternalCandidateBasicDetails.objects.get(id=add_skill.id,company_id=models.Company.objects.get(user_id=request.user.id))
                    candidates_array = ''
                    job_obj = models.JobCreation.objects.get(id=jobid)
                    candidates = models.AppliedCandidate.objects.filter(job_id=job_obj)
                    candidates_array = [i.candidate.id for i in candidates]
                    agency_submit_candidate = models.AssociateCandidateAgency.objects.filter(job_id=job_obj).values_list(
                        'candidate_id', flat=True)
                    candidates_array = list(chain(candidates_array, agency_submit_candidate))
                    if get_internalcandidate.candidate_id==None or not get_internalcandidate.candidate_id.id in candidates_array:
                        fname = get_internalcandidate.first_name
                        lname = get_internalcandidate.last_name
                        email = get_internalcandidate.email
                        gender = get_internalcandidate.gender
                        resume = get_internalcandidate.resume
                        contact = get_internalcandidate.contact
                        designation = get_internalcandidate.designation
                        notice = CandidateModels.NoticePeriod.objects.get(id=get_internalcandidate.notice.id)
                        ctc = get_internalcandidate.ctc
                        expectedctc = get_internalcandidate.expectedctc
                        current_city = CandidateModels.City.objects.get(id=get_internalcandidate.current_city.id)
                        total_exper = get_internalcandidate.total_exper
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
                        print('============\n\n')
                        current_site = get_current_site(request)
                        header=request.is_secure() and "https" or "http"
                        if not User.objects.filter(email=email.lower()).exists():
                            print('============created')
                            usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
                                                                password=password, ip=ip, device_type=device_type,
                                                                browser_type=browser_type,
                                                                browser_version=browser_version, os_type=os_type,
                                                                os_version=os_version,
                                                                referral_number=generate_referral_code())
                            mail_subject = 'Activate your account'
                            current_site = get_current_site(request)
                            # print('domain----===========',current_site.domain)
                            html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                                                                                                'name': fname + ' ' + lname,
                                                                                                'email': email,
                                                                                                'domain': current_site.domain,
                                                                                                'password': password,
                                                                                                'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id) })
                            to_email = usr.email
                            from_email = settings.EMAIL_HOST_USER
                            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                            msg.attach_alternative(html_content, "text/html")
                            # try:
                            msg.send()
                            get_internalcandidate.candidate_id = User.objects.get(email=email.lower())
                            get_internalcandidate.save()
                            add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                                                                                                'gender' :gender,
                                                                                                'resume' : resume,
                                                                                                'contact' : contact,
                                                                                                'designation' : designation,
                                                                                                'notice' : notice,
                                                                                                'ctc' : ctc,
                                                                                                'expectedctc' : expectedctc,
                                                                                                'total_exper' :  total_exper})

                            for i in get_internalcandidate.skills.all():
                                print(type(int(i.id)))
                                main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                                add_candidate.skills.add(main_skill_obj.id)
                            for i in get_internalcandidate.prefered_city.all():
                                main_city_obj = CandidateModels.City.objects.get(id=i.id)
                                add_candidate.prefered_city.add(main_city_obj.id)
                            add_candidate.save()
                        else:

                            if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = User.objects.get(email=email.lower())).exists():
                                add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                                                                                                'gender' :gender,
                                                                                                'resume' : resume,
                                                                                                'contact' : contact,
                                                                                                'designation' : designation,
                                                                                                'notice' : notice,
                                                                                                'ctc' : ctc,
                                                                                                'expectedctc' : expectedctc,
                                                                                                'total_exper' :  total_exper})
                                for i in get_internalcandidate.skills.all():
                                    print(type(int(i.id)))
                                    main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                                    add_candidate.skills.add(main_skill_obj.id)
                                for i in get_internalcandidate.prefered_city.all():
                                    main_city_obj = CandidateModels.City.objects.get(id=i.id)
                                    add_candidate.prefered_city.add(main_city_obj.id)
                                add_candidate.save()
                            toemail=[email]
                            mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
                            html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
                            from_email = settings.EMAIL_HOST_USER
                            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
                            msg.attach_alternative(html_content, "text/html")
                            # try:
                            msg.send()  
                        current_site = get_current_site(request)
                        header=request.is_secure() and "https" or "http"  
                        
                        associate_job_list=[jobid]
                        for joblist_id in associate_job_list:
                            job_obj=models.JobCreation.objects.get(id=int(joblist_id))
                            notify.send(request.user, recipient=User.objects.get(email=email.lower()), verb="Application",
                                        description="You have succesfully applied for the Job "+str(job_obj.job_title)+".",image="/static/notifications/icon/company/Job_Create.png",
                                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                            job_obj.id)+"/company")
                            # fit_score(add_candidate,job_obj)
                            # agencyid= models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
                            models.AssociateCandidateInternal.objects.update_or_create(company_id=job_obj.company_id,job_id=models.JobCreation.objects.get(id=int(joblist_id)),candidate_id=User.objects.get(email=email.lower()),defaults={
                                    'internal_candidate_id':models.InternalCandidateBasicDetails.objects.get(id=add_skill.id)
                                })
                            models.AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,dailysubmission=add_deatil,job_id=job_obj,candidate=User.objects.get(email=email.lower()),defaults={
                            'user_id':User.objects.get(id=request.user.id),'submit_type':'Company'
                            })
                            workflow = models.JobWorkflow.objects.get(job_id=job_obj)
                            currentcompleted=False
                            current_stage=None
                            next_stage = None
                            next_stage_sequance=0
                            # onthego change
                            if workflow.withworkflow:
                                print("==========================withworkflow================================")
                                workflow_stages = models.WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
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
                                            stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
                                            current_stage = stage_list_obj
                                            next_stage_sequance=stage.sequence_number+1
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                    candidate_id=User.objects.get(email=email.lower()),
                                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                                    sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                                            sequence_number = stage.sequence_number + 1
                                            status = 0
                                        else:
                                            status = 0
                                            sequence_number = stage.sequence_number + 1
                                            next_stage = stage.stage
                                        models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
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
                                        models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                                job_id=job_obj, stage=stage.stage,
                                                                                template=stage.template,
                                                                                sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
                            if workflow.onthego:
                                print("==========================onthego================================")
                                onthego_stages = models.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

                                if workflow.is_application_review:
                                    for stage in onthego_stages:
                                        if stage.sequence_number == 1:
                                            status = 2
                                            sequence_number = stage.sequence_number
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                    candidate_id=User.objects.get(email=email.lower()),
                                                                                    job_id=job_obj, stage=stage.stage,
                                                                                    template=stage.template,
                                                                                    sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                                            status = 1
                                            sequence_number = stage.sequence_number + 1
                                            stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
                                            current_stage = stage_list_obj
                                            next_stage_sequance=stage.sequence_number+1
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                    candidate_id=User.objects.get(email=email.lower()),
                                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                                    sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                                        else:
                                            status = 0
                                            sequence_number = stage.sequence_number + 1
                                            current_stage = stage_list_obj
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
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
                                        models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                                job_id=job_obj, stage=stage.stage,
                                                                                template=stage.template,
                                                                                sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
                            action_required=''
                            if next_stage_sequance!=0:
                                if models.CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                                job_id=job_obj,
                                                                                sequence_number=next_stage_sequance).exists():
                                    next_stage=models.CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
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
                                models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=User.objects.get(email=email.lower()),company_id=job_obj.company_id,defaults={
                                                                        'current_stage':current_stage,'next_stage':next_stage,
                                                                        'action_required':action_required,'update_at':datetime.datetime.now()})
                            assign_job_internal = list(
                                models.CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
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
                            job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
                            description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
                            to_email=[]
                            to_email.append(job_obj.contact_name.email)
                            to_email.append(job_obj.job_owner.email)
                            if job_obj.contact_name.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission",
                                                                                            description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                                            target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                                job_obj.id))
                            if job_obj.job_owner.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission",
                                                                                            description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                                            target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                                job_obj.id))
                            all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                            for i in all_assign_users:
                                if i.recruiter_type_internal:
                                    to_email.append(i.recruiter_id.email)
                                    if i.recruiter_id.id != request.user.id:
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
                                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview schedule",
                                                                                                    description=description,image="/static/notifications/icon/company/interview.png",
                                                                                                    target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                                        job_obj.id))
                                elif current_stage.name=='Application Review':
                                    stage_detail='Application Review'
                                    description="You have one application to review for the job "+job_obj.job_title
                                    for i in all_assign_users:
                                        if i.recruiter_type_internal:
                                            if i.recruiter_id.id != request.user.id:
                                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
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
                return redirect('company:daily_submission')

            return render(request,'company/ATS/internal_candidate_basic_form.html',context)
        else:
            return render(request, 'company/ATS/not_permoission.html', context)
    else:
        return redirect('company:add_edit_profile')


def get_job(request):
    candidateid = request.POST.get("candidateid")
    data=[]
    if candidateid!='':
        appliedjob=models.AppliedCandidate.objects.filter(candidate=User.objects.get(id=candidateid))
        appliedjob=[i.job_id.id for i in appliedjob]
        jobs=models.JobCreation.objects.filter(close_job=False,is_publish=True,company_id=models.Company.objects.get(user_id=request.user)).exclude(id__in=appliedjob)
        for job in jobs:
            data.append({'id':'company-'+str(job.id),'title':job.job_title})
    else:
        jobs=models.JobCreation.objects.filter(close_job=False,is_publish=True,company_id=models.Company.objects.get(user_id=request.user))
        for job in jobs:
            data.append({'id':'company-'+str(job.id),'title':job.job_title})

    return JsonResponse({'data':data}, safe=False)


def applied_candidate_form(request,int_cand_detail_id=None):
    context={}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['categories'] = models.CandidateCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        edit_internal_candidate=''
        if int_cand_detail_id:
            edit_internal_candidate = models.InternalCandidateBasicDetails.objects.get(id=int(int_cand_detail_id))
        if request.method == 'POST':
            job_type=request.POST.get('jobtype')
            verify = request.POST.get('verify')
            if verify=="verify":
                verifydata=True
            else:
                verifydata=False
            secure_resume_get = request.POST.get('secure-resume')
            if secure_resume_get=="Secure-Resume":
                secure_resume=True
            else:
                secure_resume=False
            fname = request.POST.get('f-name')
            lname = request.POST.get('l-name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            resume = request.FILES.get('resume')
            if resume == None:
                if edit_internal_candidate:
                    resume = edit_internal_candidate.resume
            contact = request.POST.get('contact-num')
            employee_id = request.POST.get('candidate_c_id')
            designation = request.POST.get('designation-input')
            notice = CandidateModels.NoticePeriod.objects.get(id=request.POST.get('professional-notice-period'))
            current_city = CandidateModels.City.objects.get(id=request.POST.get('candidate_current_city'))
            ctc = request.POST.get('ctc-input')
            expectedctc = request.POST.get('expected-ctc')
            total_exper = request.POST.get('professional-experience-year') +'.'+ request.POST.get(
                'professional-experience-month')
            # source=CandidateModels.Source.objects.get(id=request.POST.get('source'))

            models.InternalCandidateBasicDetails.objects.update_or_create(email=email,company_id = models.Company.objects.get(user_id=request.user.id),defaults={
                'user_id' : User.objects.get(id=request.user.id),
                'first_name' : fname,
                'last_name' : lname,
                'gender' : gender,
                'resume' : resume,
                'contact' : contact,
                'designation': designation,
                'notice' : notice,
                'ctc' : ctc,
                'current_city':current_city,
                'secure_resume':secure_resume,
                'expectedctc' : expectedctc,
                'total_exper' : total_exper,
                'update_at':datetime.datetime.now()
            })
            add_skill=models.InternalCandidateBasicDetails.objects.get(email=email,company_id = models.Company.objects.get(user_id=request.user.id))
            for i in request.POST.getlist('source'):
                if i.isnumeric():
                    main_source_obj = CandidateModels.Source.objects.get(id=i)
                    add_skill.source=main_source_obj
                else:
                    source_cre=CandidateModels.Source.objects.create(name=i)
                    add_skill.source=source_cre
            for i in request.POST.getlist('tags'):
                if i.isnumeric():
                    main_skill_obj = models.Tags.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                    add_skill.tags.add(main_skill_obj)
                else:
                    tag_cre=models.Tags.objects.create(name=i,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                    add_skill.tags.add(tag_cre)
            for i in request.POST.getlist('professional_skills'):
                if i.isnumeric():
                    main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                    add_skill.skills.add(main_skill_obj)
                else:
                    main_skill_obj=CandidateModels.Skill.objects.create(name=i)
                    add_skill.skills.add(main_skill_obj)
            for i in request.POST.getlist('candidate_search_city'):
                if i.isnumeric():
                    main_city_obj = CandidateModels.City.objects.get(id=i)
                    add_skill.prefered_city.add(main_city_obj)
            for i in request.POST.getlist('candidate_category'):
                if i.isnumeric():
                    main_categ_obj = models.CandidateCategories.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                    add_skill.categories.add(main_categ_obj)
            add_skill.save()
            if job_type=='company':
                job_obj=models.JobCreation.objects.get(id=request.POST.get('jobid'))
                password = get_random_string(length=12)
                if not User.objects.filter(email=email.lower()).exists():

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

                    usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
                                                    password=password, ip=ip, device_type=device_type,
                                                    browser_type=browser_type,
                                                    browser_version=browser_version, os_type=os_type,
                                                    os_version=os_version,
                                                    referral_number=generate_referral_code())

                    mail_subject = 'Activate your account'
                    current_site = get_current_site(request)
                    header=request.is_secure() and "https" or "http"
                    # print('domain----===========',current_site.domain)
                    html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                                                                                    'name': fname + ' ' + lname,
                                                                                    'email': email,
                                                                                    'domain': current_site.domain,
                                                                                    'password': password, 
                                                                                    'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id)
                                                                                    })
                    to_email = usr.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    # try:
                    msg.send()
                    add_skill.candidate_id = User.objects.get(email=email.lower())
                    add_skill.save()
                    add_candidate, create = CandidateModels.candidate_job_apply_detail.objects.update_or_create(
                        candidate_id=add_skill.candidate_id, defaults={
                            'gender': gender,
                            'resume': resume,
                            'contact': contact,
                            'designation': designation,
                            'notice': notice,
                            'ctc': ctc,
                            'expectedctc': expectedctc,
                            'total_exper': total_exper})

                    for i in add_candidate.skills.all():
                        print(type(int(i.id)))
                        main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                        add_candidate.skills.add(main_skill_obj.id)
                    for i in add_candidate.prefered_city.all():
                        main_city_obj = CandidateModels.City.objects.get(id=i.id)
                        add_candidate.prefered_city.add(main_city_obj.id)
                    add_candidate.save()
                else:
                    if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = add_skill.candidate_id).exists():
                        add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id =add_skill.candidate_id,defaults={
                                                                                        'gender' :gender,
                                                                                        'resume' : resume,
                                                                                        'contact' : contact,
                                                                                        'designation' : designation,
                                                                                        'notice' : notice,
                                                                                        'ctc' : ctc,
                                                                                        'expectedctc' : expectedctc,
                                                                                        'total_exper' :  total_exper})
                        for i in add_skill.skills.all():
                            print(type(int(i.id)))
                            main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                            add_candidate.skills.add(main_skill_obj.id)
                        for i in add_skill.prefered_city.all():
                            main_city_obj = CandidateModels.City.objects.get(id=i.id)
                            add_candidate.prefered_city.add(main_city_obj.id)
                        add_candidate.save()
                    toemail=[add_skill.candidate_id.email]
                    mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
                    html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
                    msg.attach_alternative(html_content, "text/html")
                    # try:
                    msg.send() 
                models.DailySubmission.objects.update_or_create(email=email,company_job_id=job_obj,internal_candidate_id_company=add_skill,company_id = models.Company.objects.get(user_id=request.user.id),defaults={
                    'candidate_id':User.objects.get(email=email),
                    'job_type':'company',
                    'internal_user_company' : models.Employee.objects.get(employee_id=User.objects.get(id=request.user.id)),
                    'first_name' : fname,
                    'last_name' : lname,
                    'gender' : gender,
                    'resume' : resume,
                    'contact' : contact,
                    'designation': designation,
                    'notice' : notice,
                    'ctc' : ctc,
                    'verify':verifydata,
                    'current_city':current_city,
                    'expectedctc' : expectedctc,
                    'total_exper' : total_exper,
                    'update_at':datetime.datetime.now()
                })
                add_deatil=models.DailySubmission.objects.get(email=email,company_job_id=job_obj,internal_candidate_id_company=add_skill,company_id = models.Company.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_deatil.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_deatil.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_deatil.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                        add_deatil.tags.add(tag_cre)
                for i in request.POST.getlist('professional_skills'):
                    if i.isnumeric():
                        main_skill_obj = CandidateModels.Skill.objects.get(id=i)
                        add_deatil.skills.add(main_skill_obj)
                    else:
                        main_skill_obj=CandidateModels.Skill.objects.create(name=i)
                        add_deatil.skills.add(main_skill_obj)
                for i in request.POST.getlist('candidate_search_city'):
                    if i.isnumeric():
                        main_city_obj = CandidateModels.City.objects.get(id=i)
                        add_deatil.prefered_city.add(main_city_obj)
                for i in request.POST.getlist('candidate_category'):
                    if i.isnumeric():
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,company_id=models.Company.objects.get(user_id=request.user.id))
                        add_deatil.categories.add(main_categ_obj)
                if not verifydata:
                    add_deatil.verified=True
                    add_deatil.applied=True
                add_deatil.save()
                if verifydata:  
                    mail_subject = '"Verify Detail" from Bidcruit'
                    current_site = get_current_site(request)
                    html_content = render_to_string('accounts/verify_detail.html', {'user': add_deatil,
                                                                                        'url':'candidate_verify',
                                                                                        'email': email,
                                                                                        'domain': current_site.domain,
                                                                                        'uid': urlsafe_base64_encode(
                                                                                            force_bytes(add_deatil.pk))})
                    to_email = add_deatil.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return redirect('company:daily_submission')
                else:
                    get_internalcandidate=models.InternalCandidateBasicDetails.objects.get(id=add_skill.id,company_id=models.Company.objects.get(user_id=request.user.id))
                    candidates_array = ''
                    job_obj = models.JobCreation.objects.get(id=request.POST.get('jobid'))
                    candidates = models.AppliedCandidate.objects.filter(job_id=job_obj)
                    candidates_array = [i.candidate.id for i in candidates]
                    agency_submit_candidate = models.AssociateCandidateAgency.objects.filter(job_id=job_obj).values_list(
                        'candidate_id', flat=True)
                    candidates_array = list(chain(candidates_array, agency_submit_candidate))
                    if get_internalcandidate.candidate_id==None or not get_internalcandidate.candidate_id.id in candidates_array:
                        fname = get_internalcandidate.first_name
                        lname = get_internalcandidate.last_name
                        email = get_internalcandidate.email
                        gender = get_internalcandidate.gender
                        resume = get_internalcandidate.resume
                        contact = get_internalcandidate.contact
                        designation = get_internalcandidate.designation
                        notice = CandidateModels.NoticePeriod.objects.get(id=get_internalcandidate.notice.id)
                        ctc = get_internalcandidate.ctc
                        expectedctc = get_internalcandidate.expectedctc
                        current_city = CandidateModels.City.objects.get(id=get_internalcandidate.current_city.id)
                        total_exper = get_internalcandidate.total_exper
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
                        print('============\n\n')
                        current_site = get_current_site(request)
                        header=request.is_secure() and "https" or "http"
                        # if not User.objects.filter(email=email.lower()).exists():
                        #     print('============created')
                        #     usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
                        #                                         password=password, ip=ip, device_type=device_type,
                        #                                         browser_type=browser_type,
                        #                                         browser_version=browser_version, os_type=os_type,
                        #                                         os_version=os_version,
                        #                                         referral_number=generate_referral_code())
                        #     mail_subject = 'Activate your account'
                        #     current_site = get_current_site(request)
                        #     # print('domain----===========',current_site.domain)
                        #     html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
                        #                                                                         'name': fname + ' ' + lname,
                        #                                                                         'email': email,
                        #                                                                         'domain': current_site.domain,
                        #                                                                         'password': password,
                        #                                                                         'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id) })
                        #     to_email = usr.email
                        #     from_email = settings.EMAIL_HOST_USER
                        #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        #     msg.attach_alternative(html_content, "text/html")
                        #     # try:
                        #     msg.send()
                        #     get_internalcandidate.candidate_id = User.objects.get(email=email.lower())
                        #     get_internalcandidate.save()
                        #     add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                        #                                                                         'gender' :gender,
                        #                                                                         'resume' : resume,
                        #                                                                         'contact' : contact,
                        #                                                                         'designation' : designation,
                        #                                                                         'notice' : notice,
                        #                                                                         'ctc' : ctc,
                        #                                                                         'expectedctc' : expectedctc,
                        #                                                                         'total_exper' :  total_exper})

                        #     for i in get_internalcandidate.skills.all():
                        #         print(type(int(i.id)))
                        #         main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                        #         add_candidate.skills.add(main_skill_obj.id)
                        #     for i in get_internalcandidate.prefered_city.all():
                        #         main_city_obj = CandidateModels.City.objects.get(id=i.id)
                        #         add_candidate.prefered_city.add(main_city_obj.id)
                        #     add_candidate.save()
                        # else:

                        #     if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = User.objects.get(email=email.lower())).exists():
                        #         add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id = User.objects.get(email=email.lower()),defaults={
                        #                                                                         'gender' :gender,
                        #                                                                         'resume' : resume,
                        #                                                                         'contact' : contact,
                        #                                                                         'designation' : designation,
                        #                                                                         'notice' : notice,
                        #                                                                         'ctc' : ctc,
                        #                                                                         'expectedctc' : expectedctc,
                        #                                                                         'total_exper' :  total_exper})
                        #         for i in get_internalcandidate.skills.all():
                        #             print(type(int(i.id)))
                        #             main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                        #             add_candidate.skills.add(main_skill_obj.id)
                        #         for i in get_internalcandidate.prefered_city.all():
                        #             main_city_obj = CandidateModels.City.objects.get(id=i.id)
                        #             add_candidate.prefered_city.add(main_city_obj.id)
                        #         add_candidate.save()
                        #     toemail=[email]
                        #     mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
                        #     html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
                        #     from_email = settings.EMAIL_HOST_USER
                        #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
                        #     msg.attach_alternative(html_content, "text/html")
                        #     # try:
                        #     msg.send()  
                        current_site = get_current_site(request)
                        header=request.is_secure() and "https" or "http"  
                        associate_job_list=[request.POST.get('jobid')]
                        for joblist_id in associate_job_list:
                            job_obj=models.JobCreation.objects.get(id=int(joblist_id))
                            notify.send(request.user, recipient=User.objects.get(email=email.lower()), verb="Application",
                                        description="You have succesfully applied for the Job "+str(job_obj.job_title)+".",image="/static/notifications/icon/company/Job_Create.png",
                                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                            job_obj.id)+"/company")
                            # fit_score(add_candidate,job_obj)
                            # agencyid= models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
                            models.AssociateCandidateInternal.objects.update_or_create(company_id=job_obj.company_id,job_id=models.JobCreation.objects.get(id=int(joblist_id)),candidate_id=User.objects.get(email=email.lower()),defaults={
                                    'internal_candidate_id':models.InternalCandidateBasicDetails.objects.get(id=add_skill.id)
                                })
                            models.AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,job_id=job_obj,dailysubmission=add_deatil,candidate=User.objects.get(email=email.lower()),defaults={
                            'user_id':User.objects.get(id=request.user.id),'submit_type':'Company'
                            })
                            workflow = models.JobWorkflow.objects.get(job_id=job_obj)
                            currentcompleted=False
                            current_stage=None
                            next_stage = None
                            next_stage_sequance=0
                            # onthego change
                            if workflow.withworkflow:
                                print("==========================withworkflow================================")
                                workflow_stages = models.WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
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
                                            stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
                                            current_stage = stage_list_obj
                                            next_stage_sequance=stage.sequence_number+1
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                    candidate_id=User.objects.get(email=email.lower()),
                                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                                    sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                                            sequence_number = stage.sequence_number + 1
                                            status = 0
                                        else:
                                            status = 0
                                            sequence_number = stage.sequence_number + 1
                                            next_stage = stage.stage
                                        models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
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
                                        models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                                job_id=job_obj, stage=stage.stage,
                                                                                template=stage.template,
                                                                                sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
                            if workflow.onthego:
                                print("==========================onthego================================")
                                onthego_stages = models.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

                                if workflow.is_application_review:
                                    for stage in onthego_stages:
                                        if stage.sequence_number == 1:
                                            status = 2
                                            sequence_number = stage.sequence_number
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                    candidate_id=User.objects.get(email=email.lower()),
                                                                                    job_id=job_obj, stage=stage.stage,
                                                                                    template=stage.template,
                                                                                    sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                                            status = 1
                                            sequence_number = stage.sequence_number + 1
                                            stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
                                            current_stage = stage_list_obj
                                            next_stage_sequance=stage.sequence_number+1
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                    candidate_id=User.objects.get(email=email.lower()),
                                                                                    job_id=job_obj, stage=stage_list_obj,
                                                                                    sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                                        else:
                                            status = 0
                                            sequence_number = stage.sequence_number + 1
                                            current_stage = stage_list_obj
                                            models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
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
                                        models.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                                job_id=job_obj, stage=stage.stage,
                                                                                template=stage.template,
                                                                                sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
                            action_required=''
                            if next_stage_sequance!=0:
                                if models.CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                                                candidate_id=User.objects.get(email=email.lower()),
                                                                                job_id=job_obj,
                                                                                sequence_number=next_stage_sequance).exists():
                                    next_stage=models.CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
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
                                models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=User.objects.get(email=email.lower()),company_id=job_obj.company_id,defaults={
                                                                        'current_stage':current_stage,'next_stage':next_stage,
                                                                        'action_required':action_required,'update_at':datetime.datetime.now()})
                            assign_job_internal = list(
                                models.CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
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
                            job_assign_recruiter = models.CompanyAssignJob.objects.filter(job_id=job_obj)
                            description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
                            to_email=[]
                            to_email.append(job_obj.contact_name.email)
                            to_email.append(job_obj.job_owner.email)
                            if job_obj.contact_name.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission",
                                                                                            description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                                            target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                                job_obj.id))
                            if job_obj.job_owner.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission",
                                                                                            description=description,image="/static/notifications/icon/company/Candidate_submission.png",
                                                                                            target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                                job_obj.id))
                            all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                            for i in all_assign_users:
                                if i.recruiter_type_internal:
                                    to_email.append(i.recruiter_id.email)
                                    if i.recruiter_id.id != request.user.id:
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
                                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Interview schedule",
                                                                                                    description=description,image="/static/notifications/icon/company/interview.png",
                                                                                                    target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                                        job_obj.id))
                                elif current_stage.name=='Application Review':
                                    stage_detail='Application Review'
                                    description="You have one application to review for the job "+job_obj.job_title
                                    for i in all_assign_users:
                                        if i.recruiter_type_internal:
                                            if i.recruiter_id.id != request.user.id:
                                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission",
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
                return redirect('company:daily_submission')
        return render(request,'company/ATS/add_candidate_basic_form.html',context)
    else:
        return redirect('company:add_edit_profile')


def tastcategory_add_or_update_view(request):
    context = {}
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        # context['Add'] = False
        # context['Edit'] = False
        # context['Delete'] = False
        # context['permission'] = check_permission(request)
        # for permissions in context['permission']:
        #     if permissions.permissionsmodel.modelname == 'Department':
        #         print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
        #         if permissions.permissionname == 'Add':
        #             context['Add'] = True
        #         if permissions.permissionname == 'Edit':
        #             context['Edit'] = True
        #         if permissions.permissionname == 'Delete':
        #             context['Delete'] = True
        # if context['Add'] or context['Edit'] or context['Delete']:
        context['categories'] = models.TaskCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        if request.method == "POST":
            id= request.POST.get("category_id")
            category_name = request.POST.get("category_name")
            color = request.POST.get("color")
            data = {}
            if id == "null":
                category = models.TaskCategories.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),category_name=category_name,color=color)
                operation = "created"
                role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                get_admin = models.Employee.objects.filter(role=role_id_get,
                                                                        company_id=models.Company.objects.get(
                                                                            user_id=request.user)).values_list(
                    'employee_id', flat=True)
                    
                for i in get_admin:
                    description = request.user.first_name + "Add Categories"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Add Categories",
                                    description=description,
                                    target_url="#")
            else:
                category = models.TaskCategories.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=int(id))
                category.category_name = category_name
                category.color = color
                category.save()
                operation = "update"
                role_id_get = models.Role.objects.get(company_id=models.Company.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                get_admin = models.Employee.objects.filter(role=role_id_get,
                                                                        company_id=models.Company.objects.get(
                                                                            user_id=request.user)).values_list(
                    'employee_id', flat=True)
                for i in get_admin:
                    description = request.user.first_name + "Update category"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Update category",
                                    description=description,
                                    target_url="#")
            # if
            data['operation'] = operation
            data['category_name'] =category.category_name
            data['category_id'] =category.id
            return HttpResponse(json.dumps(data))
        return render(request,"company/ATS/add_task_category.html",context)
    else:
        return redirect('company:add_edit_profile')

def delete_taskcategory(request):
    dept_id = request.POST.get("category_id")
    category = models.TaskCategories.objects.get(company_id=models.Company.objects.get(user_id=request.user.id),id=int(dept_id))
    category.delete()
    return HttpResponse("true")



def get_task_category(request):
    if request.method == 'POST':
        category_id = request.POST.get("category_id")
        category_get = models.TaskCategories.objects.get(id=int(category_id),
            company_id=models.Company.objects.get(user_id=request.user.id))
        print("============------", category_get)
        data = {}
        data['status'] = True
        data['category_name'] = category_get.category_name
        data['category_id'] = category_get.id
        data['color'] = category_get.color
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)


def task_managment(request):
    context={}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    context['profile']=check_profile(models.Company.objects.get(user_id=request.user.id))
    if check_profile(models.Company.objects.get(user_id=request.user.id)):
        context['taskmanagment']=models.TaskManagment.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['tastcategory']=models.TaskCategories.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['openingjobs']=models.JobCreation.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),is_publish=True,close_job=False)
        context['internalcandidates']=models.InternalCandidateBasicDetails.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['internalemployees']=models.Employee.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
        context['taskststuses']=CandidateModels.TastStatus.objects.all()
        context['priorities']=CandidateModels.Priority.objects.all()
        job_obj=None
        internal_candidate_id=None
        applied_candidate_id=None
        if request.method=='POST':
            if request.POST.get('task_id'):
                if request.POST.get('jobid'):
                    job_obj=models.JobCreation.objects.get(id=request.POST.get('jobid'),company_id=models.Company.objects.get(user_id=request.user.id))
                if request.POST.get('candidate'):
                    candidatetype=request.POST.get('candidate').split('-')
                    if candidatetype[0]=='internal':
                        internal_candidate_id=models.InternalCandidateBasicDetails.objects.get(id=candidatetype[1],company_id=models.Company.objects.get(user_id=request.user.id))
                    if candidatetype[0]=='applied':
                        applied_candidate_id=User.objects.get(id=candidatetype[1])
                tastcreate=models.TaskManagment.objects.get(id=request.POST.get('task_id'),company_id=models.Company.objects.get(user_id=request.user.id))
                tastcreate.user_id=User.objects.get(id=request.user.id)
                tastcreate.title=request.POST.get('edit-title')
                # tastcreate.priority_id=CandidateModels.Priority.objects.get(id=request.POST.get('edit_select_priority'))
                tastcreate.description=request.POST.get('edit_description')
                tastcreate.category_id=models.TaskCategories.objects.get(id=request.POST.get('edit_category'))
                tastcreate.job_id=job_obj
                tastcreate.applied_candidate_id=applied_candidate_id
                tastcreate.internal_candidate_id=internal_candidate_id
                tastcreate.owner=models.Employee.objects.get(id=request.POST.get('edit_owner'))
                tastcreate.status=CandidateModels.TastStatus.objects.all()[0]
                tastcreate.due_date=request.POST.get('edit_due_date')
                tastcreate.assignee.clear()
                for i in request.POST.getlist('edit_assign'):
                    assign = models.Employee.objects.get(id=i)
                    tastcreate.assignee.add(assign)
                tastcreate.save()
            else:
                if request.POST.get('edit_jobid'):
                    job_obj=models.JobCreation.objects.get(id=request.POST.get('jobid'),company_id=models.Company.objects.get(user_id=request.user.id))
                if request.POST.get('edit_candidate'):
                    candidatetype=request.POST.get('edit_candidate').split('-')
                    if candidatetype[0]=='internal':
                        internal_candidate_id=models.InternalCandidateBasicDetails.objects.get(id=candidatetype[1],company_id=models.Company.objects.get(user_id=request.user.id))
                    if candidatetype[0]=='applied':
                        applied_candidate_id=User.objects.get(id=candidatetype[1])
                tastcreate=models.TaskManagment.objects.create(company_id=models.Company.objects.get(user_id=request.user.id),
                    user_id=User.objects.get(id=request.user.id),
                    title=request.POST.get('title'),
                    priority_id=CandidateModels.Priority.objects.get(id=request.POST.get('select_priority')),
                    description=request.POST.get('description'),
                    category_id=models.TaskCategories.objects.get(id=request.POST.get('category')),
                    job_id=job_obj,
                    applied_candidate_id=applied_candidate_id,
                    internal_candidate_id=internal_candidate_id,
                    owner=models.Employee.objects.get(id=request.POST.get('owner')),
                    status=CandidateModels.TastStatus.objects.all()[0],
                    due_date=request.POST.get('due_date')
                )
                tastcreate.assignee.clear()
                for i in request.POST.getlist('assignee'):
                    assign = models.Employee.objects.get(id=i)
                    tastcreate.assignee.add(assign)
                tastcreate.save()
        return render(request,'company/ATS/task-manager.html',context)
    else:
        return redirect('company:add_edit_profile')


def get_task(request):
    if request.method == 'POST':
        task_id = request.POST.get("task_id")
        task_get = models.TaskManagment.objects.get(id=int(task_id),company_id=models.Company.objects.get(user_id=request.user.id))
        data = {}
        if request.POST.get("tasktype")=='taskget':
            data['status'] = True
            data['title'] = task_get.title
            data['assignee']=[assign.employee_id.first_name+' '+assign.employee_id.last_name for assign in task_get.assignee.all()]
            data['priority'] = task_get.priority_id.name
            data['description'] = task_get.description
            data['category'] = task_get.category_id.category_name
            data['category_color'] = task_get.category_id.color
            if task_get.job_id:
                data['job'] = task_get.job_id.job_title
            else:
                data['job']=None
            if task_get.applied_candidate_id:
                data['applied_candidate'] = task_get.applied_candidate_id.first_name+' '+task_get.applied_candidate_id.last_name
            else:
                data['applied_candidate'] = None
            if task_get.internal_candidate_id:
                data['internal_candidate'] = task_get.internal_candidate_id.first_name+' '+task_get.internal_candidate_id.last_name
            else:
                data['internal_candidate'] = None
            data['owner']=task_get.owner.employee_id.first_name+' '+task_get.owner.employee_id.last_name
            data['due_date']=task_get.due_date
        if request.POST.get("tasktype")=='taskedit':
            data['status'] = True
            data['taskid']=task_get.id
            data['title'] = task_get.title
            data['assignee']=[assign.id for assign in task_get.assignee.all()]
            data['priority'] = task_get.priority_id.id
            data['description'] = task_get.description
            data['category'] = task_get.category_id.id
            if task_get.job_id:
                data['job'] = task_get.job_id.id
                if task_get.applied_candidate_id:
                    applied_candidate=models.DailySubmission.objects.filter(company_job_id=task_get.job_id,company_id=models.Company.objects.get(user_id=request.user.id))
                    appliedcandidate_list=[]
                    if applied_candidate:
                        for candidate in applied_candidate:
                            appliedcandidate_list.append({'id':'applied-'+str(candidate.candidate_id.id),'name':candidate.first_name+' '+candidate.last_name})
                    data['candidates']=appliedcandidate_list
                    data['applied_candidate'] = task_get.applied_candidate_id.id
                else:
                    data['applied_candidate'] = None
            else:
                data['job']=None
                internalcandidates=models.InternalCandidateBasicDetails.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id))
                internalcandidate_list=[]
                if internalcandidates:
                    for candidate in internalcandidates:
                        internalcandidate_list.append({'id':'internal-'+str(candidate.candidate_id.id),'name':candidate.first_name+' '+candidate.last_name})
                data['candidates']=internalcandidate_list
                if task_get.internal_candidate_id:
                    data['internal_candidate'] = task_get.internal_candidate_idid
                else:
                    data['internal_candidate'] = None
            data['owner']=task_get.owner.id
            data['due_date']=task_get.due_date
        return JsonResponse(data)

    else:
        return HttpResponse(False)



def get_applied_candidate(request):
    if request.method == 'POST':
        job_id = request.POST.get("job_id")
        data=[]
        applied_candidate=models.DailySubmission.objects.filter(company_job_id=models.JobCreation.objects.get(id=job_id),company_id=models.Company.objects.get(user_id=request.user.id))
        if applied_candidate:
            for candidate in applied_candidate:
                data.append({'id':'applied-'+str(candidate.candidate_id.id),'name':candidate.first_name+' '+candidate.last_name})
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)