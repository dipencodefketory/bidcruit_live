from bidcruit import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.tokens import account_activation_token
from django.core.mail import EmailMessage, BadHeaderError, EmailMultiAlternatives
from . import models
from accounts.views import activate_account_confirmation
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, request
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.encoding import force_bytes
from company.models import CandidateHire, CompanyProfile,Company
from company import models as CompanyModels
from candidate import models as CandidateModels
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from itertools import chain
# from candidate.views import fit_score
import re
from datetime import datetime
import datetime
from django.core import serializers
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)

import agency
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from smtplib import SMTPException
import json
from django.http.response import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.utils.crypto import get_random_string
import base64
from django.http import HttpResponseRedirect
import random
import string
from smtplib import SMTPException
from notifications.signals import notify
from chat import models as ChatModels
import pdfkit
from .agencyfilters import JobFilter,CandidateFilter

def agencytype(agencyid):
    if models.AgencyType.objects.filter(agency_id=agencyid).exists():
        agencytype=models.AgencyType.objects.get(agency_id=agencyid)
        return agencytype.is_agency
    else:
        return False

def checkprofile(agencyid):
    get_agency=models.AgencyType.objects.get(agency_id=agencyid)
    if get_agency.is_freelancer:
        if models.FreelancerProfile.objects.filter(agency_id=agencyid).exists():
            return True
        else:
            return False
    elif get_agency.is_agency:
        if models.AgencyProfile.objects.filter(agency_id=agencyid).exists():
            return True
        else:
            return False
# permission
def check_permission(request):
    emp=models.InternalUserProfile.objects.get(InternalUserid=request.user)
    role_data=models.RolePermissions.objects.get(role=emp.role,agency_id=models.Agency.objects.get(user_id=request.user))
    return role_data.permission.order_by('permissionsmodel_id')

def get_tags(request):
    term = request.GET.get('term')
    tags = models.Tags.objects.filter(name__istartswith=term,agency_id=models.Agency.objects.get(user_id=request.user.id))
    tags_list = []
    for i in tags:
        data = {}
        data['id'] = i.id
        data['name'] = i.name
        tags_list.append(data)
    return JsonResponse(tags_list, safe=False)

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

def agency_type(request):
    if request.method == 'POST':
        pageName = json.loads(request.body.decode('UTF-8'))
        if(pageName['data']=='signup-freelancer'):
            print("=========")
            return render(request,'agency/signup-freelancer.html')
        elif(pageName['data']=='signup-agency'):
            return render(request,'agency/signup-agency.html')
    return render(request,'agency/sign-up.html')
def signup_freelancer(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
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
            if User.objects.filter(email=request.POST['email']).exists():
                messages.error(request, 'User Already Exists.')
                return render(request, 'agency/agency_registration.html')
            else:
                usr = User.objects.create_agency_freelancer(first_name=fname, last_name=lname,email=email.lower(),password=password,
                                                 ip=ip, device_type=device_type,browser_type=browser_type,
                                                 browser_version=browser_version, os_type=os_type,os_version=os_version)
                mail_subject = 'Activate your account.'
                current_site = get_current_site(request)
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
                # try:
                msg.send()
                agencyid=models.Agency.objects.create(agency_id=User.objects.get(email=email.lower()))
                models.CandidateCategories.objects.create(category_name='Unassigned',agency_id=agencyid,user_id=User.objects.get(email=email.lower()))
                agencyid.user_id.add(User.objects.get(email=email.lower()))
                models.AgencyType.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),defaults={'is_freelancer':True})
                department=models.Department.objects.create(name="Admin",system_generated = True,user_id=User.objects.get(email=email.lower()),agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),status=True)
                role_create = models.Role.objects.create(name='SuperAdmin', system_generated = True, status=True, agency_id=agencyid,
                                                         user_id=usr)
                permissions = models.RolePermissions.objects.create(role=role_create,system_generated = True, agency_id=agencyid,
                                                                    user_id=usr)
                get_permissionmodel = CandidateModels.PermissionsModel.objects.filter(is_agency=True).values_list('id')
                for per_id in CandidateModels.Permissions.objects.filter(permissionsmodel__in=get_permissionmodel):
                    permissions.permission.add(per_id)
                models.InternalUserProfile.objects.create(InternalUserid=User.objects.get(email=email.lower()),
                                                            user_id=User.objects.get(email=email.lower()),
                                                            role=role_create,unique_id=create_employee_id(),
                                                            contact_number='0000000000',gender='',branch='',
                                                            total_experiance=0,spaciility='',agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())))
                api_subjects = CandidateModels.CodingApiSubjects.objects.filter(status=True)
                for subject in api_subjects:
                    created_sub = models.CodingSubject.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),api_subject_id=subject,type='backend')
                    models.CodingSubjectCategory.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),subject_id=created_sub,category_name=subject.name)

                front_sub = models.CodingSubject.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),type='frontend')
                models.CodingSubjectCategory.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())), subject_id=front_sub,
                                                            category_name='Html/css/js')
                    # return redirect('accounts:signin')
                # except BadHeaderError:
                #     User.objects.get(email__exact=email).delete()
                #     messages.error(request, 'Invalid header found.')
                #     return render(request, 'agency/signup-freelancer.html')
                # except SMTPException as e:
                #     User.objects.get(email__exact=email).delete()
                #     messages.error(request, e)
                #     return render(request, 'agency/signup-freelancer.html')
                # except:
                #     User.objects.get(email__exact=email).delete()
                #     messages.error(request, 'Mail sending failed, Please check your internet connection !!')
                #     return render(request, 'agency/signup-freelancer.html')
                return activate_account_confirmation(request, fname +' '+lname , email)
    return render(request,'agency/signup-freelancer.html')



def signup_agency(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            company_name = request.POST.get('company_name')
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
            if User.objects.filter(email=request.POST['email'].lower()).exists():
                messages.error(request, 'User Already Exists.')
                return render(request, 'agency/agency_registration.html')
            else:
                usr = User.objects.create_agency(company_name=company_name, website=website,email=email.lower(),password=password,
                                                 ip=ip, device_type=device_type,browser_type=browser_type,
                                                 browser_version=browser_version, os_type=os_type,os_version=os_version)
                
                mail_subject = 'Activate your account.'
                current_site = get_current_site(request)
                html_content = render_to_string('accounts/acc_active_email.html', {'user': usr,
                                                                                   'name': company_name,
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
                # try:
                msg.send()
                agencyid=models.Agency.objects.create(agency_id=User.objects.get(email=email.lower()))
                agencyid.user_id.add(User.objects.get(email=email.lower()))
                models.CandidateCategories.objects.create(category_name='Unassigned',agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),user_id=User.objects.get(email=email.lower()))
                role_create = models.Role.objects.create(name='SuperAdmin',system_generated = True, status=True, agency_id=agencyid,
                                                         user_id=usr)
                permissions = models.RolePermissions.objects.create(role=role_create,system_generated = True, agency_id=agencyid,
                                                                    user_id=usr)
                get_permissionmodel = CandidateModels.PermissionsModel.objects.filter(is_agency=True).values_list('id')
                for per_id in CandidateModels.Permissions.objects.filter(permissionsmodel__in=get_permissionmodel):
                    permissions.permission.add(per_id)
                department=models.Department.objects.create(name="Admin",system_generated = True,user_id=User.objects.get(email=email.lower()),agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),status=True)
                models.AgencyType.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),defaults={'is_agency':True})
                models.InternalUserProfile.objects.create(InternalUserid=User.objects.get(email=email.lower()),
                                                            user_id=User.objects.get(email=email.lower()),
                                                            role=role_create,unique_id=create_employee_id(),
                                                            department=department,
                                                            contact_number='0000000000',gender='',branch='',
                                                            total_experiance=0,spaciility='',agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())))
                api_subjects = CandidateModels.CodingApiSubjects.objects.filter(status=True)
                for subject in api_subjects:
                    created_sub = models.CodingSubject.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),api_subject_id=subject,type='backend')
                    models.CodingSubjectCategory.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),subject_id=created_sub,category_name=subject.name)

                front_sub = models.CodingSubject.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())),type='frontend')
                models.CodingSubjectCategory.objects.create(agency_id=models.Agency.objects.get(user_id=User.objects.get(email=email.lower())), subject_id=front_sub,
                                                            category_name='Html/css/js')
                # return redirect('accounts:signin')
                # except BadHeaderError:
                #     User.objects.get(email__exact=email).delete()
                #     messages.error(request, 'Invalid header found.')
                #     return render(request, 'agency/signup-agency.html')
                # except SMTPException as e:
                #     User.objects.get(email__exact=email).delete()
                #     messages.error(request, e)
                #     return render(request, 'agency/signup-agency.html')
                # except:
                #     User.objects.get(email__exact=email).delete()
                #     messages.error(request, 'Mail sending failed, Please check your internet connection !!')
                #     return render(request, 'agency/signup-agency.html')
                return activate_account_confirmation(request, company_name, email)
    return render(request,'agency/signup-agency.html')


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def change_password(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        context['form']=form
        return render(request, 'agency/ATS/change-password.html',context)
    else:
        return redirect('agency:agency_profile')

@login_required(login_url="/")
def agency_Profile(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['country'] = CandidateModels.Country.objects.all()
    if request.user.is_agency:
        get_agency=models.AgencyType.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
        if get_agency.is_freelancer:
            if models.FreelancerProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
                get_profile=models.FreelancerProfile.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
                get_internalcandidate = models.InternalCandidateBasicDetail.objects.filter(
                    agency_id=models.Agency.objects.get(user_id=request.user.id))
                completed_job=CompanyModels.AssignExternal.objects.filter(recruiter_id=models.Agency.objects.get(user_id=request.user.id))
                context['get_profile']=get_profile
                context['completed_job']=len(completed_job)
                context['get_internalcandidate']=len(get_internalcandidate)
                return render(request, 'agency/ATS/agency-profile-view.html',context)
            else:
                if request.method=='POST':
                    contact_no=request.POST.get('contact_no')
                    logo=request.FILES.get('logo')
                    background_image=request.FILES.get('bgimg')
                    print(request.POST.getlist('specialties'))
                    speciality=request.POST.getlist('specialties')
                    gender=request.POST.get('gender')
                    aboutus=request.POST.get('about_us')
                    profile, created=models.FreelancerProfile.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),defaults={
                                            'user_id':User.objects.get(id=request.user.id),
                                            'agency_logo' : logo,
                                            'agency_bg' : background_image,
                                            'speciality' : ', '.join(speciality),
                                            'gender':gender,
                                            'aboutus' : aboutus,
                                            'contact_no' : contact_no,})
                    models.InternalUserProfile.objects.update_or_create(
                        agency_id=models.Agency.objects.get(user_id=request.user.id), defaults={
                            'user_id': User.objects.get(id=request.user.id),
                            'agency_logo': logo,
                            'agency_bg': background_image,
                            'spaciility': ', '.join(speciality),
                            'aboutus': aboutus,
                            'contact_no': contact_no, })
                    if models.FreelancerProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
                        get_profile=models.FreelancerProfile.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
                        context['get_profile']=get_profile
                        return render(request, 'agency/ATS//agency-profile-view.html',context)
            return render(request,'agency/ATS//agency_profile_freelancer.html',context)
        if get_agency.is_agency:
            context['companysize']=models.AgencyProfile.employee_count_choices
            context['companytypechoices']=models.AgencyProfile.agency_type_choices
            context['agency_industrytype']=CandidateModels.IndustryType.objects.all()
            
            if models.AgencyProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
                get_profile=models.AgencyProfile.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
                get_internalcandidate = models.InternalCandidateBasicDetail.objects.filter(
                    agency_id=models.Agency.objects.get(user_id=request.user.id))
                completed_job=CompanyModels.AssignExternal.objects.filter(recruiter_id=models.Agency.objects.get(user_id=request.user.id))
                context['get_profile']=get_profile
                context['completed_job']=len(completed_job)
                context['get_internalcandidate']=len(get_internalcandidate)
                return render(request, 'agency/ATS/agency-profile-view.html',context)
            else:
                if request.method=='POST':
                    admin_add=User.objects.get(id=request.user.id)
                    admin_add.first_name=request.POST.get('f_name')
                    admin_add.last_name=request.POST.get('l_name')
                    admin_add.save()
                    getinternaluser=models.InternalUserProfile.objects.get(InternalUserid=User.objects.get(id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)))
                    getinternaluser.contact_number=request.POST.get('contact_num')
                    getinternaluser.gender=request.POST.get('gender')
                    getinternaluser.branch=request.POST.get('branch')
                    getinternaluser.total_experiance=request.POST.get('professional_experience_year')+'.'+request.POST.get('professional_experience_month')
                    getinternaluser.spaciility=', '.join(request.POST.getlist('admin_specialities'))
                    asd=request.POST.get('admin_about_profile_details')
                    getinternaluser.aboutus=request.POST.get('admin_about_profile_details')
                    getinternaluser.save()
                    contact_email=request.POST.get('basic_email')
                    contact_no=request.POST.get('contact_no')
                    logo=request.FILES.get('logo')
                    background_image=request.FILES.get('bgimg')
                    speciality=request.POST.getlist('company_specialities')
                    aboutus=request.POST.get('company_about_profile_details')
                    address=request.POST.get('address_detail')
                    founded_year=request.POST.get('founded_year')
                    industry_type=request.POST.get('industrytype')
                    domain_expertise=request.POST.getlist('domain_expertise')
                    agency_profile_type=request.POST.get('agency_profile_type')
                    employee_count=request.POST.get('company_size')
                    country = request.POST.get('country')
                    state = request.POST.get('state')
                    city = request.POST.get('city')
                    profile, created=models.AgencyProfile.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),defaults={
                                            'user_id':User.objects.get(id=request.user.id),
                                            'agency_profile_type': agency_profile_type,
                                            'agency_logo' : logo,
                                            'agency_bg' : background_image,
                                            'speciality': ', '.join(speciality),
                                            'domain_expertise':', '.join(domain_expertise),
                                            'industry_type':CandidateModels.IndustryType.objects.get(id=int(industry_type)),
                                            'aboutus' : aboutus,
                                            'address' : address,
                                            'country': CandidateModels.Country.objects.get(id=country),
                                            'state': CandidateModels.State.objects.get(id=state),
                                            'city': CandidateModels.City.objects.get(id=city),
                                            'contact_email' : contact_email,
                                            'contact_no' : contact_no,
                                            'founded_year' : founded_year,
                                            'employee_count' : employee_count})
                    if models.AgencyProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
                        get_profile=models.AgencyProfile.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
                        get_internalcandidate = models.InternalCandidateBasicDetail.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
                        completed_job=CompanyModels.AssignExternal.objects.filter(recruiter_id=models.Agency.objects.get(user_id=request.user.id))
                        context['get_profile']=get_profile
                        context['completed_job']=len(completed_job)
                        context['get_internalcandidate']=len(get_internalcandidate)
                        return render(request, 'agency/ATS//agency-profile-view.html',context)
            return render(request, 'agency/ATS/agency_profile_add.html',context)
    else:
        return redirect('accounts:signin')


def agency_profile_update(request,id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['country'] = CandidateModels.Country.objects.all()
        get_agency = models.AgencyType.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
        if get_agency.is_freelancer:
            context['get_profile'] = models.FreelancerProfile.objects.get(id=id, agency_id=models.Agency.objects.get(
                user_id=request.user.id))
            context['internal_profile'] = models.InternalUserProfile.objects.get(agency_id=models.Agency.objects.get(
                user_id=request.user.id))
            if request.method == 'POST':
                contact_no = request.POST.get('contact_no')
                gender=request.POST.get('gender')
                if request.FILES.get('logo'):
                    logo =request.FILES.get('logo')
                else:
                    logo = context['get_profile'].agency_logo
                if request.FILES.get('bgimg'):
                    background_image = request.FILES.get('bgimg')
                else:
                    background_image = context['get_profile'].agency_bg
                speciality = request.POST.getlist('specialties')
                aboutus = request.POST.get('about_us')
                profile, created = models.FreelancerProfile.objects.update_or_create(
                    agency_id=models.Agency.objects.get(user_id=request.user.id), defaults={
                        'user_id': User.objects.get(id=request.user.id),
                        'agency_logo': logo,
                        'agency_bg': background_image,
                        'speciality': ', '.join(speciality),
                        'aboutus': aboutus,
                        'contact_no': contact_no, })
                models.InternalUserProfile.objects.update_or_create(
                    agency_id=models.Agency.objects.get(user_id=request.user.id), defaults={
                        'user_id': User.objects.get(id=request.user.id),
                        'gender':gender,
                        'spaciility': ', '.join(speciality),
                        'aboutus': aboutus,
                        'contact_no': contact_no, })
                return redirect('agency:agency_Profile')
            return render(request, 'agency/ATS//agency_profile_freelancer.html',context)
        if get_agency.is_agency:
            context['companysize'] = models.AgencyProfile.employee_count_choices
            context['companytypechoices'] = models.AgencyProfile.agency_type_choices
            context['agency_industrytype'] = CandidateModels.IndustryType.objects.all()

            context['get_profile'] = models.AgencyProfile.objects.get(id=id,agency_id=models.Agency.objects.get(user_id=request.user.id))
            if request.method == 'POST':
                contact_email = request.POST.get('basic_email')
                contact_no = request.POST.get('contact_no')
                if request.FILES.get('logo'):
                    logo =request.FILES.get('logo')
                else:
                    logo = context['get_profile'].agency_logo
                if request.FILES.get('bgimg'):
                    background_image = request.FILES.get('bgimg')
                else:
                    background_image = context['get_profile'].agency_bg
                speciality = request.POST.getlist('specialties')
                aboutus = request.POST.get('company_about_profile_details')
                address = request.POST.get('address_detail')
                founded_year = request.POST.get('founded_year')
                industry_type = request.POST.get('industrytype')
                domain_expertise=request.POST.getlist('domain_expertise')
                agency_profile_type = request.POST.get('agency_profile_type')
                employee_count = request.POST.get('company_size')
                country = request.POST.get('country')
                state = request.POST.get('state')
                city = request.POST.get('city')
                profile, created = models.AgencyProfile.objects.update_or_create(
                    agency_id=models.Agency.objects.get(user_id=request.user.id), defaults={
                        'user_id': User.objects.get(id=request.user.id),
                        'agency_profile_type': agency_profile_type,
                        'agency_logo': logo,
                        'agency_bg': background_image,
                        'speciality': ', '.join(speciality),
                        'domain_expertise':', '.join(domain_expertise),
                        'industry_type': CandidateModels.IndustryType.objects.get(id=int(industry_type)),
                        'aboutus': aboutus,
                        'address': address,
                        'country': CandidateModels.Country.objects.get(id=country),
                        'state': CandidateModels.State.objects.get(id=state),
                        'city': CandidateModels.City.objects.get(id=city),
                        'contact_email': contact_email,
                        'contact_no': contact_no,
                        'founded_year': founded_year,
                        'employee_count': employee_count})
                return redirect('agency:agency_Profile')
            return render(request, 'agency/ATS/agency_profile_add.html', context)
    else:
        return redirect('agency:agency_profile')
@login_required(login_url="/")
def dashbord(request):
    context={}
    jobwise=[]
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['latest_10_candidates']=models.InternalCandidateBasicDetail.objects.filter(agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))).order_by('-create_at')[:10]
        get_assign_job=CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('job_id')
        get_candidate_job=CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).values_list('candidate_id__id',flat=True)
        # job_list=models.Tracker.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('job_id')
        
        for i in get_assign_job:
            jobdetail={'job_id':i.job_id.id,'job_title':i.job_id.job_title,'company':i.job_id.company_id.company_id.company_name,'remote_job':i.job_id.remote_job,
                        'exp':i.job_id.experience_year_max,'opening_date':i.job_id.publish_at,'job_type':i.job_id.job_type.name}
            
            result = models.AssociateJob.objects.filter(job_id=i.job_id).count()
            jobdetail['qpplicant']=result
            if i.job_id.salary_as_per_market:
                jobdetail['salary_range']='As per market' 
            else:
                jobdetail['salary_range']=i.job_id.min_salary+' LAP to ' +i.job_id.max_salary+' LAP'
            jobdetail['candidates']=[]
            jobwise_tracker = CompanyModels.Tracker.objects.filter(job_id=i.job_id).order_by('-update_at')
            for job in jobwise_tracker:
                if job.candidate_id.id in  get_candidate_job:
                    if CompanyModels.JobOffer.objects.filter(job_id=job.job_id,candidate_id=job.candidate_id,is_accepted=True).exists():
                        pass
                    else:
                        jobdetail['candidates'].append({'candidatefname':job.candidate_id.first_name,'candidatelname':job.candidate_id.last_name,'current':job.current_stage,'candidateid':job.candidate_id.id,
                                                        'next':job.next_stage,'action':job.action_required,'currentcompleted':job.currentcompleted,'reject':job.reject,'withdraw':job.withdraw})
            jobwise.append(jobdetail)
        #     print("=========",jobdetail)
        context['job_tracker']=jobwise
        return render(request, 'agency/ATS/dashbord.html', context)
    else:
        return redirect('agency:agency_profile')
# client add
def add_client(request,client_id=None):

    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Client Request':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
        if context['Add']:
            context['country'] = CandidateModels.Country.objects.all()
            context['replacement_terms'] = CandidateModels.ReplacementTerms.objects.all()
            context['payment_terms'] = CandidateModels.PaymentTerms.objects.all()
            context['industrytype'] = CandidateModels.IndustryType.objects.all()
            if client_id:
                context['client_data'] = models.CompanyAgencyConnection.objects.get(id=client_id,agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request,'agency/ATS/add-client.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_profile')

def get_companies(request):
    # cities = City.objects.all()
    print("GET COMAPNIES WAS CALLLLED")
    term = request.GET.get('term')
    connection = models.CompanyAgencyConnection.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),company_id__company_id__email=term).values_list('company_id',flat=True)
    companyid=CompanyProfile.objects.exclude(company_id__in=connection)
    company_list = []
    for i in companyid:
        data = {}
        print(i.company_id.company_id.id)
        data['id'] = i.company_id.company_id.id
        data['email'] = i.company_id.company_id.email
        data['company_name'] = i.company_id.company_id.company_name
        company_list.append(data)
    # print("citiesss",cities)
    return JsonResponse(company_list, safe=False)

def get_exists_client(request):
    data={}
    if request.method == 'POST':
        clientdata = json.loads(request.body.decode('UTF-8'))
        if clientdata['client_value'].isnumeric():
            if User.objects.filter(id=clientdata['client_value']).exists():
                clientdetail=User.objects.get(id=clientdata['client_value'])
                data['company_name']=clientdetail.company_name
                data['client_name']=clientdetail.first_name+ ' ' +clientdetail.last_name
                data['website']=clientdetail.website
                if CompanyProfile.objects.filter(company_id=Company.objects.get(company_id=clientdetail.id)).exists():
                    companyprofile=CompanyProfile.objects.get(company_id=Company.objects.get(company_id=clientdetail.id))
                    data['contact_no']=companyprofile.contact_no1
                    data['industry_type']=companyprofile.industry_type.id
                    data['address']=companyprofile.address
                    data['country']=companyprofile.country.id
                    data['state']=companyprofile.state.id
                    data['city']=companyprofile.city.id
                    data['countryname']=companyprofile.country.country_name
                    data['statename']=companyprofile.state.state_name
                    data['cityname']=companyprofile.city.city_name
                data['status']=True
                return JsonResponse(data, safe=False)
            else:
                data['status']=False
                return JsonResponse(data, safe=False)
        else:
            data['status']=False
            return JsonResponse(data, safe=False)
    else:
        data['status']=False
        return JsonResponse(data, safe=False)

def invite_client(request):
    if request.method=='POST':
        website=request.POST.get('website')
        workemail=request.POST.get('client-email')
        client_name=request.POST.get('client-name')
        company_name=request.POST.get('comnpany-name')
        contact_number=request.POST.get('contact-number-rate')
        industry=request.POST.get('industrial_type')
        address=request.POST.get('street-address')
        country=request.POST.get('country')
        state=request.POST.get('state')
        city=request.POST.get('city')
        commission_rate=request.POST.get('commission-rate')
        contract_details=request.FILES.get('contract')
        recuriement_terms=request.POST.get('recuriement-terms')
        payment_terms=request.POST.get('payment-terms')
        # contract_file=request.FILES.get('contract')
        if workemail.isnumeric():
            if User.objects.filter(id=workemail).exists():
                connection,update = models.CompanyAgencyConnection.objects.update_or_create( agency_id=models.Agency.objects.get(user_id=request.user.id),company_id=Company.objects.get(user_id=User.objects.get(id=workemail)),
                                                                            defaults={
                                                                            'website':website,
                                                                            'workemail':User.objects.get(id=workemail).email,
                                                                            'client_name':client_name,
                                                                            'company_name':company_name,
                                                                            'contact_number':contact_number,
                                                                            'industry':CandidateModels.IndustryType.objects.get(id=industry),
                                                                            'address':address,
                                                                            'country':CandidateModels.Country.objects.get(id=country),
                                                                            'state':CandidateModels.State.objects.get(id=state),
                                                                            'city':CandidateModels.City.objects.get(id=city),
                                                                            'contract_details':contract_details,
                                                                            'commission_rate':commission_rate,
                                                                            'payment_terms':CandidateModels.PaymentTerms.objects.get(id=payment_terms),
                                                                            'replacement_terms':CandidateModels.ReplacementTerms.objects.get(id=recuriement_terms),
                                                                            'is_accepted':False,
                                                                            'is_rejected':False,
                                                                            'is_terminated':False,
                                                                            'user_id':User.objects.get(id=request.user.id)})
                mail_subject = 'Invitation from Agency'
                # current_site = get_current_site(request)
                html_content = render_to_string('agency/ATS/connection.html',
                                                {'client': User.objects.get(id=workemail).email})
                to_email = User.objects.get(id=workemail).email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http" 
                description = connection.agency_id.agency_id.company_name +" sent you connection request."
                notify.send(request.user, recipient=User.objects.get(id=workemail), verb="Agency Request",
                                    description=description,image="/static/notifications/icon/company/request.png",
                                    target_url=header+"://"+current_site.domain+"/company/request_view/"+str(connection.id))
                return redirect('agency:all_connection')
        else:
            connection,update = models.CompanyAgencyConnection.objects.update_or_create( agency_id=models.Agency.objects.get(user_id=request.user.id),workemail=workemail,
                                                                        defaults={
                                                                        'website':website,
                                                                        'workemail':workemail,
                                                                        'client_name':client_name,
                                                                        'company_name':company_name,
                                                                        'contact_number':contact_number,
                                                                        'industry':CandidateModels.IndustryType.objects.get(id=industry),
                                                                        'address':address,
                                                                        'country':CandidateModels.Country.objects.get(id=country),
                                                                        'state':CandidateModels.State.objects.get(id=state),
                                                                        'city':CandidateModels.City.objects.get(id=city),
                                                                        'contract_details':contract_details,
                                                                        'commission_rate':commission_rate,
                                                                        'payment_terms':CandidateModels.PaymentTerms.objects.get(id=int(payment_terms)),
                                                                        'replacement_terms':CandidateModels.ReplacementTerms.objects.get(id=int(recuriement_terms)),
                                                                        'user_id':User.objects.get(id=request.user.id)})
            mail_subject = 'Invitation from Agency'
            # current_site = get_current_site(request)
            html_content = render_to_string('agency/ATS/connection.html', {'client': workemail})
            to_email = workemail
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect('agency:client_list')
def client_list(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Edit'] = False
        context['Delete'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Client Request':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
        if context['View'] or context['Edit'] or context['Delete']:
            context['clientlist']=models.CompanyAgencyConnection.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request,'agency/ATS/client_list.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_profile')
def client_detail_view(request,client_id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Edit'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Client Request':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
        if context['View'] or context['Edit']:
            context['client_detail']=models.CompanyAgencyConnection.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=client_id)
            return render(request,'agency/ATS/add_client_view.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_profile')

def delete_client(request):
    if request.method == 'POST':
        deleteclient = json.loads(request.body.decode('UTF-8'))
        if models.CompanyAgencyConnection.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),id=deleteclient['client_id']).exists(): 
            models.CompanyAgencyConnection.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=deleteclient['client_id']).delete()
            return HttpResponse(True)
        else:
            return HttpResponse(False)


def all_connection(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Edit'] = False
        context['Delete'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Client Request':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
        # if context['View'] or context['Edit'] or context['Delete']:
        context['pending_connections']=models.CompanyAgencyConnection.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),is_accepted=False,is_rejected=False)
        active_connections = models.CompanyAgencyConnection.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),is_accepted=True,is_rejected=False)#here will be filter query later
        
        context['active_connections'] = active_connections
        return render(request,'agency/ATS/all_connection.html',context)
    else:
        return redirect('agency:agency_Profile')

def active_connection_view(request,id):
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['accept_job_count']=0
        context['applied_candidate_count']=0
        job_submit_resume={}
        # 
        client_detail = models.CompanyAgencyConnection.objects.get(id=id,agency_id=models.Agency.objects.get(user_id=request.user.id),is_accepted=True,is_rejected=False)#here will be filter query later
        if models.AgencyType.objects.filter(agency_id=client_detail.agency_id,is_agency=True).exists():
            context['agency_profile']=models.AgencyProfile.objects.get(agency_id=client_detail.agency_id)
        if models.AgencyType.objects.filter(agency_id=client_detail.agency_id,is_freelancer=True).exists():
            context['agency_profile']=models.FreelancerProfile.objects.get(agency_id=client_detail.agency_id)
        if CompanyModels.CompanyProfile.objects.filter(company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id)).exists():
            context['company_profile']=CompanyModels.CompanyProfile.objects.get(company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id))
        if models.AgencyProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
            context['agencyprofile']=models.AgencyProfile.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
        if CompanyModels.AssignExternal.objects.filter(recruiter_id=models.Agency.objects.get(user_id=request.user.id),company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id)).exists():
            context['accept_job']=CompanyModels.AssignExternal.objects.filter(recruiter_id=models.Agency.objects.get(user_id=request.user.id),company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id),is_accepted=True)
            for jobs in context['accept_job']:

                print(jobs.job_id)
                jobsubmitresume = CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=jobs.job_id,company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id))
                job_submit_resume[jobs.job_id] =jobsubmitresume.count()
            context['accept_job_count']=context['accept_job'].count()
        if CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id)).exists():
            context['applied_candidate']=CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),company_id=CompanyModels.Company.objects.get(id=client_detail.company_id.id)).distinct('candidate_id')
            context['applied_candidate_count']=context['applied_candidate'].count()
        context['job_submit_resume']=job_submit_resume
        print(job_submit_resume)
        context['client_detail'] = client_detail
        return render(request,'agency/ATS/all_connected_client_view.html',context)
    else:
        return redirect('agency:agency_Profile')
def resend_mail(request):
    # connection_id = request.GET.get('connection_id')
    # print("\n\n\n\\n\n\n\n id zzzz",connection_id)
    # connection = models.CompanyAgencyConnection.objects.get(id=connection_id)
    # client = connection.company_id
    # agency = connection.agency_id
    # mail_subject = 'Invitation from Agency'
    # # current_site = get_current_site(request)
    # html_content = render_to_string('agency/connection.html', {'client': client})
    # to_email = client.email
    # from_email = settings.EMAIL_HOST_USER
    # msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
    # msg.attach_alternative(html_content, "text/html")
    # msg.send()
    return HttpResponse("done")

def job_request_table(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['AcceptReject'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                if permissions.permissionname == 'Accept/Reject':
                    context['AcceptReject'] = True
        if context['AcceptReject']:
            agencyid=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
            context['requestlist']=CompanyModels.AssignExternal.objects.filter(recruiter_id=agencyid.id,is_accepted=False,is_rejected=False)
            return render(request,'agency/ATS/job-request-table.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def job_openings_table(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['AcceptReject'] = False
        context['Add'] = False
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                if permissions.permissionname == 'Accept/Reject':
                    context['AcceptReject'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
                if permissions.permissionname == 'View':
                    context['View'] = True
        if context['Add'] or  context['Edit'] or  context['Delete']:
            context['internaljobs'] = models.JobCreation.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),close_job=False).order_by('-created_at')
        if context['AcceptReject']:
            agencyid=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
            context['requestlist']=CompanyModels.AssignExternal.objects.filter(recruiter_id=agencyid.id,is_accepted=False,is_rejected=False)
        emp = models.InternalUserProfile.objects.filter(InternalUserid=request.user,role__name='SuperAdmin')
        if emp:
            agencyid=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
            get_user_list=models.Agency.objects.filter(id=agencyid.id).values_list('user_id')
            context['jobs']=CompanyModels.AssignExternal.objects.filter(recruiter_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),is_accepted=True,is_rejected=False)
        else:
            context['jobs'] = models.AssignJobInternal.objects.filter(internal_user_id=models.InternalUserProfile.objects.get(InternalUserid=request.user))

        return render(request, 'agency/ATS/job_openings_table.html', context)
    else:
        return redirect('agency:agency_Profile')

def request_job_view(request, id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['AcceptReject']=False
        context['Assign']=False
        context['Unassign']=False
        context['Associate']=False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'JobCreation':
                if permissions.permissionname == 'Accept/Reject':
                    context['AcceptReject'] = True
                if permissions.permissionname == 'Accept/Reject':
                    context['Assign'] = True
                if permissions.permissionname == 'Accept/Reject':
                    context['Unassign'] = True
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                if permissions.permissionname == 'Associate':
                    context['Associate'] = True
        if context['Unassign'] or context['Assign'] or context['AcceptReject'] or context['Associate']:
            get_user_list=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
            acceptjobs=CompanyModels.AssignExternal.objects.filter(recruiter_id=get_user_list,job_id=CompanyModels.JobCreation.objects.get(id=id).id,is_accepted=True,is_rejected=False)
            if acceptjobs:
                acceptjobs=acceptjobs[0]
            else:
                acceptjobs=''
            context['jobs']=acceptjobs

            job_obj = CompanyModels.JobCreation.objects.get(id=id)
            context['job_obj']=job_obj
            if CompanyModels.JobWorkflow.objects.filter(job_id=job_obj).exists():
                job_workflow = CompanyModels.JobWorkflow.objects.get(job_id=job_obj)
                if job_workflow.workflow_id:
                    main_workflow = CompanyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
                    workflow_stages = CompanyModels.WorkflowStages.objects.filter(workflow=main_workflow).order_by('sequence_number')
                    context['workflow_stages']=workflow_stages
                    context['main_workflow']=main_workflow
            if CompanyModels.JobWorkflow.objects.filter(job_id=job_obj).exists():
                job_workflow = CompanyModels.JobWorkflow.objects.get(job_id=job_obj)
                context['job_workflow']=job_workflow
                if job_workflow.withworkflow:
                    context['workflow']=True
                else:
                    context['workflow']=False
                if job_workflow.workflow_id:
                    main_workflow = CompanyModels.Workflows.objects.get(id=job_workflow.workflow_id.id)
                    workflow_stages = CompanyModels.WorkflowStages.objects.filter(workflow=main_workflow).order_by('sequence_number')
                    context['workflow_stages']= workflow_stages
                    context['main_workflow']= main_workflow

                    workflow_data = []
                    for stage in workflow_stages:
                        stage_dict = {'stage': stage, 'data': ''}
                        if stage.stage.name == 'MCQ Test':
                            mcq_template = CompanyModels.ExamTemplate.objects.get(company_id=stage.company_id, template=stage.template,
                                                                            stage=stage.stage)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            if mcq_template.question_wise_time:
                                get_template_que = CompanyModels.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)

                                for time in get_template_que:
                                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                        "%M:%S")
                                stage_dict['mcq_time'] = total_time.time()
                            else:
                                stage_dict['mcq_time'] = datetime.datetime.strptime(mcq_template.duration, "%M:%S").time()
                            if mcq_template.marking_system == "question_wise":
                                get_template_que = CompanyModels.ExamQuestionUnit.objects.filter(template=mcq_template.template.id)
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
                            descriptive_template = CompanyModels.DescriptiveExamTemplate.objects.get(
                                company_id=stage.company_id,
                                stage=stage.stage,
                                template=stage.template)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')

                            get_template_que = CompanyModels.DescriptiveExamQuestionUnit.objects.filter(
                                template=descriptive_template.template.id)

                            for time in get_template_que:
                                total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time, "%M:%S")
                            stage_dict['descriptive_time'] = total_time.time()

                            get_template_que = CompanyModels.DescriptiveExamQuestionUnit.objects.filter(
                                template=descriptive_template.template.id)
                            total_marks = 0
                            for mark in get_template_que:
                                total_marks += int(mark.question_mark)
                            stage_dict['descriptive_marks'] = total_marks
                            stage_dict['data'] = descriptive_template

                        if stage.stage.name == 'Image Test':
                            image_template = CompanyModels.ImageExamTemplate.objects.get(company_id=stage.company_id,
                                                                                    stage=stage.stage,
                                                                                    template=stage.template)
                            total_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                            if image_template.question_wise_time:
                                get_template_que = CompanyModels.ImageExamQuestionUnit.objects.filter(
                                    template=image_template.template.id)

                                for time in get_template_que:
                                    total_time = total_time - time_zero + datetime.datetime.strptime(time.question_time,
                                                                                                        "%M:%S")
                                stage_dict['image_time'] = total_time.time()
                            else:
                                stage_dict['image_time'] = datetime.datetime.strptime(image_template.duration, "%M:%S").time()
                            if image_template.marking_system == "question_wise":
                                get_template_que = CompanyModels.ImageExamQuestionUnit.objects.filter(
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

                            audio_template = CompanyModels.AudioExamTemplate.objects.get(company_id=stage.company_id,
                                                                                    stage=stage.stage,
                                                                                    template=stage.template)

                            get_template_que = CompanyModels.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                            total_marks = 0
                            for mark in get_template_que:
                                total_marks += int(mark.question_mark)
                            stage_dict['audio_marks'] = total_marks
                            stage_dict['data'] = audio_template

                        if stage.stage.name == 'Coding Test':

                            coding_template = CompanyModels.CodingExamConfiguration.objects.get(company_id=stage.company_id,
                                                                                            template_id=stage.template)
                            if coding_template.assignment_type == 'marks':
                                coding_que_marks = CompanyModels.CodingExamQuestions.objects.filter(
                                    coding_exam_config_id=coding_template.id)
                                total_marks = 0
                                for i in coding_que_marks:
                                    total_marks += int(i.marks)
                                stage_dict['total_marks'] = total_marks
                            else:
                                coding_que_rating = CompanyModels.CodingScoreCard.objects.filter(coding_exam_config_id=coding_template)
                                stage_dict['coding_que_rating'] = coding_que_rating
                            stage_dict['data'] = coding_template

                        workflow_data.append(stage_dict)

                    context['workflow_data'] = workflow_data
            get_agency=models.AgencyType.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id))
            role_data = models.RolePermissions.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user),permission__permissionname='Associate').values_list('role')

            if get_agency.is_freelancer:
                context['internal_user_freelancer']=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            if get_agency.is_agency:
                context['internal_user_agency']=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),role__in=role_data)
            # context['applied_job_list'] = models.AssignJobInternal.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id))
            if models.AssignJobInternal.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id)).exists():
                context['internaljob']=models.AssignJobInternal.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id))
                context['assign_job']=context['internaljob'].internal_user_id.all().values_list('id', flat=True)
            context['active_job_count'] = len(
                CompanyModels.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=False, close_job_targetdate=False,
                                                is_publish=True))
            context['close_job_count'] = len(
                CompanyModels.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=True))
            context['last_close_job'] = CompanyModels.JobCreation.objects.filter(company_id=job_obj.company_id.id,
                                                                        close_job=True).order_by('-close_job_at').first()
            context['latest_10_job'] = CompanyModels.JobCreation.objects.filter(company_id=job_obj.company_id.id, close_job=False,
                                                                        close_job_targetdate=False, is_publish=True).order_by(
                '-publish_at')

            # print("=====================",context['assign_job'])
            if request.method=='POST':
                if 'Reject' in request.POST:
                    accept_job=CompanyModels.AssignExternal.objects.get(recruiter_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id).id)
                    accept_job.is_rejected=True
                    accept_job.save()
                    current_site = get_current_site(request)
                    header=request.is_secure() and "https" or "http" 
                    companyname=''
                    if accept_job.recruiter_id.agency_id.company_name:
                        companyname = accept_job.recruiter_id.agency_id.company_name
                    else:
                        companyname = accept_job.recruiter_id.agency_id.first_name +' '+ accept_job.recruiter_id.agency_id.first_name
                    description = companyname +" has declined your Job "+job_obj.job_title+" Request"
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.company_id.company_id.id), verb="Job Request declined",
                                        description=description,image="/static/notifications/icon/company/decline.png",
                                        target_url=header+"://"+current_site.domain+"/company/created_job_view/"+str(job_obj.id))
                    return redirect('agency:request_job_view',id=str(job_obj.id))
                elif 'Accept' in request.POST:
                    agency_internaluser=request.POST.getlist('ir-selector-1')
                    print('agency_internaluser',agency_internaluser)
                    accept_job=CompanyModels.AssignExternal.objects.get(recruiter_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id).id)
                    accept_job.is_accepted=True
                    accept_job.save()
                    internaljob,created=models.AssignJobInternal.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id),
                                                                        defaults={
                                                                            'user_id':User.objects.get(id=request.user.id)
                                                                        })
                    for user_internal in agency_internaluser:
                        print('============================',models.InternalUserProfile.objects.get(InternalUserid=user_internal))
                        internaljob.internal_user_id.add(models.InternalUserProfile.objects.get(InternalUserid=user_internal))
                    assign_internal=''
                    if models.AssignJobInternal.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id)).exists():
                        assign_internal=models.AssignJobInternal.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=CompanyModels.JobCreation.objects.get(id=id))
                    to_email=[]
                    for i in assign_internal.internal_user_id.all():
                        to_email.append(i.InternalUserid.email)
                    if len(to_email)!=0:
                        mail_subject = 'You have been invited to a new job'
                        html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"You have been assigned to new job "+job_obj.job_title+" by “Admin/role”. Please login and submit candidates"})
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
                        msg.attach_alternative(html_content, "text/html")
                        # try:
                        msg.send()
                        current_site = get_current_site(request)
                        header=request.is_secure() and "https" or "http" 
                        companyname=''
                        if accept_job.recruiter_id.agency_id.company_name:
                            companyname = accept_job.recruiter_id.agency_id.company_name
                        else:
                            companyname = accept_job.recruiter_id.agency_id.first_name +' '+ accept_job.recruiter_id.agency_id.first_name
                        description = companyname +" has accepted your Job "+job_obj.job_title+" Request"
                        notify.send(request.user, recipient=User.objects.get(id=job_obj.company_id.company_id.id), verb="Job Request accepted",
                                            description=description,image="/static/notifications/icon/company/Accept.png",
                                            target_url=header+"://"+current_site.domain+"/agency/job_view/"+str(job_obj.id))
                    return redirect('agency:request_job_view',id=str(job_obj.id))
            return render(request, 'agency/ATS/job-request-view.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def add_internal_user(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalUser':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
        if context['Add'] :
            context['department']=models.Department.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),status=True)
            context['role']=models.Role.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            context['RecruiterType']=CandidateModels.RecruiterType.objects.all()
            if request.method == 'POST':
                fname = request.POST.get('f-name')
                lname = request.POST.get('l-name')
                email = request.POST.get('email')
                gender = request.POST.get('gender')
                contact = request.POST.get('contact-num')
                department=request.POST.get('department')
                recruiter_type=request.POST.get('recruitertype')
                branch=request.POST.get('branch')
                spaciility=request.POST.getlist('specialties')
                aboutus = request.POST.getlist('aboutus')
                role=request.POST.get('role')
                total_exper = request.POST.get('professional-experience-year')+'.' + request.POST.get(
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
                if User.objects.filter(email=request.POST['email'].lower()).exists():
                    context['message'] = "email already exists"
                else:
                    print('created')
                    usr = User.objects.create_agency_user(email=email.lower(), first_name=fname, last_name=lname,
                                                        password=password, ip=ip, device_type=device_type,
                                                        browser_type=browser_type,
                                                        browser_version=browser_version, os_type=os_type,
                                                        os_version=os_version)
                    agencyid=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))
                    agencyid.user_id.add(User.objects.get(email=email.lower()))
                    internaluser=models.InternalUserProfile.objects.create(InternalUserid=User.objects.get(email=email.lower()),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                role=models.Role.objects.get(id=role),recruiter_type=CandidateModels.RecruiterType.objects.get(id=recruiter_type),
                                                                department=models.Department.objects.get(id=department),
                                                                contact_number=contact,gender=gender,branch=branch,unique_id=create_employee_id(),
                                                                total_experiance=total_exper,aboutus=aboutus,spaciility=', '.join(spaciility),agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)))
                    try:
                        mail_subject = 'Activate your account.'
                        current_site = get_current_site(request)
                        # print('domain----===========',current_site.domain)
                        html_content = render_to_string('accounts/send_credentials.html', {'user': usr,
                                                                                            'name': fname + ' ' + lname,
                                                                                            'email': email,
                                                                                            'domain': current_site.domain,
                                                                                            'password': password, })
                        to_email = usr.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                            name="SuperAdmin")
                        get_admin = models.InternalUserProfile.objects.filter(role=role_id_get, agency_id=models.Agency.objects.get(
                            user_id=request.user)).values_list('InternalUserid', flat=True)
                        current_site = get_current_site(request)
                        header=request.is_secure() and "https" or "http" 
                        for i in get_admin:
                            description = request.user.first_name + "Add Internal User"
                            if i != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=i), verb="Add Internal User",
                                            description=description,
                                            target_url="http://192.168.1.148:8000/agency/internal_user_view/"+str(internaluser.id))
                        return redirect('agency:internal_user_list')
                    except BadHeaderError:
                        new_registered_usr = User.objects.get(email__exact=email).delete()
                        context['message'] = "email not send"
            return render(request, 'agency/ATS/add_inter_user.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')
def internal_user_list(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['View'] = True
        context['Edit'] = False
        context['Delete'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalUser':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['View'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['View'] or context['Edit'] or context['Delete']:
            context['internaluser']=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request, 'agency/ATS/internal_user_list.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')
def update_internal_user(request,id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Add'] = False
        context['Edit'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalUser':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
        if context['Add'] or context['Edit']:
            context['department'] = models.Department.objects.filter(
                agency_id=models.Agency.objects.get(user_id=request.user.id), status=True)
            context['role'] = models.Role.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            context['RecruiterType'] = CandidateModels.RecruiterType.objects.all()
            context['internaluser']=models.InternalUserProfile.objects.get(id=id,agency_id=models.Agency.objects.get(user_id=request.user))
            if request.method=='POST':
                fname = request.POST.get('f-name')
                lname = request.POST.get('l-name')
                email = request.POST.get('email')
                gender = request.POST.get('gender')
                contact = request.POST.get('contact-num')
                department = request.POST.get('department')
                recruiter_type = request.POST.get('recruitertype')
                branch = request.POST.get('branch')
                spaciility = request.POST.getlist('specialties')
                aboutus = request.POST.get('aboutus')
                role = request.POST.get('role')
                total_exper = request.POST.get('professional-experience-year') + '.' + request.POST.get(
                    'professional-experience-month')
                update,updated=models.InternalUserProfile.objects.update_or_create(id=id,agency_id=models.Agency.objects.get(
                        user_id=User.objects.get(id=request.user.id)),defaults={
                                                        'user_id':User.objects.get(id=request.user.id),
                                                        'role':models.Role.objects.get(id=role),
                                                        'recruiter_type':CandidateModels.RecruiterType.objects.get(
                                                            id=recruiter_type),
                                                        'department':models.Department.objects.get(id=department),
                                                        'contact_number':contact, 'gender':gender, 'branch':branch,
                                                        'total_experiance':total_exper, 'aboutus':aboutus,
                                                        'spaciility':', '.join(spaciility)})
                role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                    name="SuperAdmin")
                get_admin = models.InternalUserProfile.objects.filter(role=role_id_get, agency_id=models.Agency.objects.get(
                    user_id=request.user)).values_list('InternalUserid', flat=True)
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http" 
                for i in get_admin:
                    description = request.user.first_name + "Update Internal User"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Internal User",
                                    description=description,
                                    target_url="http://192.168.1.148:8000/agency/internal_user_view/" + str(update.id))
                return redirect('agency:internal_user_list')
            return render(request,'agency/ATS/add_inter_user.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')
def internal_user_view(request,id):
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['accept_job_count']=0
        context['applied_candidate_count']=0
        job_submit_resume={}
        company_logo={} 
        client_detail = models.InternalUserProfile.objects.get(id=id,agency_id=models.Agency.objects.get(user_id=request.user.id))#here will be filter query later
        if models.AssignJobInternal.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),internal_user_id=id).exists():
            context['accept_job']=models.AssignJobInternal.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),internal_user_id=id)
            for jobs in context['accept_job']:
                jobsubmitresume = models.AssociateJob.objects.filter(internal_user__id=id,agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=jobs.job_id).count()
                
                if CompanyModels.CompanyProfile.objects.filter(company_id=jobs.job_id.company_id).exists():
                    company_profile=CompanyModels.CompanyProfile.objects.get(company_id=jobs.job_id.company_id)
                    company_logo[jobs.job_id] =company_profile
                job_submit_resume[jobs.job_id] =jobsubmitresume
        
            context['accept_job_count']=context['accept_job'].count()
        if models.AssociateJob.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),internal_user=id).exists():
            applied_candidate=models.AssociateJob.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),internal_user=id)
            context['applied_candidate']=applied_candidate.distinct('internal_candidate_id')
            context['applied_candidate_count']=applied_candidate.count()
        context['job_submit_resume']=job_submit_resume
        context['company_logo']=company_logo
        context['client_detail'] = client_detail
        return render(request,'agency/ATS/internal_user_profile.html',context)
    else:
        return redirect('agency:agency_Profile')

def add_internal_candidate_basic_detail(request,int_cand_detail_id=None):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['Add'] = False
        context['Edit'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        edit_internal_candidate=''
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'Add':
                    context['Add'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
        if context['Add'] or context['Edit'] :
            if int_cand_detail_id:
                edit_internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=int(int_cand_detail_id))
                context['edit_internal_candidate'] = edit_internal_candidate
            if request.method == 'POST':
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

                models.InternalCandidateBasicDetail.objects.update_or_create(email=email,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                    'user_id' : User.objects.get(id=request.user.id),
                    'candidate_custom_id' : employee_id,
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
                add_skill=models.InternalCandidateBasicDetail.objects.get(email=email,agency_id = models.Agency.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_skill.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_skill.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_skill.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_skill.categories.add(main_categ_obj)
                if User.objects.filter(email=email.lower()).exists():
                    add_skill.candidate_id=User.objects.get(email=email.lower())
                add_skill.save()
                if secure_resume_get=="Secure-Resume":
                    return redirect("agency:redact_resume",internal_candidate_id = add_skill.id)
                else:
                    return redirect('agency:all_candidates')

            return render(request,'agency/ATS/add_candidate_basic_form.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def redact_resume(request,internal_candidate_id):
    internal_candidate = get_object_or_404(models.InternalCandidateBasicDetail,pk=internal_candidate_id)
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['internal_candidate'] = internal_candidate
        return render(request,"agency/ATS/redact_resume.html",context)
    else:
        return redirect('agency:agency_Profile')


def get_file_name(file_path):
    file_name = file_path.split('/')[-1]
    return file_name

def save_redacted_resume(request,internal_candidate_id):
    internal_candidate = get_object_or_404(models.InternalCandidateBasicDetail,pk=internal_candidate_id)
    file_name = get_file_name(internal_candidate.resume.url)
    # print("request.Post",request.POST)
    # print("bodyyyyyyy",request.body)
    data = json.loads(request.body.decode('UTF-8'))
    print("\n\n\n\n\n\\n\ndatttttttttta",data)
    redacted_resume_blob = data['pdf_blob']
    # print(pdf_s)
    media_path = 'media/'
    redacted_file_path = media_path+file_name
    redacted_resume = open(redacted_file_path,'wb+')
    redacted_resume.write(base64.b64decode(redacted_resume_blob))
    redacted_resume.close()
    internal_candidate.secure_resume_file.name = redacted_file_path[len(media_path):]
    internal_candidate.save()
    # file = open('myfile.dat', 'w+')
    return HttpResponse("done")

def get_candidate_categories(request):
    term = request.GET.get('term')
    categories = models.CandidateCategories.objects.filter(category_name__istartswith=term,
                                                       agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)))
    categories_list = []
    for i in categories:
        data = {}
        data['id'] = i.id
        data['name'] = i.category_name
        categories_list.append(data)
    return JsonResponse(categories_list, safe=False)

def all_candidates(request):
    data = []
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['Edit'] = False
        context['Delete'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['View'] = True
                if permissions.permissionname == 'Edit':
                    context['Edit'] = True
                if permissions.permissionname == 'Delete':
                    context['Delete'] = True
        if context['View'] or context['Edit'] or context['Delete']:
            print(request.user.id)
            candidates = models.InternalCandidateBasicDetail.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),withdraw_by_Candidate=False)
            candidate_in_review = models.CandidateTempDatabase.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).order_by('-create_at')
            context['candidate_in_review']= candidate_in_review
            myFilter = CandidateFilter(request.GET, queryset=candidates)
            candidates = myFilter.qs 
            context['myFilter']=myFilter
            context ['candidates']=candidates
            if models.InternalUserProfile.objects.filter(InternalUserid=request.user).exists():
                employee_obj = models.InternalUserProfile.objects.get(InternalUserid=request.user)
                context['employee_obj']= employee_obj
            # for candidate in candidates:
            #     candidate_dict = {'id': candidate.id, 'name': candidate.first_name + ' ' + candidate.last_name,
            #                       'city': candidate.prefered_city.all()}
            #     # candidate_dict['job_title'] = professional_detail.current_job_title
            #     candidate_dict['experience'] = candidate.total_exper
            #     candidate_dict['expected_salary'] = candidate.expectedctc
            #     candidate_dict['notice_period'] = candidate.notice.notice_period
            #     candidate_dict['update_at'] = candidate.update_at
            #     candidate_dict['customid'] = candidate.candidate_custom_id

            #     # candidate_dict['source'] = models.InternalCandidateSource.objects.get(internal_candidate_id=candidate.id)
            #     data.append(candidate_dict)
            return render(request, 'agency/ATS/all_candidates.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')


def view_candidate(request, candidate_id):
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['View'] = True
        context['Associate'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'InternalCandidate':
                print(len(permissions.permissionname))
                if permissions.permissionname == 'View':
                    print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                    context['View'] = True
                if permissions.permissionname == 'Associate':
                    context['Associate'] = True
        if context['View'] or context['Associate']:
            if models.InternalCandidateBasicDetail.objects.filter(id=candidate_id).exists():
                basic_detail = models.InternalCandidateBasicDetail.objects.get(id=candidate_id)
                context['basic_detail'] = basic_detail
                agencyjob=models.AssignJobInternal.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id__close_job=False)
                context['job_list']=agencyjob
                agencyinternaljob=models.JobCreation.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),close_job=False)
                context['internal_job_list']=agencyinternaljob
                context['candidate_education'] = CandidateModels.CandidateEducation.objects.filter(
                    candidate_id=basic_detail.candidate_id)
                context['candidate_experience'] = CandidateModels.CandidateExperience.objects.filter(
                    candidate_id=basic_detail.candidate_id)
                context['candidate_certification'] = CandidateModels.CandidateCertificationAttachment.objects.filter(
                    candidate_id=basic_detail.candidate_id)
                context['candidate_award'] = CandidateModels.CandidateAward.objects.filter(
                    candidate_id=basic_detail.candidate_id)
                context['candidate_portfolio'] = CandidateModels.CandidatePortfolio.objects.filter(
                    candidate_id=basic_detail.candidate_id)
                context['candidate_preferences'] = CandidateModels.CandidateJobPreference.objects.filter(
                    candidate_id=basic_detail.candidate_id)
                # basic_detail = models.InternalCandidate.objects.get(id=candidate_id)
                # professional_detail = models.InternalCandidateProfessionalDetail.objects.get(internal_candidate_id=candidate_id)
                # candidate_preference = models.InternalCandidatePreference.objects.get(internal_candidate_id=candidate_id)
                # candidate_education = models.InternalCandidateEducation.objects.filter(internal_candidate_id=candidate_id)
                # candidate_experience = models.InternalCandidateExperience.objects.filter(internal_candidate_id=candidate_id)
                # candidate_attachments = models.InternalCandidateAttachment.objects.filter(internal_candidate_id=candidate_id)
                # candidate_source = models.InternalCandidateSource.objects.get(internal_candidate_id=candidate_id)
                # main_skills = models.InternalCandidateProfessionalSkill.objects.get(
                #     internal_candidate_id=candidate_id).skills.all()
                # custom_added_skill = models.InternalCandidateProfessionalSkill.objects.get(
                #     internal_candidate_id=candidate_id).custom_added_skills.all()
                notes = models.InternalCandidateNotes.objects.filter(internal_candidate_id=candidate_id,agency_id=models.Agency.objects.get(
                                                                            user_id=request.user.id))
                # skills = []
                # for i in main_skills:
                #     skills.append(i.name)
                # for i in custom_added_skill:
                #     skills.append(i.name)

                # context['basic_detail'] = basic_detail
                # context['professional_detail'] = professional_detail
                # context['candidate_preference'] = candidate_preference
                # context['candidate_education'] = candidate_education
                # context['candidate_experience'] = candidate_experience
                # context['attachments'] = candidate_attachments
                # context['sources'] = candidate_source
                # context['skills'] = skills
                context['notes'] = notes
                applied_job = CompanyModels.AssociateCandidateAgency.objects.filter(candidate_id=basic_detail.candidate_id,
                                                                    agency_id=models.Agency.objects.get(
                                                                        user_id=request.user.id))
                context['appliedjobcount'] = len(applied_job)
                # =================
                candidate_stages_data = []
                for job in applied_job:
                    stages = CompanyModels.CandidateJobStagesStatus.objects.filter(
                        candidate_id=job.candidate_id,
                        job_id=job.job_id).order_by('sequence_number')

                    data = {'id': User.objects.get(id=basic_detail.candidate_id.id), 'job_obj': job.job_id, 'stages': stages,
                            'applied_date': job.create_at}
                    candidate_stages_data.append(data)
                context['applied_job'] = candidate_stages_data
                return render(request, 'agency/ATS/Candidate_view.html', context)
            else:
                return HttpResponse('Invalid Url')
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def internal_candidate_notes(request):
    if request.method == 'POST':
        candidate = models.InternalCandidateBasicDetail.objects.get(id=request.POST.get('candidate_id'))
        created_note = models.InternalCandidateNotes.objects.create(internal_candidate_id=candidate,
                                                                    agency_id=models.Agency.objects.get(
                                                                        user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id),
                                                                    note=request.POST.get('message'))
        return JsonResponse({'date': created_note.create_at, 'status': 'success'}, safe=False)

from django.core import serializers
def check_candidate_email_is_valid(request):
    email = request.POST.get("email")
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    data={}
    if (re.search(regex, email)):
        user_obj = models.InternalCandidateBasicDetail.objects.filter(email=email,agency_id = models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))).exists()
        if user_obj:
            user_data=models.InternalCandidateBasicDetail.objects.get(email=email,agency_id = models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)))
            # data = serializers.serialize('json', models.InternalCandidateBasicDetail.objects.get(email=email,agency_id = models.Agency.objects.get(user_id=User.objects.get(id=request.user.id))))
            if user_data.candidate_id:
                data['candidate_id']=user_data.candidate_id.id
            else:
                data['candidate_id']=None
            if user_data.candidate_custom_id:
                data['candidate_custom_id']=user_data.candidate_custom_id
            else:
                data['candidate_custom_id']=None
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
            if user_data.secure_resume:
                data['secure_resume']=user_data.secure_resume
            else:
                data['secure_resume']=None
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
            return HttpResponse(False)
    else:
        return HttpResponse('Invalid')


def check_candidate_customid_is_valid(request):
    candidatecid = request.POST.get("customid")
    regex = '^[a-zA-Z]{4}[@#$%&*]{1}[0-9]{4}'
    if (re.search(regex, candidatecid)):
        user_obj = models.InternalCandidateBasicDetail.objects.filter(candidate_custom_id=candidatecid).exists()
        if user_obj:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    else:
        return HttpResponse('Invalid')
def generate_referral_code():
    num = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(12)])
    return num

def associate_job(request,candidate_id):
    alert={}
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        current_site = get_current_site(request)
        header=request.is_secure() and "https" or "http" 
        get_internalcandidate=models.InternalCandidateBasicDetail.objects.get(id=candidate_id)
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=candidate_id)
        context['edit_internal_candidate']=internal_candidate
        if request.method=="POST":
            associate_jon_list=request.POST.get('associate-selector')
            
            job_id_get=associate_jon_list.split('-')
            if job_id_get[0]=='company':
                context['jobid']=CompanyModels.JobCreation.objects.get(id=job_id_get[1])
            if job_id_get[0]=='agency':
                context['jobid']=models.JobCreation.objects.get(id=job_id_get[1])
            context['jobtype']=job_id_get[0]
            
            return render(request,'agency/ATS/applied_candidate_detail_form.html',context)
        else:
            return HttpResponseRedirect('/agency/view_candidate/'+str(get_internalcandidate.id))
            # else:
            #     return HttpResponse(False)
    else:
        return redirect('agency:agency_Profile')

def submit_candidate(request, id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['job_id']= id
        candidates = models.InternalCandidateBasicDetail.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        context['candidates'] = candidates
        internal_candidate=''
        if request.method == 'POST':
            context['source']=CandidateModels.Source.objects.all()
            context['notice_period']= CandidateModels.NoticePeriod.objects.all()
            context['countries']= CandidateModels.Country.objects.all()
            context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            job_obj = CompanyModels.JobCreation.objects.get(id=int(id))
            context['jobid']=job_obj
            context['jobtype']='company'
            internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=request.POST.get('selected_candidate'))
            context['edit_internal_candidate']=internal_candidate
            return render(request,'agency/ATS/applied_candidate_detail_form.html',context)
            # fname = internal_candidate.first_name
            # lname = internal_candidate.last_name
            # email = internal_candidate.email
            # gender = internal_candidate.gender
            # resume = internal_candidate.resume
            # contact = internal_candidate.contact
            # secure_resume=internal_candidate.secure_resume
            # secure_resume_file=internal_candidate.secure_resume_file
            # designation = internal_candidate.designation
            # notice = internal_candidate.notice
            # ctc = internal_candidate.ctc
            # expectedctc = internal_candidate.expectedctc
            # total_exper = internal_candidate.total_exper
            # password = get_random_string(length=12)
        #     if not User.objects.filter(email=internal_candidate.email.lower()).exists():

        #         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        #         if x_forwarded_for:
        #             ip = x_forwarded_for.split(',')[0]
        #         else:
        #             ip = request.META.get('REMOTE_ADDR')
        #         device_type = ""
        #         if request.user_agent.is_mobile:
        #             device_type = "Mobile"
        #         if request.user_agent.is_tablet:
        #             device_type = "Tablet"
        #         if request.user_agent.is_pc:
        #             device_type = "PC"
        #         browser_type = request.user_agent.browser.family
        #         browser_version = request.user_agent.browser.version_string
        #         os_type = request.user_agent.os.family
        #         os_version = request.user_agent.os.version_string
        #         usr = User.objects.apply_candidate(email=email.lower(), first_name=fname, last_name=lname,
        #                                         password=password, ip=ip, device_type=device_type,
        #                                         browser_type=browser_type,
        #                                         browser_version=browser_version, os_type=os_type,
        #                                         os_version=os_version,
        #                                         referral_number=generate_referral_code())

        #         mail_subject = 'Activate your account'
        #         current_site = get_current_site(request)
        #         header=request.is_secure() and "https" or "http"
        #         # print('domain----===========',current_site.domain)
        #         html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
        #                                                                         'name': fname + ' ' + lname,
        #                                                                         'email': email,
        #                                                                         'domain': current_site.domain,
        #                                                                         'password': password, 
        #                                                                         'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id)
        #                                                                         })
        #         to_email = usr.email
        #         from_email = settings.EMAIL_HOST_USER
        #         msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
        #         msg.attach_alternative(html_content, "text/html")
        #         # try:
        #         msg.send()
        #         internal_candidate.candidate_id = User.objects.get(email=email.lower())
        #         internal_candidate.save()
        #         add_candidate, create = CandidateModels.candidate_job_apply_detail.objects.update_or_create(
        #             candidate_id=internal_candidate.candidate_id, defaults={
        #                 'gender': gender,
        #                 'resume': resume,
        #                 'contact': contact,
        #                 'designation': designation,
        #                 'notice': notice,
        #                 'ctc': ctc,
        #                 'expectedctc': expectedctc,
        #                 'total_exper': total_exper})

        #         for i in internal_candidate.skills.all():
        #             print(type(int(i.id)))
        #             main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
        #             add_candidate.skills.add(main_skill_obj.id)
        #         for i in internal_candidate.prefered_city.all():
        #             main_city_obj = CandidateModels.City.objects.get(id=i.id)
        #             add_candidate.prefered_city.add(main_city_obj.id)
        #         add_candidate.save()
        #     else:
        #         if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = internal_candidate.candidate_id).exists():
        #             add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id =internal_candidate.candidate_id,defaults={
        #                                                                             'gender' :gender,
        #                                                                             'resume' : resume,
        #                                                                             'contact' : contact,
        #                                                                             'designation' : designation,
        #                                                                             'notice' : notice,
        #                                                                             'ctc' : ctc,
        #                                                                             'expectedctc' : expectedctc,
        #                                                                             'total_exper' :  total_exper})
        #             for i in internal_candidate.skills.all():
        #                 print(type(int(i.id)))
        #                 main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
        #                 add_candidate.skills.add(main_skill_obj.id)
        #             for i in internal_candidate.prefered_city.all():
        #                 main_city_obj = CandidateModels.City.objects.get(id=i.id)
        #                 add_candidate.prefered_city.add(main_city_obj.id)
        #             add_candidate.save()
        #         toemail=[internal_candidate.email]
        #         mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
        #         html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
        #         from_email = settings.EMAIL_HOST_USER
        #         msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
        #         msg.attach_alternative(html_content, "text/html")
        #         # try:
        #         msg.send()
        #         internal_candidate.candidate_id = User.objects.get(email=internal_candidate.email)
        #         internal_candidate.save()
        #     CompanyModels.AssociateCandidateAgency.objects.update_or_create(company_id=job_obj.company_id,job_id=job_obj,agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),candidate_id=internal_candidate.candidate_id,
        #             defaults={
        #                 'agency_internal_id':models.InternalCandidateBasicDetail.objects.get(id=internal_candidate.id)
        #             })
        #     CompanyModels.AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,job_id=job_obj,candidate=User.objects.get(email=email.lower()),
        #             defaults={
        #                 'submit_type':'Agency'
        #             })
        #     models.DailySubmission.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),company_job_id=CompanyModels.JobCreation.objects.get(id=job_obj.id),internal_candidate_id=internal_candidate.id,job_type='company',
        #             defaults={
        #                 'internal_user':models.InternalUserProfile.objects.get(InternalUserid=request.user.id),
        #                 'user_id':request.user,
        #                 'applied':True
        #             })
        #     if secure_resume:
        #         models.CandidateSecureData.objects.update_or_create(
        #                                                 agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),
        #                                                 job_id=job_obj,
        #                                                 company_id=job_obj.company_id,
        #                                                 candidate_id=User.objects.get(email=email.lower()),
        #                                                 defaults={'user_id': User.objects.get(
        #                                                     id=request.user.id)
        #                                                 })
        #     models.AssociateJob.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),
        #                                                                 job_id=job_obj,
        #                                                                 internal_candidate_id=models.InternalCandidateBasicDetail.objects.get(id=internal_candidate.id),
        #                                                                 internal_user=models.InternalUserProfile.objects.get(InternalUserid=request.user.id),
        #                                                                 defaults={'user_id' : User.objects.get(id=request.user.id)
        #                                                                 })
        #     workflow = CompanyModels.JobWorkflow.objects.get(job_id=job_obj)
        #     current_stage=None
        #     currentcompleted=False
        #     next_stage = None
        #     next_stage_sequance=0
        #     # onthego change
        #     if workflow.withworkflow:
        #         print("==========================withworkflow================================")
        #         workflow_stages = CompanyModels.WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
        #         if workflow.is_application_review:
        #             print("==========================is_application_review================================")
        #             print('\n\n is_application_review')
        #             for stage in workflow_stages:
        #                 if stage.sequence_number == 1:
        #                     status = 2
        #                     sequence_number = stage.sequence_number
        #                 elif stage.sequence_number == 2:
        #                     print("==========================Application Review================================")
        #                     status = 1
        #                     stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
        #                     current_stage = stage_list_obj
        #                     next_stage_sequance=stage.sequence_number+1
        #                     CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                             candidate_id=internal_candidate.candidate_id,
        #                                                             job_id=job_obj, stage=stage_list_obj,
        #                                                             sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
        #                     sequence_number = stage.sequence_number + 1
        #                     status = 0
        #                 else:
        #                     status = 0
        #                     sequence_number = stage.sequence_number + 1
        #                     next_stage = stage.stage
        #                 CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj, stage=stage.stage,
        #                                                         template=stage.template,
        #                                                         sequence_number=sequence_number,status=status,custom_stage_name=stage.stage_name)
        #         else:
        #             for stage in workflow_stages:
        #                 if stage.sequence_number == 1:
        #                     status = 2
        #                     current_stage = stage.stage
        #                 elif stage.sequence_number == 2:
        #                     status = 1
        #                     next_stage = stage.stage
        #                 else:
        #                     status = 0
        #                 CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj, stage=stage.stage,
        #                                                         template=stage.template,
        #                                                         sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
        #     internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=request.POST.get('selected_candidate'))
        #     if workflow.onthego:
        #         print("==========================onthego================================")
        #         onthego_stages = CompanyModels.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

        #         if workflow.is_application_review:
        #             for stage in onthego_stages:
        #                 if stage.sequence_number == 1:
        #                     status = 2
        #                     sequence_number = stage.sequence_number
        #                     CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                             candidate_id=internal_candidate.candidate_id,
        #                                                             job_id=job_obj, stage=stage.stage,
        #                                                             template=stage.template,
        #                                                             sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

        #                     status = 1
        #                     sequence_number = stage.sequence_number + 1
        #                     stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
        #                     current_stage = stage_list_obj
        #                     next_stage_sequance=stage.sequence_number+1
        #                     CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                             candidate_id=internal_candidate.candidate_id,
        #                                                             job_id=job_obj, stage=stage_list_obj,
        #                                                             sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
        #                 else:
        #                     status = 0
        #                     sequence_number = stage.sequence_number + 1
        #                     current_stage = stage_list_obj
        #                     CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                             candidate_id=internal_candidate.candidate_id,
        #                                                             job_id=job_obj, stage=stage.stage,
        #                                                             template=stage.template,
        #                                                             sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)
        #         else:
        #             for stage in onthego_stages:
        #                 if stage.sequence_number == 1:
        #                     status = 2
        #                     current_stage = stage.stage
        #                 elif stage.sequence_number == 2:
        #                     status = 1
        #                     next_stage = stage.stage
        #                 else:
        #                     status = 0
        #                 CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj, stage=stage.stage,
        #                                                         template=stage.template,
        #                                                         sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
        #     action_required=''
            
        #     if next_stage_sequance!=0:
        #         if CompanyModels.CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj,
        #                                                         sequence_number=next_stage_sequance).exists():
        #             next_stage=CompanyModels.CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj,
        #                                                         sequence_number=next_stage_sequance).stage
        #     if not current_stage==None:
        #         if current_stage.name=='Interview' :
        #             action_required='By Company/Agency'
        #         elif current_stage.name=='Application Review' :
                    
        #             action_required='By Company'
        #         else:
        #             action_required='By Candidate'
        #     if current_stage!='':
        #         CompanyModels.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=internal_candidate.candidate_id,company_id=job_obj.company_id,defaults={
        #                                                 'current_stage':current_stage,'next_stage':next_stage,
        #                                                 'action_required':action_required,'update_at':datetime.datetime.now()})
        #     assign_job_internal = list(
        #         CompanyModels.CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
        #                                         company_id=job_obj.company_id).values_list(
        #             'recruiter_id', flat=True))
        #     assign_job_internal.append(job_obj.job_owner.id)
        #     assign_job_internal.append(job_obj.contact_name.id)
        #     assign_job_agency_internal=list(models.AssignJobInternal.objects.filter(job_id=job_obj).values_list(
        #                         'internal_user_id__InternalUserid__id', flat=True))
        #     assign_job_internal.extend(assign_job_agency_internal)
        #     assign_job_internal = list(set(assign_job_internal))
        #     title = job_obj.job_title
        #     chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(id=request.user.id).id, title=title,candidate_id=User.objects.get(id=internal_candidate.candidate_id.id))
        #     print(assign_job_internal)
        #     ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=internal_candidate.candidate_id.id).id)
        #     for i in assign_job_internal:
        #         ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
        #     ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
        #     candidate=User.objects.get(email=internal_candidate.email)
        #     job_assign_recruiter = CompanyModels.CompanyAssignJob.objects.filter(job_id=job_obj)
        #     agency_name=models.Agency.objects.get(user_id=request.user.id).agency_id.company_name
        #     current_site = get_current_site(request)
        #     header=request.is_secure() and "https" or "http"
        #     if not agency_name:
        #         agency_name=request.user.first_name+' '+request.user.last_name
        #     description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
        #     to_email=[]
        #     to_email.append(job_obj.contact_name.email)
        #     to_email.append(job_obj.job_owner.email)
        #     if job_obj.contact_name.id != request.user.id:
        #         notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                     description=description,image="/static/notifications/icon/company/Candidate.png",
        #                                                                     target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                         job_obj.id))
        #     if job_obj.job_owner.id != request.user.id:
        #         notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                     description=description,image="/static/notifications/icon/company/Candidate.png",
        #                                                                     target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                         job_obj.id))
        #     all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        #     for i in all_assign_users:
        #         if i.recruiter_type_internal:
        #             to_email.append(i.recruiter_id.email)
        #             if i.recruiter_id.id != request.user.id:
        #                 notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                     description=description,image="/static/notifications/icon/company/Candidate.png",
        #                                                                     target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                         job_obj.id))
        #     description="Your profile has been succesfully submitted for the job"+job_obj.job_title+" by "+agency_name
        #     notify.send(request.user, recipient=User.objects.get(id=internal_candidate.candidate_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                     description=description,image="/static/notifications/icon/candidate/Application_Submission.png",
        #                                                                     target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+'/agency')
        #     all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        #     stage_detail=''
        #     if not current_stage==None:
        #         if current_stage.name=='Interview' :
        #             stage_detail='Interview'
        #             description="You have one application to review for the job "+job_obj.job_title
        #             for i in all_assign_users:
        #                 if i.recruiter_type_internal:
        #                     if i.recruiter_id.id != request.user.id:
        #                         notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                             description=description,image="/static/notifications/icon/company/Application_Review.png",
        #                                                                             target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                                 job_obj.id))
        #         elif current_stage.name=='Application Review':
        #             stage_detail='Application Review'
        #             description="You have one application to review for the job "+job_obj.job_title
        #             for i in all_assign_users:
        #                 if i.recruiter_type_internal:
        #                     if i.recruiter_id.id != request.user.id:
        #                         notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                             description=description,image="/static/notifications/icon/company/Application_Review.png",
        #                                                                             target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                                 job_obj.id))
        #     to_email=list(set(to_email))
        #     mail_subject = "New Candidate submission"
        #     html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"New candidate has been submitted by "+request.user.first_name+" "+request.user.last_name+" – <a href="+header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(job_obj.id)+" >Applicant profile link.</a> Please login to review"})
        #     from_email = settings.EMAIL_HOST_USER
        #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
        #     msg.attach_alternative(html_content, "text/html")
        #     # try:
        #     msg.send()
        #     return redirect('agency:request_job_view', id=job_obj.id)
        return render(request, "agency/ATS/submit_candidate.html", context)

    else:
        return redirect('agency:agency_Profile')
def applied_candidate_form(request,int_cand_detail_id=None):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        edit_internal_candidate=''
        if int_cand_detail_id:
            edit_internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=int(int_cand_detail_id))
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

            models.InternalCandidateBasicDetail.objects.update_or_create(email=email,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                'user_id' : User.objects.get(id=request.user.id),
                'candidate_custom_id' : employee_id,
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
            add_skill=models.InternalCandidateBasicDetail.objects.get(email=email,agency_id = models.Agency.objects.get(user_id=request.user.id))
            for i in request.POST.getlist('source'):
                if i.isnumeric():
                    main_source_obj = CandidateModels.Source.objects.get(id=i)
                    add_skill.source=main_source_obj
                else:
                    source_cre=CandidateModels.Source.objects.create(name=i)
                    add_skill.source=source_cre
            for i in request.POST.getlist('tags'):
                if i.isnumeric():
                    main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                    add_skill.tags.add(main_skill_obj)
                else:
                    tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                    main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                    add_skill.categories.add(main_categ_obj)
            add_skill.save()
            if job_type=='company':
                job_obj=CompanyModels.JobCreation.objects.get(id=request.POST.get('jobid'))
                models.DailySubmission.objects.update_or_create(email=email,company_job_id=job_obj,internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                    'job_type':'company',
                    'internal_user' : models.InternalUserProfile.objects.get(InternalUserid=User.objects.get(id=request.user.id)),
                    'candidate_custom_id' : employee_id,
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
                    'secure_resume':secure_resume,
                    'expectedctc' : expectedctc,
                    'total_exper' : total_exper,
                    'update_at':datetime.datetime.now()
                })
                add_deatil=models.DailySubmission.objects.get(email=email,company_job_id=job_obj,internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_deatil.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_deatil.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_deatil.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_deatil.categories.add(main_categ_obj)
                add_deatil.save()
                if secure_resume_get=="Secure-Resume":
                    return redirect("agency:internal_redact_resume",internal_candidate_id = add_deatil.id)
                else:
                    mail_subject = '"Verify Detail" from Bidcruit'
                    current_site = get_current_site(request)
                    html_content = render_to_string('accounts/verify_detail.html', {'user': add_deatil,
                                                                                        'url':'verify_detail',
                                                                                        'email': email,
                                                                                        'domain': current_site.domain,
                                                                                        'uid': urlsafe_base64_encode(
                                                                                            force_bytes(add_deatil.pk))})
                    to_email = add_deatil.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return redirect('agency:all_candidates')
            if job_type=='agency':
                job_obj=models.JobCreation.objects.get(id=request.POST.get('jobid'))
                models.DailySubmission.objects.update_or_create(email=email,agency_job_id=job_obj,internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                    'job_type':'agency',
                    'internal_user' : models.InternalUserProfile.objects.get(InternalUserid=User.objects.get(id=request.user.id)),
                    'candidate_custom_id' : employee_id,
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
                    'secure_resume':secure_resume,
                    'expectedctc' : expectedctc,
                    'total_exper' : total_exper,
                    'update_at':datetime.datetime.now()
                })
                add_deatil=models.DailySubmission.objects.get(email=email,agency_job_id=job_obj,internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_deatil.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_deatil.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_deatil.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_deatil.categories.add(main_categ_obj)
                add_deatil.save()
                if secure_resume_get=="Secure-Resume":
                    return redirect("agency:internal_redact_resume",internal_candidate_id = add_deatil.id)
                else:
                    mail_subject = '"Verify Detail" from Bidcruit'
                    current_site = get_current_site(request)
                    html_content = render_to_string('accounts/verify_detail.html', {'user': add_deatil,
                                                                                        'url':'verify_detail',
                                                                                        'email': email,
                                                                                        'domain': current_site.domain,
                                                                                        'uid': urlsafe_base64_encode(
                                                                                            force_bytes(add_deatil.pk))})
                    to_email = add_deatil.email
                    from_email = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return redirect('agency:all_candidates')
        return render(request,'agency/ATS/add_candidate_basic_form.html',context)
    else:
        return redirect('agency:agency_Profile')
def dept_add_or_update_view(request):
    print("addddddddddddd viewwwwwwwwwwwwwwwwwwww")
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['departments'] = models.Department.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            if request.method == "POST":
                id= request.POST.get("department_id")
                department_name = request.POST.get("department_name")
                # department,created = models.Department.objects.get_or_create(name=department_name)
                try:
                    department = models.Department.objects.get(name__iexact=department_name)
                    created=False
                except:
                    created = True
                    print("no department with that id found")
                data = {}
                if created == False:
                    data["status"] = created
                    return HttpResponse(json.dumps(data))
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                if id == "null":
                    department = models.Department.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),name=department_name)
                    operation = "created"
                    role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                    get_admin = models.InternalUserProfile.objects.filter(role=role_id_get,
                                                                        agency_id=models.Agency.objects.get(
                                                                            user_id=request.user)).values_list(
                        'InternalUserid', flat=True)
                    
                    for i in get_admin:
                        description = request.user.first_name + "Add Department"
                        if i != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i), verb="Add Department",
                                        description=description,
                                        target_url="http://192.168.1.148:8000/agency/dept_add_or_update_view/")
                else:
                    department = models.Department.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=int(id))
                    department.name = department_name
                    department.save()
                    operation = "update"
                    role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                    get_admin = models.InternalUserProfile.objects.filter(role=role_id_get,
                                                                        agency_id=models.Agency.objects.get(
                                                                            user_id=request.user)).values_list(
                        'InternalUserid', flat=True)
                    for i in get_admin:
                        description = request.user.first_name + "Update Department"
                        if i != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Department",
                                        description=description,
                                        target_url="http://192.168.1.148:8000/agency/dept_add_or_update_view/")
                # if
                data["status"] = created
                data['operation'] = operation
                data['department_name'] =department.name
                data['department_id'] =department.id
                return HttpResponse(json.dumps(data))
            return render(request,"agency/ATS/add_department.html",context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def get_department(request):
    if request.method == "POST":
        id=request.POST.get("department_id")
        department = models.Department.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=int(id))
        data = {}
        data['department_id'] =department.id
        data['department_name'] =department.name
        return HttpResponse(json.dumps(data))

def delete_department(request):
    dept_id = request.POST.get("department_id")
    department = models.Department.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=int(dept_id))
    department.delete()
    return HttpResponse("true")

# category


def category_add_or_update_view(request):
    print("addddddddddddd viewwwwwwwwwwwwwwwwwwww")
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        if request.method == "POST":
            id= request.POST.get("category_id")
            category_name = request.POST.get("category_name")
            # department,created = models.Department.objects.get_or_create(name=department_name)
            try:
                category = models.CandidateCategories.objects.get(category_name__iexact=category_name,agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                category = models.CandidateCategories.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),category_name=category_name)
                operation = "created"
                role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                get_admin = models.InternalUserProfile.objects.filter(role=role_id_get,
                                                                        agency_id=models.Agency.objects.get(
                                                                            user_id=request.user)).values_list(
                    'InternalUserid', flat=True)
                    
                for i in get_admin:
                    description = request.user.first_name + "Add Categories"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Add Categories",
                                    description=description,
                                    target_url="#")
            else:
                category = models.CandidateCategories.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=int(id))
                category.category_name = category_name
                category.save()
                operation = "update"
                role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                        name="SuperAdmin")
                get_admin = models.InternalUserProfile.objects.filter(role=role_id_get,
                                                                        agency_id=models.Agency.objects.get(
                                                                            user_id=request.user)).values_list(
                    'InternalUserid', flat=True)
                for i in get_admin:
                    description = request.user.first_name + "Update category"
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Department",
                                    description=description,
                                    target_url="#")
            # if
            data["status"] = created
            data['operation'] = operation
            data['category_name'] =category.category_name
            data['category_id'] =category.id
            return HttpResponse(json.dumps(data))
        return render(request,"agency/ATS/add_category.html",context)
    else:
        return redirect('agency:agency_Profile')
    # else:
    #     return render(request, 'agency/ATS/not_permoission.html', context)

def get_candidate_category(request):
    if request.method == "POST":
        id=request.POST.get("category_id")
        category = models.CandidateCategories.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=int(id))
        data = {}
        data['category_id'] =category.id
        data['category_name'] =category.category_name
        return HttpResponse(json.dumps(data))

def delete_candidatecategory(request):
    dept_id = request.POST.get("category_id")
    category = models.CandidateCategories.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=int(dept_id))
    category.delete()
    return HttpResponse("true")




def role_list(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['role']=models.Role.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request, "agency/ATS/role_list.html",context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def role_permission(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        check_permission(request)
        context['role_model']=CandidateModels.PermissionsModel.objects.filter(is_agency=True)
        context['role_data']=CandidateModels.Permissions.objects.filter(is_agency=True)
        if request.method=='POST':
            role_name=request.POST.get('role-name')
            role_description=request.POST.get('role-description')
            role_create=models.Role.objects.create(name=role_name,description=role_description,status=True,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=request.user)
            permissions=models.RolePermissions.objects.create(role=role_create,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=request.user)
            for per_id in request.POST.getlist('permissionname'):
                permissions.permission.add(CandidateModels.Permissions.objects.get(id=per_id))
            role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                name="SuperAdmin")
            get_admin = models.InternalUserProfile.objects.filter(role=role_id_get,
                                                                agency_id=models.Agency.objects.get(
                                                                    user_id=request.user)).values_list(
                'InternalUserid', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            for i in get_admin:
                description = request.user.first_name + "Add Role"
                if i != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i), verb="Add Role",
                                description=description,
                                target_url="http://192.168.1.148:8000/agency/role_list/")
            return redirect('agency:role_list')
        return render(request, "agency/ATS/role_permission.html",context)
    else:
        return redirect('agency:agency_Profile')

def role_permission_update(request,id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        check_permission(request)
        context['role_model']=CandidateModels.PermissionsModel.objects.filter(is_agency=True)
        role_model=CandidateModels.PermissionsModel.objects.filter(is_agency=True).values_list('id')
        context['role_data']=CandidateModels.Permissions.objects.filter(permissionsmodel__in=role_model,is_agency=True)
        context['agency_role'] = models.Role.objects.get(id=id)
        agency_permission = models.RolePermissions.objects.get(role=context['agency_role'])
        agency_permission = agency_permission.permission.all()
        context['agency_permission']=[i.id for i in agency_permission]
        if request.method=='POST':
            role_name=request.POST.get('role-name')
            role_description=request.POST.get('role-description')
            models.Role.objects.filter(id=id,agency_id=models.Agency.objects.get(user_id=request.user.id)).update(name=role_name,description=role_description)
            permissions=models.RolePermissions.objects.get(role=id,agency_id=models.Agency.objects.get(user_id=request.user.id))
            permissions.permission.clear()
            for per_id in request.POST.getlist('permissionname'):
                print('permissions.permission', permissions.permission.all())
                permissions.permission.add(CandidateModels.Permissions.objects.get(id=per_id))
            role_id_get = models.Role.objects.get(agency_id=models.Agency.objects.get(user_id=request.user),
                                                name="SuperAdmin")
            get_admin = models.InternalUserProfile.objects.filter(role=role_id_get,
                                                                agency_id=models.Agency.objects.get(
                                                                    user_id=request.user)).values_list(
                'InternalUserid', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"
            for i in get_admin:
                description = request.user.first_name + "Update Role"
                if i != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Role",
                                description=description,
                                target_url="http://192.168.1.148:8000/agency/role_list/")
            return redirect('agency:role_list')
        return render(request, "agency/ATS/role_permission_update.html",context)
    else:
        return redirect('agency:agency_Profile')

def applied_candidates_view(request, id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        job_obj = CompanyModels.JobCreation.objects.get(id=id)
        print(job_obj,'====',job_obj.company_id,'====',models.Agency.objects.get(user_id=request.user.id))
        agency_submit_candidate = CompanyModels.AssociateCandidateAgency.objects.filter(job_id=job_obj,
                                                                                company_id=job_obj.company_id,agency_id=models.Agency.objects.get(user_id=request.user.id)).values_list(
            'candidate_id', flat=True)
        candidates_array = agency_submit_candidate

        candidate_job_apply_detail = CandidateModels.candidate_job_apply_detail.objects.filter(
            candidate_id__in=candidates_array)
        print("==========", agency_submit_candidate, )
        candidate_stages_data = []
        secure = False
        candidatetype = ''
        candidate_fname = ''
        candidate_lname = ''
        resume = ''
        contactno = ''
        for candidate_id in candidates_array:
            stages = CompanyModels.CandidateJobStagesStatus.objects.filter(
                company_id=job_obj.company_id,
                candidate_id=User.objects.get(id=candidate_id),
                job_id=job_obj).order_by('sequence_number')
            # secure_resume
            current_stage = ''
            if len(stages.filter(status=1))==0:
                current_stage = 'Waiting For Stage'
            else:
                current_stage = stages.filter(status=1)[0].stage.name
            candidatetype = 'Internal'
            candidate_detail = models.InternalCandidateBasicDetail.objects.get(
                candidate_id=User.objects.get(id=candidate_id), agency_id=models.Agency.objects.get(user_id=request.user.id))
            resume = candidate_detail.resume.url
            contactno = candidate_detail.contact
            candidate_fname = candidate_detail.candidate_id.first_name + ' ' + candidate_detail.candidate_id.last_name
            candidate_lname = candidate_detail.candidate_id.last_name
            secure = False
            data = {'id': User.objects.get(id=candidate_id),'current_stage':current_stage, 'candidate_detail':candidate_detail,'stages': stages, 'secure': secure,
                    'candidatetype': candidatetype, 'contactno': contactno, 'resume': resume,
                    'candidate_fname': candidate_fname,'candidate_lname': candidate_lname}
            candidate_stages_data.append(data)
            print(len(candidate_stages_data))
        context['candidates']= candidate_job_apply_detail
        context['candidate_stages_data']= candidate_stages_data
        context['job_obj']= job_obj
        context['job_id']= job_obj.id
        return render(request, "agency/ATS/applied-candidate-view.html",context)
    else:
        return redirect('agency:agency_Profile')



from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.safestring import mark_safe
def company_portal_candidate_tablist(request, candidate_id, job_id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        job_obj = CompanyModels.JobCreation.objects.get(id=job_id)
        candidate_obj = User.objects.get(id=candidate_id)
        chat=''
        groupmessage=''
        uniquecode=''
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
        if request.method == 'POST':
            if 'schedule_interview' in request.POST:
                if request.POST.get('interview_stage'):
                    stage_obj = CompanyModels.CandidateJobStagesStatus.objects.get(id=request.POST.get('interview_stage'))
                    print('interviewers', request.POST.getlist('interviewers'))
                    in_time = datetime.datetime.strptime(request.POST.get('interview_time'), "%I:%M %p")
                    out_time = datetime.datetime.strftime(in_time, "%H:%M")
                    meridiem = request.POST.get('interview_time').split(' ')[1]
                    interview_template = CompanyModels.InterviewTemplate.objects.get(company_id=stage_obj.company_id,
                                                                            template_id=stage_obj.template)
                    schedule_obj, created = CompanyModels.InterviewSchedule.objects.update_or_create(candidate_id=candidate_obj,
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
                                                                                                }
                                                                                            )
                    for participant in request.POST.getlist('interviewers'):
                        participant_obj = User.objects.get(id=participant)
                        schedule_obj.participants.add(participant_obj)
                else:
                    return HttpResponse('Something Went Wrong')

            elif 'withdraw_candidate' in request.POST:
                CompanyModels.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=job_obj.company_id,
                                                                defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})

            elif 'hire_candidate' in request.POST:
                CompanyModels.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=job_obj.company_id,
                                                                defaults={
                                                                    'hire_by': User.objects.get(id=request.user.id),
                                                                    'is_hired': True})
                job_stages = CompanyModels.CandidateJobStagesStatus.objects.filter(
                    company_id=CompanyModels.Company.objects.get(id=job_obj.company_id),
                    candidate_id=candidate_obj,
                    job_id=job_obj).order_by('sequence_number').last()
                job_stages.status = 1
                job_stages.save()

            elif 'reenter_candidate' in request.POST:
                CompanyModels.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                company_id=job_obj.company_id,
                                                                defaults={
                                                                    'withdraw_by': None,
                                                                    'is_withdraw': False})
            else:
                stage_obj = CompanyModels.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
                if 'shortlist' in request.POST:
                    stage_obj.action_performed = True
                    stage_obj.status = 2
                    stage_obj.save()
                    new_sequence_no = stage_obj.sequence_number + 1
                    if CompanyModels.CandidateJobStagesStatus.objects.filter(job_id=job_obj, candidate_id=candidate_obj,
                                                            sequence_number=new_sequence_no).exists():
                        new_stage_status = CompanyModels.CandidateJobStagesStatus.objects.get(job_id=job_obj, candidate_id=candidate_obj,
                                                                                    sequence_number=new_sequence_no)
                        new_stage_status.status = 1
                        new_stage_status.save()

                if 'reject' in request.POST:
                    stage_obj.status = -1
                    stage_obj.action_performed = True
                    stage_obj.assessment_done = True
                    stage_obj.save()

                if 'onhold' in request.POST:
                    stage_obj.status = 3
                    stage_obj.action_performed = False
                    stage_obj.save()

        candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(candidate_id=candidate_obj)
        internal_users = CompanyModels.Employee.objects.filter(company_id=job_obj.company_id)
        stages_status = CompanyModels.CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                                    candidate_id=candidate_obj,
                                                                    job_id=job_obj).order_by('sequence_number')
        interview_schedule_data = None
        job_offer_data = None
        stages_data = []
        for stage in stages_status:
            stage_dict = {'stage': stage, 'result': ''}

            if stage.stage.name == 'Interview':
                print('\n\nin Interview')
                interview_schedule_obj = CompanyModels.InterviewSchedule.objects.filter(candidate_id=candidate_obj,job_id=job_obj,
                                                        company_id=stage.company_id,
                                                        template=stage.template,
                                                        job_stages_id=stage)
                if interview_schedule_obj.exists():
                    interview_schedule_data = interview_schedule_obj[0]
            if stage.stage.name == 'Job Offer':
                print('\n\nin Job Offer')
                job_offer_obj = CompanyModels.JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
                                                                                company_id=stage.company_id,
                                                                                job_stages_id=stage)
                if job_offer_obj.exists():
                    job_offer_data = job_offer_obj[0]
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
                    mcq_test_result = CandidateModels.Mcq_Exam_result.objects.get(company_id=stage.company_id,
                                                                                candidate_id=stage.candidate_id,
                                                                                job_id=job_obj,
                                                                                template=stage.template)
                    stage_dict['result'] = mcq_test_result

                if stage.stage.name == 'Descriptive Test':
                    descriptive_result = CandidateModels.Descriptive_Exam_result.objects.get(company_id=stage.company_id,
                                                                                            candidate_id=stage.candidate_id,
                                                                                            job_id=job_obj,
                                                                                            template=stage.template)
                    stage_dict['result'] = descriptive_result

                if stage.stage.name == 'Image Test':
                    image_result = CandidateModels.Image_Exam_result.objects.get(company_id=stage.company_id,
                                                                                candidate_id=stage.candidate_id,
                                                                                job_id=job_obj,
                                                                                template=stage.template)
                    stage_dict['result'] = image_result

                if stage.stage.name == 'Coding Test':
                    exam_config = CompanyModels.CodingExamConfiguration.objects.get(template_id=stage.template)
                    coding_result = CandidateModels.Coding_Exam_result.objects.get(candidate_id=stage.candidate_id,
                                                                                company_id=stage.company_id,
                                                                                template=stage.template,
                                                                                job_id=stage.job_id)
                    stage_dict['result'] = coding_result
                    # if exam_config.technology == 'backend':
                    #
                    # else:
                    #     all_front_end_codes = CandidateModels.CodingFrontEndExamFill.objects.filter(candidate_id=stage.candidate_id,
                    #                                                                                 job_id=stage.job_id,
                    #                                                                                 template=stage.template,
                    #                                                                                 company_id=stage.company_id).order_by('exam_question_id')
                    #     stage_dict['result'] = all_front_end_codes

            stages_data.append(stage_dict)

        collaboration_obj = CompanyModels.Collaboration.objects.filter(company_id=job_obj.company_id, candidate_id=candidate_obj,
                                                                job_id=job_obj)

        candidate_job_status = None
        if CompanyModels.CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
            candidate_job_status = CompanyModels.CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)
        candidate_education = CandidateModels.CandidateEducation.objects.filter(candidate_id=candidate_obj)
        candidate_experience = CandidateModels.CandidateExperience.objects.filter(candidate_id=candidate_obj)
        candidate_certification =CandidateModels.CandidateCertificationAttachment.objects.filter(candidate_id=candidate_obj)
        candidate_award=CandidateModels.CandidateAward.objects.filter(candidate_id=candidate_obj)
        candidate_portfolio=CandidateModels.CandidatePortfolio.objects.filter(candidate_id=candidate_obj)
        candidate_preferences=CandidateModels.CandidateJobPreference.objects.filter(candidate_id=candidate_obj)
        context['job_obj']= job_obj
        context['candidate_obj']= candidate_obj
        context['candidate_detail']= candidate_detail
        context['interview_schedule_data']= interview_schedule_data
        context['job_offer_data']= job_offer_data
        context['internal_users']= internal_users
        context['stages_status']= stages_status
        context['stages_data']= stages_data
        context['collaboration_obj']= collaboration_obj
        context['candidate_job_status']=candidate_job_status
        context['chatObject']= chat
        context['groupmessage']=groupmessage
        context['chat_id_json']= uniquecode
        return render(request, "agency/ATS/company-portal-candidate-tablist.html",context)
    else:
        return redirect('agency:agency_Profile')


def change_employee_status(request):
    if request.method == "POST":
        employee_obj = models.InternalUserProfile.objects.get(id=request.POST.get('employee_id'))
        employee_obj.InternalUserid.is_active = not employee_obj.InternalUserid.is_active
        employee_obj.InternalUserid.save()
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

def candidate_request(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):    
        data=[]
        requested_candidate=None
        if models.InternalUserProfile.objects.filter(InternalUserid=request.user,agency_id=models.Agency.objects.get(user_id=request.user),
                                                        role__name='SuperAdmin'):
            requested_candidate= models.CandidateSecureData.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),is_request=True).order_by('-update_at')
        else:
            print(request.user.id)
            requested_candidate = models.CandidateSecureData.objects.filter(user_id=request.user,
                agency_id=models.Agency.objects.get(user_id=request.user.id), is_request=True).order_by('-update_at')
        for requested_candidates in requested_candidate:
            request_data={}
            get_company_profile = CompanyModels.CompanyProfile.objects.get(company_id=requested_candidates.company_id)
            internalcandiatedetail=models.InternalCandidateBasicDetail.objects.get(candidate_id=requested_candidates.candidate_id,agency_id=models.Agency.objects.get(user_id=request.user.id))
            request_data['company_name']=requested_candidates.company_id.company_id.company_name
            request_data['company_industry'] = get_company_profile.industry_type.name
            request_data['company_city'] = get_company_profile.city.city_name
            request_data['company_logo'] = get_company_profile.company_logo.url
            request_data['candidate_name'] = requested_candidates.candidate_id.first_name+' '+requested_candidates.candidate_id.last_name
            request_data['candidate_candidateid'] = requested_candidates.candidate_id.id
            request_data['candidate_id'] = requested_candidates.id
            request_data['candidate_secureid'] = internalcandiatedetail.candidate_custom_id
            request_data['candidate_gender'] = internalcandiatedetail.gender
            request_data['candidate_designation'] = internalcandiatedetail.designation
            request_data['candidate_dateofsubmission'] = requested_candidates.create_at
            request_data['request_accept'] = requested_candidates.is_accepted
            data.append(request_data)
        context['datas']=data
        return render(request, "agency/ATS/all-requests.html",context)
    else:
        return redirect('agency:agency_Profile')


def request_for_detail_action(request,internalid,candidateid):
    if request.method=='POST':
        agency_candidate=models.CandidateSecureData.objects.filter(id=internalid,agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                    candidate_id =User.objects.get(id=candidateid)).update(is_accepted=True,update_at=datetime.datetime.now())

        # for i in get_admin:
        #     description = request.user.first_name + "Update Role"
        #     if i != request.user.id:
        #         notify.send(request.user, recipient=User.objects.get(id=i), verb="Update Role",
        #                     description=description,
        #                     target_url="http://192.168.1.148:8000/company/role_list/")
        return redirect('agency:candidate_request')
    else:
        return HttpResponse(False)


def create_employee_id():
    link = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(9)])
    if models.InternalUserProfile.objects.filter(unique_id=link).exists():
        return create_employee_id()
    else:
        return link

def invite_candidate(request,id):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        if models.InternalUserProfile.objects.filter(unique_id=id).exists():
            context['notice_period']= CandidateModels.NoticePeriod.objects.all()
            employee_obj = models.InternalUserProfile.objects.get(unique_id=id)
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
                                                                        agency_id=employee_obj.agency_id, defaults={
                        'user_id': employee_obj.user_id,
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
                return render(request,'agency/ATS/thankyou.html')
            return render(request,'agency/ATS/candidate_invite.html',context)
        else:
            return render(request, 'accounts/404.html')
    else:
        return redirect('agency:agency_Profile')

def verify_candidate(request,id):
    context={}
    context['notice_period']= CandidateModels.NoticePeriod.objects.all()
    candid_data = models.CandidateTempDatabase.objects.get(id=id)
    context['candid_data'] = candid_data
    if request.method == 'POST':
        fname = request.POST.get('f-name')
        lname = request.POST.get('l-name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        if request.FILES.get('resume'):
            resume = request.FILES.get('resume')
        else:
            if candid_data.resume:
                resume = candid_data.resume
            else:
                resume = None
        secure_resume_get = request.POST.get('secure-resume')
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

        temp_obj,created = models.InternalCandidateBasicDetail.objects.update_or_create(email=candid_data.email,
                                                                agency_id=candid_data.agency_id, defaults={
                'user_id': candid_data.user_id,
                'candidate_custom_id':request.POST.get('candidate_c_id'),
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
        for i in request.POST.getlist('source'):
            if i.isnumeric():
                main_source_obj = CandidateModels.Source.objects.get(id=i)
                temp_obj.source=main_source_obj
            else:
                source_cre=CandidateModels.Source.objects.create(name=i)
                temp_obj.source=source_cre
        for i in request.POST.getlist('tags'):
            if i.isnumeric():
                main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                temp_obj.tags.add(main_skill_obj)
            else:
                tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
                temp_obj.tags.add(tag_cre)
        
        for i in request.POST.getlist('candidate_category'):
            if i.isnumeric():
                main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                temp_obj.categories.add(main_categ_obj)
        if User.objects.filter(email=email.lower()).exists():
            temp_obj.candidate_id = User.objects.get(email=email.lower())
        temp_obj.save()
        models.CandidateTempDatabase.objects.get(id=id).delete()
        if secure_resume_get=="Secure-Resume":
            return redirect("agency:redact_resume",internal_candidate_id = temp_obj.id)
        else:
            return redirect('agency:all_candidates')
    return render(request, 'agency/ATS/verify_candidate.html', context)



def tracker(request):
    context={}
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        jobwise=[]
        candidatewise=[]
        get_assign_job=CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('job_id')
        get_candidate_job=CompanyModels.AssociateCandidateAgency.objects.filter(agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).values_list('candidate_id__id',flat=True)
        # job_list=models.Tracker.objects.filter(company_id=models.Company.objects.get(user_id=User.objects.get(id=request.user.id)),job_id__close_job=False).distinct('job_id')
        
        for i in get_assign_job:
            jobdetail={'job_id':i.job_id.id,'job_title':i.job_id.job_title,'company':i.job_id.company_id.company_id.company_name,'remote_job':i.job_id.remote_job,
                        'exp':i.job_id.experience_year_max,'opening_date':i.job_id.publish_at,'job_type':i.job_id.job_type.name}
            
            result = models.AssociateJob.objects.filter(job_id=i.job_id).count()
            jobdetail['qpplicant']=result
            if i.job_id.salary_as_per_market:
                jobdetail['salary_range']='As per market' 
            else:
                jobdetail['salary_range']=i.job_id.min_salary+' LAP to ' +i.job_id.max_salary+' LAP'
            jobdetail['candidates']=[]
            jobwise_tracker = CompanyModels.Tracker.objects.filter(job_id=i.job_id).order_by('-update_at')
            for job in jobwise_tracker:
                if job.candidate_id.id in  get_candidate_job:
                    if CompanyModels.JobOffer.objects.filter(job_id=job.job_id,candidate_id=job.candidate_id,is_accepted=True).exists():
                        pass
                    else:
                        jobdetail['candidates'].append({'candidatefname':job.candidate_id.first_name,'candidatelname':job.candidate_id.last_name,'current':job.current_stage,'candidateid':job.candidate_id.id,
                                                        'next':job.next_stage,'action':job.action_required,'currentcompleted':job.currentcompleted,'reject':job.reject,'withdraw':job.withdraw})
            jobwise.append(jobdetail)
        #     print("=========",jobdetail)
        context['job_tracker']=jobwise
    
        candidate_list=CompanyModels.Tracker.objects.filter(job_id__close_job=False,candidate_id__in=get_candidate_job).distinct('candidate_id')
        for i in candidate_list:
            if i.candidate_id.id in get_candidate_job:
                getprofile=CandidateModels.candidate_job_apply_detail.objects.get(candidate_id=i.candidate_id)
                if CompanyModels.JobOffer.objects.filter(job_id=i.job_id,candidate_id=i.candidate_id,is_accepted=True).exists():
                    pass
                else:
                    candidatedetail={'candidatefname':i.candidate_id.first_name,'candidatelname':i.candidate_id.last_name,'designation':getprofile.designation,
                                'email':i.candidate_id.email,'contact':getprofile.contact,'total_exper':getprofile.total_exper,'notice':getprofile.notice.notice_period,
                                'current':str(getprofile.ctc)+' LAP','expectedctc':str(getprofile.expectedctc)+' LAP'}
                    candidatedetail['jobs']=[]
                    candidatewise_tracker = CompanyModels.Tracker.objects.filter(candidate_id=i.candidate_id).order_by('-update_at')
                    for job in candidatewise_tracker:
                        candidatedetail['jobs'].append({'job_id':job.job_id.id,'job_title':job.job_id.job_title,'company':job.job_id.company_id.company_id.company_name,'current':job.current_stage,
                                                        'next':job.next_stage,'action':job.action_required,'currentcompleted':job.currentcompleted,'reject':job.reject,'withdraw':job.withdraw})
            candidatewise.append(candidatedetail)
        context['candidate_tracker']=candidatewise
        return render(request,'agency/ATS/job-tracker.html',context)

    else:
        return redirect('agency:agency_Profile')


# =============================== mcq subject and question


def mcq_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.MCQ_subject.objects.create(subject_name=subject_name['subject_name'],
                                                             agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                                                           agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                                             agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def mcq_subject_list(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['subject']= models.MCQ_subject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),)
            return render(request, 'agency/ATS/mcq_subject.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')


def preview_mcq(request, id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                data=models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),mcq_subject=models.MCQ_subject.objects.get(id=id))
                context['questions']=data
            else:
                data = None
                context['questions'] = data
            return render(request, 'agency/ATS/mcq_view.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def add_mcq(request,id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            question_get=models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),mcq_subject=models.MCQ_subject.objects.get(id=id),created_at__date=datetime.datetime.today().date())
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
                create_que_option=models.mcq_Question.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                    user_id=User.objects.get(id=request.user.id),
                                                                    mcq_subject=models.MCQ_subject.objects.get(id=id),
                                                                    question_description =question,
                                                                    question_level =CandidateModels.QuestionDifficultyLevel.objects.get(id=int(level)),
                                                                    correct_option =answer,option_a =option1 ,option_b =option2,option_c =option3 ,option_d =option4)
                create_que_option.save()
                return redirect('agency:add_mcq',id)
            context['sub_name']=subject_obj.subject_name
            context['level'] = level
            context['question'] = question
            return render(request, 'agency/ATS/mcq_add.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def mcq_delete_question(request):
    if request.method == 'POST':
        question_data = json.loads(request.body.decode('UTF-8'))
        # print(subject_data)
        models.mcq_Question.objects.get(id=int(question_data['question_id']),
                                             agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


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
        update_que=models.mcq_Question.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=queid)
        update_que.question_description =question
        update_que.question_level =CandidateModels.QuestionDifficultyLevel.objects.get(id=int(level))
        update_que.correct_option =answer
        update_que.option_a =option1
        update_que.option_b =option2
        update_que.option_c =option3
        update_que.option_d =option4
        update_que.save()
        return redirect('agency:preview_mcq',id=update_que.mcq_subject.id)


def get_mcq_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        que_get=models.mcq_Question.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=que_id)
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



# ===========================Image based question bank
def image_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.ImageSubject.objects.create(subject_name=subject_name['subject_name'],
                                                        agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_id.subject_name}
        return HttpResponse(json.dumps(data))


def image_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.ImageSubject.objects.get(id=int(subject_data['sub_id']),
                                                             agency_id=models.Agency.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def image_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.ImageSubject.objects.get(id=int(subject_data['sub_id']),
                                               agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def image_based_all(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['subject'] = models.ImageSubject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request,'agency/ATS/image_based_all.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')
def image_based_question_view(request,id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            if models.ImageSubject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),id=id).exists():
                subject_obj = models.ImageSubject.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=id)
                
                questions = models.ImageOption.objects.filter(subject_id=subject_obj)
                context['sub_id']=id
                context['sub_name']=subject_obj.subject_name
                context['questions'] = questions
            return render(request, 'agency/ATS/image_based_question_view.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def image_based_question_add(request,id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        subject_obj = models.ImageSubject.objects.get(id=id)
        image_question=models.ImageQuestion.objects.filter(subject=subject_obj,agency_id=models.Agency.objects.get(user_id=request.user.id),created_at__date=datetime.datetime.today().date())
        image_que=[]
        for image_questions in image_question:
            if models.ImageOption.objects.filter(question_id=image_questions.id,agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
                option=models.ImageOption.objects.get(question_id=image_questions.id,agency_id=models.Agency.objects.get(user_id=request.user.id))
                image_que.append({'question':image_questions.image_que_description,'que_file':image_questions.question_file,'correct_option':option.answer,'option1':option.option1,'option1_file':option.file1,'option2':option.option2,'option2_file':option.file2,'option3':option.option3,'option3_file':option.file3,'option4':option.option4,'option4_file':option.file4,'question_level':image_questions.question_level.level_name})
        level = CandidateModels.QuestionDifficultyLevel.objects.all()
        if request.method == 'POST':
            print('123',request.POST)
            print('\n\nfiles',request.FILES)
            level=request.POST.get('question_level')
            img_question_obj = models.ImageQuestion.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                user_id=User.objects.get(id=request.user.id),
                                                subject=subject_obj,
                                                question_level=CandidateModels.QuestionDifficultyLevel.objects.get(id=int(level)),
                                                image_que_description=request.POST.get('question'),
                                                question_file=request.FILES.get('question_file'))

            options_obj = models.ImageOption.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
        return render(request, 'agency/ATS/image_based_question_add.html',context)
    else:
        return redirect('agency:agency_Profile')

def delete_image_question(request):
    if request.method == 'POST':
        img_data = json.loads(request.body.decode('UTF-8'))
        que_obj = models.ImageQuestion.objects.get(id=img_data['que_id'])
        models.ImageOption.objects.get(question_id=que_obj).delete()
        que_obj.delete()
        return HttpResponse(True)



# ============================coding
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
                                                         agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                                                       agency_id=models.Agency.objects.get(user_id=request.user.id))
        subject_get.api_subject_id = CandidateModels.CodingApiSubjects.objects.get(id=subject_data['api_sub_id'])
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def coding_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.CodingSubject.objects.get(id=int(subject_data['sub_id']),
                                         agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def coding_add_category(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('UTF-8'))

        category_id = models.CodingSubjectCategory.objects.create(category_name=data['category_name'],
                                                                  subject_id=models.CodingSubject.objects.get(
                                                                      id=data['sub_id']),
                                                                  agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                  user_id=User.objects.get(id=request.user.id))
        category_id.save()
        data = {'status': True, 'category_id': category_id.id, 'category_name': category_id.category_name}
        return HttpResponse(json.dumps(data))


def coding_update_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        category_get = models.CodingSubjectCategory.objects.get(id=int(category_data['cat_id']),
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id))
        category_get.category_name = category_data['cat_name']
        category_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def coding_delete_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        models.CodingSubjectCategory.objects.get(id=int(category_data['category_id']),
                                                 agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def coding_subject_all(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['subject'] = models.CodingSubject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request, 'agency/ATS/coding_subject_all.html', context)
    else:
        return redirect('agency:agency_Profile')

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
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            subject = models.CodingSubject.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id), id=id)
            categ = models.CodingSubjectCategory.objects.get(subject_id=subject)
            return redirect('agency:coding_question_add',categ.id)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def coding_question_add(request, id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        category_obj = models.CodingSubjectCategory.objects.get(id=id)
        coding_ques=models.CodingQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                category_id=category_obj,created_at__date=datetime.datetime.today().date())
        if request.method == 'POST':
            category_obj = models.CodingSubjectCategory.objects.get(id=id)
            coding_data = json.loads(request.body.decode('UTF-8'))
            question_obj = models.CodingQuestion.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
        return render(request, 'agency/ATS/coding_question_add.html', context)
    else:
        return redirect('agency:agency_Profile')

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
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                                                            agency_id=models.Agency.objects.get(user_id=request.user.id))
            context['questions']=questions
            context['category_id'] = categ_obj.id
            return render(request, 'agency/ATS/coding_question_view.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')


def delete_coding_question(request):
    if request.method == 'POST':
        coding_data = json.loads(request.body.decode('UTF-8'))
        models.CodingQuestion.objects.get(id=coding_data['que_id']).delete()
        return HttpResponse(True)



def get_coding_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        que_get=models.CodingQuestion.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=que_id)
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
        update_que=models.CodingQuestion.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=queid)
        update_que.question_type =que_type
        update_que.coding_que_title =title
        update_que.coding_que_description =question
        update_que.save()
        return redirect('agency:coding_question_view',id=update_que.category_id.id)



# ============================descriptive

def descriptive_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        subject_id = models.Descriptive_subject.objects.create(subject_name=subject_name['subject_name'],
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_id.subject_name}
        return HttpResponse(json.dumps(data))


def descriptive_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.Descriptive_subject.objects.get(id=int(subject_data['sub_id']),
                                                             agency_id=models.Agency.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def descriptive_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.Descriptive_subject.objects.get(id=int(subject_data['sub_id']),
                                               agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def descriptive_list(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['subject'] = models.Descriptive_subject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request,'agency/ATS/descriptive_all.html',context)
    else:
        return redirect('agency:agency_Profile')

def descriptive_add(request,id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        subject_obj = models.Descriptive_subject.objects.get(id=id)
        descriptive_que=models.Descriptive.objects.filter(subject=subject_obj,
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),created_at__date=datetime.datetime.today().date())
        if request.method == 'POST':
            descriptive_data = json.loads(request.body.decode('UTF-8'))
            descriptive_obj = models.Descriptive.objects.create(subject=subject_obj,
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                paragraph_description=descriptive_data['que'])
            data = {'id': descriptive_obj.id, 'paragraph_description': descriptive_obj.paragraph_description}
            return HttpResponse(json.dumps(data))
        context['sub_id']= id
        context['subject_obj']=subject_obj
        context['descriptive_que']=descriptive_que
        return render(request,'agency/ATS/descriptive_add.html', context)
    else:
        return redirect('agency:agency_Profile')

def descriptive_view(request,id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            return render(request,'agency/ATS/descriptive_view.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def delete_descriptive_question(request):
    if request.method == 'POST':
        desc_data = json.loads(request.body.decode('UTF-8'))
        models.Descriptive.objects.get(id=desc_data['que_id'],agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)

def get_descriptive_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        que_get=models.Descriptive.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=que_id)
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
        update_que=models.Descriptive.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=queid)
        update_que.paragraph_description =question
        update_que.save()
        return redirect('agency:descriptive_view',id=update_que.subject.id)






# ==================================audio


def audio_add_subject(request):
    if request.method == 'POST':
        subject_name = json.loads(request.body.decode('UTF-8'))
        print(subject_name)
        subject_id = models.Audio_subject.objects.create(subject_name=subject_name['subject_name'],
                                                        agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                        user_id=User.objects.get(id=request.user.id))
        subject_id.save()
        data = {'status': True, 'subject_id': subject_id.id, 'subject_name': subject_id.subject_name}
        return HttpResponse(json.dumps(data))


def audio_update_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        subject_get = models.Audio_subject.objects.get(id=int(subject_data['sub_id']),
                                                             agency_id=models.Agency.objects.get(user_id=request.user.id))
        subject_get.subject_name = subject_data['sub_name']
        subject_get.save()
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def audio_delete_subject(request):
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        models.Audio_subject.objects.get(id=int(subject_data['sub_id']),
                                               agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def audio_list(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            context['subject'] = models.Audio_subject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            return render(request,'agency/ATS/audio_all.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def audio_add(request,id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        subject_obj = models.Audio_subject.objects.get(id=id)
        audio_que=models.Audio.objects.filter(subject=subject_obj,
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),created_at__date=datetime.datetime.today().date())
        if request.method == 'POST':
            audio_data = json.loads(request.body.decode('UTF-8'))
            audio_obj = models.Audio.objects.create(subject=subject_obj,
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                paragraph_description=audio_data['que'])
            data = {'id': audio_obj.id, 'paragraph_description': audio_obj.paragraph_description}
            return HttpResponse(json.dumps(data))
        context['sub_id']= id
        context['audio_que']=audio_que
        context['sub_name']=subject_obj.subject_name
        return render(request,'agency/ATS/audio_add.html', context)
    else:
        return redirect('agency:agency_Profile')

def audio_view(request,id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                questions = models.Audio.objects.filter(subject=models.Audio_subject.objects.get(id=id),agency_id=models.Agency.objects.get(user_id=request.user.id))
                context['questions']=questions
                context['sub_id'] = id
            else:
                questions = None
                context['questions'] = questions
                context['sub_id'] = id
            return render(request,'agency/ATS/audio_view.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def delete_audio_question(request):
    if request.method == 'POST':
        desc_data = json.loads(request.body.decode('UTF-8'))
        models.Audio.objects.get(id=desc_data['que_id']).delete()
        return HttpResponse(True)


def get_audio_question(request):
    data={}
    if request.method=="POST":
        que_id = json.loads(request.body.decode('UTF-8'))
        print(que_id)
        # get_audiopaper=models.AudioExamQuestionUnit.objects.filter(question=models.Audio.objects.get(id=que_id)).values_list('template')
        # get_workflow=models.WorkflowStages.objects.filter(template__in=get_audiopaper).values_list('workflow_id')
        # get_job=models.JobWorkflow.objects.filter(workflow_id__in=get_workflow).values_list('job_id')
        # job_status=models.JobCreation.objects.filter(id__in=get_job)
        # print('template',get_audiopaper)
        # print('get_workflow',get_workflow)
        # print('get_job',get_job)
        active=False
        # for jobstatus in job_status:
        #     print(jobstatus.status.name)
        #     if jobstatus.status.name=='In Progress':
        #         active=True
        print(active)
        if not active:
            que_get=models.Audio.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=que_id)
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
        update_que=models.Audio.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),id=queid)
        update_que.paragraph_description =question
        update_que.save()
        return redirect('agency:audio_view',id=update_que.subject.id)
    


# =========================================================template creation


def template_listing(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                agency_id=models.Agency.objects.get(user_id=request.user.id)).order_by('id')
            context['get_category']= get_category
            print('get_category>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',get_category)
            get_templates = models.Template_creation.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                                                                        agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                    return redirect('agency:job_creation_template')
                # if str(stage.name).upper() == 'JCR':
                #     return redirect('agency:jcr')
                if str(stage.name).upper() == 'PREREQUISITES':
                    return redirect('agency:pre_requisites')
                if str(stage.name).upper() == 'MCQ TEST':
                    return redirect('agency:add_exam_template')
                if str(stage.name).upper() == 'CODING TEST':
                    return redirect('agency:coding_exam_configuration')
                if str(stage.name).upper() == 'DESCRIPTIVE TEST':
                    return redirect('agency:descriptive_exam_template')
                if str(stage.name).upper() == 'IMAGE TEST':
                    return redirect('agency:image_add_exam_template')
                if str(stage.name).upper() == 'AUDIO TEST':
                    return redirect('agency:audio_exam_template')
                # if str(stage.name).upper() == 'INTERVIEW':
                #     return redirect('agency:interview_template')
                if str(stage.name).upper() == 'CUSTOM':
                    return redirect('agency:custom_template')
            return render(request, 'agency/ATS/template-creation.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')
def add_category(request):
    if request.method == 'POST':
        category_name = json.loads(request.body.decode('UTF-8'))
        print("======================================", category_name)
        create_stage_id = models.TemplateCategory.objects.create(name=category_name['add_category'],
                                                                 stage=CandidateModels.Stage_list.objects.get(
                                                                     id=int(category_name['stage_id'])),
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                                            agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
        return HttpResponse(True)


def update_category(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        print(category_data)
        category_get = models.TemplateCategory.objects.get(id=int(category_data['cat_id']),
                                                           stage=CandidateModels.Stage_list.objects.get(
                                                               id=int(category_data['stage_id'])),
                                                           agency_id=models.Agency.objects.get(user_id=request.user.id))
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
            agency_id=models.Agency.objects.get(user_id=request.user.id))
        print("============------", category_get)
        data = {}
        data['status'] = True
        data['category_get'] = serializers.serialize('json', category_get)
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)


def delete_template(request):
    data={}
    if request.method == 'POST':
        template_data = json.loads(request.body.decode('UTF-8'))
        # get_workflow=models.WorkflowStages.objects.filter(template=int(template_data['template_id'])).values_list('workflow_id')
        # get_job=models.JobWorkflow.objects.filter(workflow_id__in=get_workflow).values_list('job_id')
        # job_status=models.JobCreation.objects.filter(id__in=get_job)
        # print('get_workflow',get_workflow)
        # print('get_job',get_job)
        active=False
        # for jobstatus in job_status:
        #     print(jobstatus.status.name)
        #     if jobstatus.status.name=='In Progress':
        #         active=True
        print(active)
        if not active:
            delete_template=models.Template_creation.objects.get(id=int(template_data['template_id']),
                                             category=models.TemplateCategory.objects.get(
                                                 id=int(template_data['cat_id'])),
                                             stage=CandidateModels.Stage_list.objects.get(id=int(template_data['stage_id'])),
                                             agency_id=models.Agency.objects.get(user_id=request.user.id)).delete()
            if delete_template:
                data['status'] = True
            else:
                data['status'] = False
            
        else:
            data['status'] = 'replica'
        
        return JsonResponse(data)


# pre_requisites

def pre_requisites(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        return render(request, 'agency/ATS/prerequisites-form.html',context)
    else:
        return redirect('agency:agency_Profile')
def pre_requisites_edit(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        return render(request,'agency/ATS/prerequisites-edit.html',context)
    else:
        return redirect('agency:agency_Profile')

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
            agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
        pre_requisite.data = json.dumps(data[0]['template-data'])
        pre_requisite.html_data = data[0]['html-data']
        pre_requisite.save()
        pre_requisite.template.status = True
        pre_requisite.template.save()
        
        data = {}
        data['status'] = True
        data['url'] = header+"://"+current_site.domain+'/agency/template_listing/'
        template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        description = template_name.name+" has been added to your workspace"
        all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
        for i in all_internal_users:
            if i.InternalUserid.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Pre-Requisites Template",
                                                                    description=description,image="/static/notifications/icon/company/Template.png",
                                                                    target_url=header+"://"+current_site.domain+"/agency/view_pre_requisites/"+str(pre_requisite.id))
        all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                        user_id=request.user)).values_list('InternalUserid', flat=True)
        get_email=[]
        
        for j in all_internaluser:
            get_email.append(User.objects.get(id=j).email)
        link=header+"://"+current_site.domain+"/agency/view_pre_requisites/"+str(pre_requisite.id)
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
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        pre_requisite = models.PreRequisites.objects.get(id=id,agency_id=models.Agency.objects.get(user_id= request.user))
        context["pre_requisite"] = pre_requisite
        return render(request,"agency/ATS/prerequisites-preview-template.html",context)
    else:
        return redirect('agency:agency_Profile')


# mcq template

def add_exam_template(request,template_id=None):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        subject=models.MCQ_subject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                                                            agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
                for i in all_internal_users:
                    description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Create MCQ Template"
                    if i.InternalUserid.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create MCQ Template",
                                                                            description=description,
                                                                            target_url=header+"://"+current_site.domain+"/company/mcq_template_view/"+str(exam_template.template.id))
                return redirect('agency:template_listing')
            return redirect('agency:exam_view',pk=exam_template.id)
        return render(request,"agency/ATS/add-mcq-exam.html",context)
    else:
        return redirect('agency:agency_Profile')

def exam_view(request,pk):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.ExamTemplate.objects.get(id=pk)
        print(exam_template.marking_system)
        context['exam_template'] = exam_template
        if not exam_template.exam_type == "custom":
            return redirect('agency:template_listing')
        if exam_template.exam_type == "custom":
            basic_questions = models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "basic",mcq_subject=models.MCQ_subject.objects.get(id=int(request.session['sub'])))
            intermediate_questions =  models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",mcq_subject=models.MCQ_subject.objects.get(id=int(request.session['sub'])))
            advanced_questions =  models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "advance",mcq_subject=models.MCQ_subject.objects.get(id=int(request.session['sub'])))


        #getting basic qustioons according to page no
        context["basic_questions"] = basic_questions
        #getting intermediate qustioons according to page no
        context["intermediate_questions"] = intermediate_questions
        #getting basic qustioons according to page no
        context["advanced_questions"] = advanced_questions
        # del request.session['sub']

    
        return render(request,"agency/ATS/mcq_exam_question_select.html",context)
    else:
        return redirect('agency:agency_Profile')

def exam_edit(request,pk):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.ExamTemplate.objects.get(template_id=pk)
        context['exam_template'] = exam_template

        exam_paper = models.QuestionPaper.objects.get(exam_template = exam_template,agency_id = models.Agency.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        mcq_subject = exam_paper.exam_template.subject
        if not exam_template.exam_type == "custom":
            return redirect('agency:template_listing')
        if exam_template.exam_type == "custom":
            basic_questions = models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "basic",mcq_subject=mcq_subject)
            intermediate_questions =  models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",mcq_subject=mcq_subject)
            advanced_questions =  models.mcq_Question.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "advance",mcq_subject=mcq_subject)

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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit MCQ Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Edit MCQ Template",
                            description=description,
                            target_url=header+"://"+current_site.domain+"/agency/mcq_template_view/"+str(exam_templatetemplate.id))
                # for i in in 
        return render(request,"agency/ATS/mcq_exam_question_edit.html",context)
    else:
        return redirect('agency:agency_Profile')
def create_exam(request,pk):
    exam_template = get_object_or_404(models.ExamTemplate,id=pk)
    question_paper = models.QuestionPaper.objects.create(exam_template=exam_template,
                                                        agency_id=models.Agency.objects.get(user_id=request.user.id),
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
    all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    description = template_name.name+" has been added to your workspace"
    for i in all_internal_users:
        if i.InternalUserid.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create MCQ Template",
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/company/mcq_template_view/"+str(exam_template.template.id))
    print("question idsssss",question_ids)
    all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                    user_id=request.user)).values_list('InternalUserid', flat=True)
    get_email=[]
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/agency/mcq_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'MCQ Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return HttpResponse("lolwa")


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


def mcq_template_view(request,template_id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        for j in  mcq_question:
            print(j)
        context['mcq_que']=mcq_question
        context['exam_data']=exam_name
        context["question_wise_flag"]=question_wise_flag
        return render(request,'agency/ATS/mcq_template_view.html',context)
    else:
        return redirect('agency:agency_Profile')
# =======================================image template

def image_add_exam_template(request,template_id=None):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        subject=models.ImageSubject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                                                            agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
                for i in all_internal_users:
                    description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Create Image Template"
                    if i.InternalUserid.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Image Template",
                                                                            description=description,
                                                                            target_url=header+"://"+current_site.domain+"/agency/images_template_view/"+str(exam_template.template.id))

                return redirect('agency:template_listing')
            return redirect('agency:image_exam_view',pk=exam_template.id)
        return render(request,"agency/ATS/image-add-exam.html",context)
    else:
        return redirect('agency:agency_Profile')

def image_exam_view(request,pk):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.ImageExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        if exam_template.exam_type == "custom":
            basic_questions = models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "basic",subject=models.ImageSubject.objects.get(id=int(request.session['sub'])))
            intermediate_questions =  models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",subject=models.ImageSubject.objects.get(id=int(request.session['sub'])))
            advanced_questions =  models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "advance",subject=models.ImageSubject.objects.get(id=int(request.session['sub'])))
            options = models.ImageOption.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            return redirect('agency:template_listing')
        # del request.session['sub']
        return render(request,"agency/ATS/image-exam-view.html",context)
    else:
        return redirect('agency:agency_Profile')

def image_exam_edit(request,pk):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.ImageExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        
        exam_paper = models.ImageQuestionPaper.objects.get(exam_template= exam_template,agency_id = models.Agency.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        img_subject = exam_paper.exam_template.subject

        if exam_template.exam_type != "custom":
            return redirect('agency:template_listing')

        basic_questions = models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "basic",subject=img_subject)
        intermediate_questions =  models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",subject=img_subject)
        advanced_questions =  models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "advance",subject=img_subject)
        options = models.ImageOption.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit Image Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Create Image Template",
                                                                    description=description,
                                                                    target_url=header+"://"+current_site.domain+"/agency/images_template_view/"+str(exam_template.template.id))


        # del request.session['sub']
        return render(request,"agency/ATS/image-exam-edit.html",context)
    else:
        return redirect('agency:agency_Profile')

def image_create_exam(request,pk):
    exam_template = get_object_or_404(models.ImageExamTemplate,id=pk)
    question_paper = models.ImageQuestionPaper.objects.create(exam_template=exam_template,
                                                            agency_id=models.Agency.objects.get(user_id=request.user.id),
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
    all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                        user_id=request.user)).values_list('InternalUserid', flat=True)
    get_email=[]
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/agency/images_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'Image Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
       
    all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
    description = template_name.name+" has been added to your workspace"
    for i in all_internal_users:
        if i.InternalUserid.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Image Template",
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/agency/images_template_view/"+str(exam_template.template.id))
    print("question idsssss",question_ids)
    return HttpResponse("lolwa")


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


def images_template_view(request,template_id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        return render(request,"agency/ATS/image-template-view.html",context)
    else:
        return redirect('agency:agency_Profile')

def image_exam_edit(request,pk):
    context={}
    exam_template = models.ImageExamTemplate.objects.get(template=pk)
    context['exam_template'] = exam_template
    
    exam_paper = models.ImageQuestionPaper.objects.get(exam_template= exam_template,agency_id = models.Agency.objects.get(user_id = request.user))
    context['exam_paper'] = exam_paper
    img_subject = exam_paper.exam_template.subject

    if exam_template.exam_type != "custom":
        return redirect('agency:template_listing')

    basic_questions = models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "basic",subject=img_subject)
    intermediate_questions =  models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "intermediate",subject=img_subject)
    advanced_questions =  models.ImageQuestion.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),question_level__level_name = "advance",subject=img_subject)
    options = models.ImageOption.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
        description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit Image Template"
        if exam_template.user_id.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Create Image Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/agency/images_template_view/"+str(exam_template.template.id))


    # del request.session['sub']
    return render(request,"agency/ATS/image-exam-edit.html",context)


# =======================================descriptive template

def descriptive_exam_template(request,template_id=None):
    # views added after templates
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        subject = models.Descriptive_subject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                agency_id=models.Agency.objects.get(user_id=request.user.id),
                defaults={
                'subject' : models.Descriptive_subject.objects.get(id=int(request.POST.get("language_name"))),
                'exam_name' : request.POST.get("exam_name"),
                'total_question' : request.POST.get("no_of_total_questions"),
                'user_id' : User.objects.get(id=request.user.id),
                })
            request.session['sub'] = int(request.POST.get("language_name"))
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
            for i in all_internal_users:
                description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Create Descriptive Template"
                if i.InternalUserid.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Descriptive Template",
                                                                        description=description,
                                                                        target_url=header+"://"+current_site.domain+"/company/descriptive_template_view/"+str(exam_template.template.id))
            return redirect('agency:descriptive_exam_view', pk=exam_template.id)
        return render(request, "agency/ATS/add-descriptive_exam.html", context)
    else:
        return redirect('agency:agency_Profile')

def descriptive_exam_view(request, pk):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.DescriptiveExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        descriptive_questions = models.Descriptive.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                subject=models.Descriptive_subject.objects.get(
                                                                    id=int(request.session['sub'])))

        # getting basic qustioons according to page no
        context["basic_questions"] = descriptive_questions
        
    # del request.session['sub']
        return render(request, "agency/ATS/descriptive_exam-view.html", context)
    else:
        return redirect('agency:agency_Profile')

def descriptive_exam_edit(request, pk):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        print("edit was called")
        exam_template = models.DescriptiveExamTemplate.objects.get(template=pk)
        context['exam_template'] = exam_template

        
        exam_paper = models.DescriptiveQuestionPaper.objects.get(exam_template= exam_template,agency_id = models.Agency.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        descriptive_subject = exam_paper.exam_template.subject

        descriptive_questions = models.Descriptive.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit descriptive Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Edit descriptive Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/agency/descriptive_template_view/"+str(exam_template.template.id))
        # del request.session['sub']
        context["basic_questions"] = descriptive_questions
        
    # del request.session['sub']
        return render(request, "agency/ATS/descriptive_exam-edit.html", context)
    else:
        return redirect('agency:agency_Profile')


def descriptive_create_exam(request, pk):
    exam_template = get_object_or_404(models.DescriptiveExamTemplate, id=pk)
    user = User.objects.get(id=request.user.id)
    question_paper = models.DescriptiveQuestionPaper.objects.create(exam_template=exam_template, 
                                                                    agency_id=models.Agency.objects.get(user_id=request.user.id),
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
    all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                        user_id=request.user)).values_list('InternalUserid', flat=True)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http" 
    get_email=[]
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/agency/descriptive_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'Descriptive Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    description = template_name.name+" has been added to your workspace"
    all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
    for i in all_internal_users:
        if i.InternalUserid.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create descriptive Template" + str(exam_template.template_id.id),
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/agency/descriptive_template_view/"+str(exam_template.template_id.id))

    return HttpResponse("/agency/template_listing")


def descriptive_get_count(request):
    data = {}
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        basic_count = models.Descriptive.objects.filter(subject=models.Descriptive_subject.objects.get(id=int(subject_data['subject_id'])),
                                                           agency_id=models.Agency.objects.get(user_id=request.user.id))
        print('++++++++++++++++++++++++++++++',len(basic_count))
        data['basic_count'] = len(basic_count)
        data['status'] = True
    else:
        data['basic_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))



def descriptive_template_view(request,template_id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        return render(request,'agency/ATS/descriptive_template_view.html',context)
    else:
        return redirect('agency:agency_Profile')


# ========================================Audio/Video template 


def audio_exam_template(request,template_id=None):
    # views added after templates
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        subject = models.Audio_subject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            return redirect('agency:audio_exam_view', pk=exam_template.id)
        return render(request, "agency/ATS/add-audio_exam.html", context)
    else:
        return redirect('agency:agency_Profile')

def audio_exam_view(request, pk):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.AudioExamTemplate.objects.get(id=pk)
        context['exam_template'] = exam_template
        if exam_template.exam_type == "custom":
            audio_questions = models.Audio.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                subject=models.Audio_subject.objects.get(
                                                                    id=int(request.session['sub'])))

        # getting basic qustioons according to page no
        print(audio_questions)
        context["basic_questions"] = audio_questions
        # del request.session['sub']
        return render(request, "agency/ATS/audio_exam-view.html", context)
    else:
        return redirect('agency:agency_Profile')

def audio_exam_edit(request, pk):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_template = models.AudioExamTemplate.objects.get(template=pk)
        context['exam_template'] = exam_template
        exam_paper = models.AudioQuestionPaper.objects.get(exam_template= exam_template,agency_id = models.Agency.objects.get(user_id = request.user))
        context['exam_paper'] = exam_paper
        audio_subject = exam_paper.exam_template.subject

        if exam_template.exam_type == "custom":
            audio_questions = models.Audio.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit Audio Template"
            if exam_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=exam_template.user_id.id),verb="Edit Audio Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/agency/audio_template_view/"+str(exam_template.template.id))

            return redirect('agency:template_listing')
        return render(request, "agency/ATS/audio_exam-edit.html", context)
    else:
        return redirect('agency:agency_Profile')

def audio_create_exam(request, pk):
    exam_template = get_object_or_404(models.AudioExamTemplate, id=pk)
    user = User.objects.get(id=request.user.id)
    question_paper = models.AudioQuestionPaper.objects.create(exam_template=exam_template, agency_id=models.Agency.objects.get(user_id=request.user.id),
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
    all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                        user_id=request.user)).values_list('InternalUserid', flat=True)
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"  
    get_email=[]
    template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
    for j in all_internaluser:
        get_email.append(User.objects.get(id=j).email)
    link=header+"://"+current_site.domain+"/agency/audio_template_view/"+str(exam_template.template.id)
    mail_subject = 'New Template Added'
    html_content = render_to_string('company/email/template_create.html',{'template_type':'Audio Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    description = template_name.name+" has been added to your workspace"
    all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
    for i in all_internal_users:
        if i.InternalUserid.id != request.user.id:
            notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Audio Template",
                                                                description=description,image="/static/notifications/icon/company/Template.png",
                                                                target_url=header+"://"+current_site.domain+"/agency/audio_template_view/"+str(exam_template.template.id))

    return HttpResponse('lolwa')
# end later views



def audio_template_view(request,template_id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        if models.AudioExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id)).exists():
            questions = models.AudioExamQuestionUnit.objects.filter(template=models.Template_creation.objects.get(id=template_id))
            exam_name=models.AudioExamTemplate.objects.get(template=models.Template_creation.objects.get(id=template_id))
            # questions = models.Descriptive.objects.filter(subject=subject_obj)
            print('questions',questions)
        else:
            questions = None
        context['questions']=questions
        context['exam_data']=exam_name
        return render(request,'agency/ATS/audio_template_view.html',context)
    else:
        return redirect('agency:agency_Profile')

def audio_get_count(request):
    data = {}
    if request.method == 'POST':
        subject_data = json.loads(request.body.decode('UTF-8'))
        print(subject_data)
        basic_count = models.Audio.objects.filter(subject=models.Audio_subject.objects.get(id=int(subject_data['subject_id'])),
                                                           agency_id=models.Agency.objects.get(user_id=request.user.id))
        print('++++++++++++++++++++++++++++++',len(basic_count))
        data['basic_count'] = len(basic_count)
        data['status'] = True
    else:
        data['basic_count'] = 0
        data['status'] = False
    return HttpResponse(json.dumps(data))


# ==============================================================coding template

def coding_exam_configuration(request,template_id=None):
    user_obj = User.objects.get(id=request.user.id)
    backend_subjects = models.CodingSubject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),type='backend')
    frontend_subjects = models.CodingSubject.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),type='frontend')
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            models.CodingExamConfiguration.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                agency_id=models.Agency.objects.get(user_id=request.user.id),
                template_id=template_obj)
            request.session['exam_configuration_id'] = exam_configuration.id
            return redirect('agency:coding_question_selection')
        return render(request, 'agency/ATS/coding_exam_configuration.html',context)
    else:
        return redirect('agency:agency_Profile')

def coding_question_selection(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                    models.CodingExamQuestions.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            coding_exam_config_id=exam_configuration_obj, question_id=question)
                if exam_configuration_obj.assignment_type == 'marks':
                    return redirect('agency:coding_question_marking')
                if exam_configuration_obj.assignment_type == 'rating':
                    return redirect('agency:coding_question_rating')
            context['exam_configuration']= exam_configuration_obj
            context['questions']= questions
            context['no_of_que']=range(0,no_of_que)
            return render(request, 'agency/ATS/coding_question_selection.html',context)
        else:
            return render(request, 'accounts/404.html')
    else:
        return redirect('agency:agency_Profile')

def coding_question_edit_selection(request,template_id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                
                new_exam_question = models.CodingExamQuestions.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            coding_exam_config_id=exam_configuration_obj, question_id=question)
            if exam_configuration_obj.assignment_type == 'marks':
                return redirect('agency:coding_question_marking_edit',exam_config_id=exam_configuration_obj.id)
            if exam_configuration_obj.assignment_type == 'rating':
                return redirect('agency:coding_question_rating_edit',exam_config_id=exam_configuration_obj.id)
            
        return render(request, 'agency/ATS/coding_question_edit_selection.html',context)
    else:
        return redirect('agency:agency_Profile')

def coding_question_marking(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                            user_id=request.user)).values_list('InternalUserid', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http" 
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            link=header+"://"+current_site.domain+"/agency/coding_template_view/"+str(exam_configuration_obj.template_id.id)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Coding Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace" 
            all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
            for i in all_internal_users:
                if i.InternalUserid.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Coding Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/agency/coding_template_view/"+str(exam_configuration_obj.template_id.id))

            return redirect('agency:template_listing')
        context['questions']= questions
        return render(request, 'agency/ATS/coding_question_marking.html',context)
    else:
        return redirect('agency:agency_Profile')

def coding_question_marking_edit(request,exam_config_id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit Coding Template"
            if exam_configuration_obj.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=context['get_template'].user_id.id),verb="Edit Coding Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/agency/coding_template_view/"+str(exam_configuration_obj.template_id.id))

            return redirect('agency:template_listing')
        context['questions']= questions
        return render(request, 'agency/ATS/coding_question_marking_edit.html', context)
    else:
        return redirect('agency:agency_Profile')


def coding_question_rating(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        exam_configuration_id = request.session['exam_configuration_id']
        exam_configuration_obj = models.CodingExamConfiguration.objects.get(id=exam_configuration_id)
        if request.method == 'POST':
            scorecard_title = request.POST.getlist('title')
            models.CodingScoreCard.objects.filter(coding_exam_config_id=exam_configuration_obj).delete()
            for title in scorecard_title:
                models.CodingScoreCard.objects.create(title=title, coding_exam_config_id=exam_configuration_obj)
            exam_configuration_obj.template_id.status = True
            exam_configuration_obj.template_id.save()
            all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                            user_id=request.user)).values_list('InternalUserid', flat=True)
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            link = header+"://"+current_site.domain+"/agency/coding_template_view/"+str(exam_configuration_obj.template_id.id)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Coding Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace"
            all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
            for i in all_internal_users:
                if i.InternalUserid.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Coding Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/agency/coding_template_view/"+str(exam_configuration_obj.template_id.id))

            return redirect('agency:template_listing')
        return render(request, 'agency/ATS/coding_question_rating.html',context)
    else:
        return redirect('agency:agency_Profile')

def coding_question_rating_edit(request,exam_config_id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            return redirect('agency:template_listing')
        return render(request, 'agency/ATS/coding_question_rating_edit.html',context)
    else:
        return redirect('agency:agency_Profile')
def get_subject_categories(request,subject_id):
    # subject = models.CodingSubject.objects.get(id=subject_id)
    all_categories = models.CodingSubjectCategory.objects.filter(subject_id__id = subject_id)
    category_data = []

    for i in all_categories:
        category_data.append([i.id,i.category_name])

    return HttpResponse(json.dumps(category_data))


def coding_template_view(request, template_id):
    template_getque= models.CodingExamConfiguration.objects.get(template_id=models.Template_creation.objects.get(id=template_id))
    questions=models.CodingExamQuestions.objects.filter(coding_exam_config_id=template_getque.id)
    return render(request, 'agency/ATS/coding_template_view.html', {'questions': questions,'exam_data':template_getque})



def coding_total_questions(request,id):
    categ = models.CodingSubjectCategory.objects.get(subject_id=id)
    count = models.CodingQuestion.objects.filter(category_id=categ).count()
    return HttpResponse(str(count))


# ==========================================interview template

def interview_template(request,template_id=None):
    context ={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        if template_id:
            print("ifwa")
            template = get_object_or_404(models.Template_creation,id=template_id)
            stage = template.stage
            category=template.category
            context['template_id'] = template_id
            exam_template = models.InterviewTemplate.objects.filter(template=template)
            if exam_template.exists():
                print("inside nested if")
                context['exam_template']= exam_template[0]
        else:
            stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
            category=models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
            template=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        if request.method == 'POST':
            interview_template_obj,update = models.InterviewTemplate.objects.update_or_create(
                agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),
                stage=stage,
                category=category,
                template=template,
                defaults={
                'user_id':User.objects.get(id=request.user.id),
                'interview_name':request.POST.get('interview_name'),
                'interview_type':request.POST.get('interview_type')})
            ratings = request.POST.getlist('rate-title')
            for title in ratings:
                models.InterviewScorecard.objects.create(title=title, interview_template=interview_template_obj)
            interview_template_obj.template.status = True
            interview_template_obj.template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"    
            all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                            user_id=request.user)).values_list('InternalUserid', flat=True)
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            link=header+"://"+current_site.domain+"/agency/interview_template_view/"+str(interview_template_obj.id)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Interview Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace"
            all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
            for i in all_internal_users:
                if i.InternalUserid.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Interview Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/agency/interview_template_view/"+str(interview_template_obj.id))

            return redirect('agency:template_listing')
        context['template']=template
        return render(request, "agency/ATS/interview_template.html",context)
    else:
        return redirect('agency:agency_Profile')

def interview_template_edit(request,interview_temp_id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        interview_template = models.InterviewTemplate.objects.get(template=interview_temp_id)  
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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit Interview Template"
            if interview_template.user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=interview_template.user_id.id),verb="Edit Interview Template",
                                                                description=description,
                                                                target_url=header+"://"+current_site.domain+"/agency/interview_template_view/"+str(interview_template.id))
            return redirect('agency:template_listing')
        return render(request, "agency/ATS/interview_template_edit.html",context)
    else:
        return redirect('agency:agency_Profile')

def interview_template_view(request,interview_temp_id):
    context={}
    interview_template = models.InterviewTemplate.objects.get(template=interview_temp_id)
    score_cards = models.InterviewScorecard.objects.filter(interview_template=interview_template)
    context['interview_template'] = interview_template
    context['score_cards'] = score_cards

    if request.method == 'POST':
        return redirect('agency:template_listing')
    return render(request, "agency/ATS/interview_template_view.html",context)


# ======================================================custom template

def custom_template(request):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        stage = CandidateModels.Stage_list.objects.get(id=int(request.session['create_template']['stageid']))
        category = models.TemplateCategory.objects.get(id=int(request.session['create_template']['categoryid']))
        template = models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
        if request.method == 'POST':
            enable_file_input = False
            file_input = None
            if request.POST.get('enable_file_input') == 'on':
                enable_file_input = True
            if request.FILES.get('file_input'):
                file_input = request.FILES.get('file_input')
            custom_template_obj,update = models.CustomTemplate.objects.update_or_create(
                agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),
                stage=stage,
                category=category,
                template=template,
                defaults={
                'title':request.POST.get('title'),'description': request.POST.get('description'),
                    'enable_file_input': enable_file_input,'file_input': file_input})
            ratings = request.POST.getlist('rate-title')
            for title in ratings:
                scorecard = models.CustomTemplateScorecard.objects.create(title=title)
                custom_template_obj.scorecards.add(scorecard)
            custom_template_obj.template.status = True
            custom_template_obj.template.save()
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http" 
            all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                            user_id=request.user)).values_list('InternalUserid', flat=True)
            get_email=[]
            template_name=models.Template_creation.objects.get(id=int(request.session['create_template']['templateid']))
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            # link=header+"://"+current_site.domain+"/company/view_pre_requisites/"+str(pre_requisite.id)
            link=''
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Custom Template','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'link':link})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            description = template_name.name+" has been added to your workspace"
            all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
            for i in all_internal_users:
                if i.InternalUserid.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Custom Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url="#")
            return redirect('agency:template_listing')
        return render(request, "agency/ATS/custom_template.html",context)
    else:
        return redirect('agency:agency_Profile')

def custom_stage(request,id):
    stage_obj = models.CandidateJobStagesStatus.objects.get(id=id)
    custom_round_obj = models.CustomTemplate.objects.filter(agency_id=stage_obj.agency_id, template=stage_obj.template)
    custom_result_data = None
    if custom_round_obj.exists():
        custom_round_data = custom_round_obj[0]
        custom_result = models.CustomResult.objects.filter(candidate_id=stage_obj.candidate_id, agency_id=stage_obj.agency_id,
                                                         custom_template__template=stage_obj.template,
                                                         job_id=stage_obj.job_id)
        if custom_result.exists():
            custom_result_data = custom_result[0]
        scorecards = custom_round_data.scorecards.all()
        print('id>>', custom_stage)
        if request.method == 'POST':
            description = request.POST.get('description')
            custom_result,created = models.CustomResult.objects.update_or_create(candidate_id=stage_obj.candidate_id,
                                                         agency_id=stage_obj.Agency,job_id=stage_obj.job_id,
                                                         custom_template=custom_round_data,
                                                         defaults={
                                                             'user_id':request.user,'description':description,
                                                         })
            for scorecard in scorecards:
                rating = request.POST.get('rating' + str(scorecard.id))
                comment = request.POST.get('comment' + str(scorecard.id))
                custom_result.scorecard_results.add(
                    models.CustomScorecardResult.objects.create(title=scorecard.title, comment=comment, rating=rating))

            stage_obj.assessment_done = True
            stage_obj.status = 2
            stage_obj.save()
            # return redirect('agency:agency_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,
            #                 job_id=stage_obj.job_id.id)
        return render(request, "agency/ATS/custom_stage.html", {'custom_round_data': custom_round_data,'custom_result_data':custom_result_data,
                                                                 'scorecards': scorecards})
    else:
        return HttpResponse(False)



# ========================================================================job creation template


def job_creation_template(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):

        context['job_types'] = CandidateModels.JobTypes.objects.all()
        context['template_category'] = models.TemplateCategory.objects.filter(stage=1,agency_id=models.Agency.objects.get(user_id=request.user.id))
        # context['job_status'] = CandidateModels.JobStatus.objects.all()
        context['job_shift'] = CandidateModels.JobShift.objects.all()
        context['countries'] = CandidateModels.Country.objects.all()
        context['industry_types'] = CandidateModels.IndustryType.objects.all()
        context['departments'] = models.Department.objects.filter(
            agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                                                        agency_id=models.Agency.objects.get(user_id=request.user.id), defaults={
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
            all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
            for i in all_internal_users:
                if i.InternalUserid.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Job Template",
                                                                        description=description,image="/static/notifications/icon/company/Template.png",
                                                                        target_url=header+"://"+current_site.domain+"/agency/job_template_view/"+str(template_id.template.id))
            
            all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                            user_id=request.user)).values_list('InternalUserid', flat=True)
            get_email=[]
            
            for j in all_internaluser:
                get_email.append(User.objects.get(id=j).email)
            mail_subject = 'New Template Added'
            html_content = render_to_string('company/email/template_create.html',{'template_type':'Job','username':request.user.first_name+' '+request.user.last_name,'templatename':template_name.name,'templateid':template_id.id,'link':'job_template_view'})
            from_email = settings.EMAIL_HOST_USER
            msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return redirect('agency:template_listing')
        return render(request, 'agency/ATS/job_creation_template.html', context)
    else:
        return redirect('agency:agency_Profile')


def job_creation_template_edit(request,id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['get_template']=models.JobCreationTemplate.objects.get(template=models.Template_creation.objects.get(
                                                        id=id))
        context['job_types'] = CandidateModels.JobTypes.objects.all()
        context['template_category'] = models.TemplateCategory.objects.filter(stage=1,agency_id=models.Agency.objects.get(user_id=request.user.id))
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
                                                        agency_id=models.Agency.objects.get(user_id=request.user.id), defaults={
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
            description = models.Agency.objects.get(user_id=request.user.id).agency_id.company_name + "Edit Job Template"
            if context['get_template'].user_id.id != request.user.id:
                notify.send(request.user, recipient=User.objects.get(id=context['get_template'].user_id.id),verb="Edit Job Template",
                                                                    description=description,
                                                                    target_url=header+"://"+current_site.domain+"/agency/job_template_view/"+str(context['get_template'].template.id))
            return redirect('agency:template_listing')
        return render(request, 'agency/ATS/job_creation_template.html', context)
    else:
        return redirect('agency:agency_Profile')


def get_job_template(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        print(category_data)
        template_data=[]
        get_job_template = models.Template_creation.objects.filter(category=models.TemplateCategory.objects.get(id=int(category_data['category'])),
            agency_id=models.Agency.objects.get(user_id=request.user.id))
        for template_get in get_job_template:
            template_data.append({'template_id':template_get.id,'template_name':template_get.name})
        print("============------", get_job_template)
        data = {}
        data['status'] = True
        data['get_job_template'] = template_data
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)



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



def job_template_view(request, template_id):
    context={}
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
        return render(request, 'agency/ATS/not_permoission.html', context)
    return render(request, 'agency/ATS/job-template-view.html', context)


# ===================================================workflow


def workflow_list(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
            flows = models.Workflows.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id)).order_by('-created_at')
            for flow in flows:
                stages = models.WorkflowStages.objects.filter(workflow=flow,display=True,agency_id=models.Agency.objects.get(user_id=request.user.id)).order_by('sequence_number')
                stage_list = [stage.stage_name for stage in stages]
                data.append({'workflow_id': flow.id, 'workflow_name': flow.name,'is_configured':flow.is_configured, 'stages': stage_list})
            context['stage']=data
            return render(request, 'agency/ATS/workflow_list.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def workflow_view(request,id):
    context = {}
    Workflows_obj = models.Workflows.objects.get(id=id)
    stages = models.WorkflowStages.objects.filter(workflow=Workflows_obj, display=True).order_by('sequence_number')
    workflow_data = []
    for stage in stages:
        stage_dict = {'stage': stage, 'data': '','workflow_configuration':''}
        if stage.stage.name == 'MCQ Test':
            mcq_template = models.ExamTemplate.objects.get(agency_id=stage.agency_id, template=stage.template,
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
                agency_id=stage.agency_id,
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
            image_template = models.ImageExamTemplate.objects.get(agency_id=stage.agency_id,
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
            audio_template = models.AudioExamTemplate.objects.get(agency_id=stage.agency_id,
                                                                  stage=stage.stage,
                                                                  template=stage.template)

            get_template_que = models.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
            total_marks = 0
            for mark in get_template_que:
                total_marks += int(mark.question_mark)
            stage_dict['audio_marks'] = total_marks
            stage_dict['data'] = audio_template

        if stage.stage.name == 'Coding Test':
            coding_template = models.CodingExamConfiguration.objects.get(agency_id=stage.agency_id,
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
            interview_template = models.InterviewTemplate.objects.get(agency_id=stage.agency_id,template_id=stage.template)
            interview_scorecards = models.InterviewScorecard.objects.filter(interview_template=interview_template)
            stage_dict['data'] = interview_template
            stage_dict['interview_scorecards'] = interview_scorecards

        workflow_data.append(stage_dict)

    context['workflow_data'] = workflow_data
    return render(request, 'agency/ATS/workflow_view.html',context)


def create_workflow(request):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id))
                first = True
                count = 1
                workflow_data = workflow_data['data']
                for data in workflow_data:
                    print('\n\n\nlen', len(workflow_data))
                    if len(workflow_data) == 1:
                        stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                        models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name='Job Applied', workflow=workflow_obj,
                                                            stage=stage_obj, sequence_number=count, display=False)
                        count += 1

                        stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                        category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                        template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                        models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name=data['stage_name'], workflow=workflow_obj,
                                                            stage=stage_obj,
                                                            category=category_obj, template=template_obj,
                                                            sequence_number=count)
                        count += 1

                        stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                        models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            user_id=User.objects.get(id=request.user.id),
                                                            stage_name='Job Offer', workflow=workflow_obj,
                                                            stage=stage_obj, sequence_number=count, display=False)
                        count += 1
                    else:
                        if first:
                            print('first called', data)
                            stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                            models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name='Job Applied', workflow=workflow_obj,
                                                                stage=stage_obj, sequence_number=count,display=False)
                            first = False
                            count += 1

                            stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                            category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                            template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                            models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                            models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name=data['stage_name'], workflow=workflow_obj,
                                                                stage=stage_obj,
                                                                category=category_obj, template=template_obj,
                                                                sequence_number=count)
                            count += 1

                            stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                            models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                user_id=User.objects.get(id=request.user.id),
                                                                stage_name='Job Offer', workflow=workflow_obj,
                                                                stage=stage_obj, sequence_number=count,display=False)
                            count += 1
                        else:
                            stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                            category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                            template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                            models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            return render(request, 'agency/ATS/create_workflow.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')
def edit_workflow(request, id):
    print('w -id', id)
    workflow_obj = models.Workflows.objects.get(id=id)
    # get_activejob=models.JobWorkflow.objects.filter(workflow_id=workflow_obj,job_id__close_job_targetdate=False,job_id__close_job=False)
    # if get_activejob:
    #     return HttpResponse(False)
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
                models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                     user_id=User.objects.get(id=request.user.id),
                                                     stage_name='Job Applied', workflow=workflow_obj,
                                                     stage=stage_obj, sequence_number=count, display=False)
                count += 1

                stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                     user_id=User.objects.get(id=request.user.id),
                                                     stage_name=data['stage_name'], workflow=workflow_obj,
                                                     stage=stage_obj,
                                                     category=category_obj, template=template_obj,
                                                     sequence_number=count)
                count += 1

                stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                     user_id=User.objects.get(id=request.user.id),
                                                     stage_name='Job Offer', workflow=workflow_obj,
                                                     stage=stage_obj, sequence_number=count, display=False)
                count += 1
            else:
                if first:
                    print('first called', data)
                    stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                    models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                         user_id=User.objects.get(id=request.user.id),
                                                         stage_name='Job Applied', workflow=workflow_obj,
                                                         stage=stage_obj, sequence_number=count, display=False)
                    first = False
                    count += 1

                    stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                    category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                    template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                    models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                    models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                         user_id=User.objects.get(id=request.user.id),
                                                         stage_name=data['stage_name'], workflow=workflow_obj,
                                                         stage=stage_obj,
                                                         category=category_obj, template=template_obj,
                                                         sequence_number=count)
                    count += 1

                    stage_obj = CandidateModels.Stage_list.objects.get(name='Job Offer')
                    models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                         user_id=User.objects.get(id=request.user.id),
                                                         stage_name='Job Offer', workflow=workflow_obj,
                                                         stage=stage_obj, sequence_number=count, display=False)
                    count += 1
                else:
                    stage_obj = CandidateModels.Stage_list.objects.get(id=data['stage_id'])
                    category_obj = models.TemplateCategory.objects.get(id=data['cate_id'])
                    template_obj = models.Template_creation.objects.get(id=data['temp_id'])
                    models.WorkflowStages.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
    return render(request, 'agency/ATS/create_workflow.html', {'stages': stages,
                                                                'workflow_obj': workflow_obj, 'is_edit': True})


def get_workflow_data(request):
    stages_data = []
    category_data = []
    template_data = []
    stages = CandidateModels.Stage_list.objects.filter(active=True).exclude(name__in=["Job Creation"])
    for i in stages:
        # stage
        if models.TemplateCategory.objects.filter(stage=i.id,agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
            stage_dict = {'key': i.id, 'stage_name': i.name}
            stages_data.append(stage_dict)
            print('satge name', i.name)

            # category
            categories = models.TemplateCategory.objects.filter(stage=i.id,agency_id=models.Agency.objects.get(user_id=request.user.id))
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
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        if workflow_id == None:
            workflow_id = request.session.get('workflow_configure')
        if workflow_id:
            workflow_obj = models.Workflows.objects.get(id=workflow_id)
            workflow_stages = models.WorkflowStages.objects.filter(workflow=workflow_obj,display=True)
            internaluser=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)))
            workflow_data = []
            for stage in workflow_stages:
                stage_dict = {'stage': stage, 'data': ''}
                if stage.stage.name == 'MCQ Test':
                    print('aaaaaaaaaaa',stage.agency_id,'-------',stage.template,'--------',stage.stage)
                    mcq_template = models.ExamTemplate.objects.get(agency_id=stage.agency_id,template=stage.template,
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
                        agency_id=stage.agency_id,
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
                    image_template = models.ImageExamTemplate.objects.get(agency_id=stage.agency_id,
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
                    print("agency_id",stage.agency_id)
                    print("stage",stage.stage)
                    print("templte ",stage.template)
                    audio_template = models.AudioExamTemplate.objects.get(agency_id=stage.agency_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)
                    
                    get_template_que = models.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                    total_marks=0
                    for mark in get_template_que:
                        total_marks+=int(mark.question_mark)
                    stage_dict['audio_marks']=total_marks
                    stage_dict['data'] = audio_template

                if stage.stage.name == 'Coding Test':
                    print('\n\n\nstage.agency_id',  stage.agency_id)
                    print('template',  stage.template)
                    coding_template = models.CodingExamConfiguration.objects.get(agency_id=stage.agency_id,
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
                                                                    agency_id=stage.agency_id,
                                                                    is_automation=is_automation,
                                                                    shortlist=shortlist,
                                                                    onhold=onhold,
                                                                    reject=reject)

                    if stage.stage.name == 'Prerequisites':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,agency_id=stage.agency_id,)

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
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage, agency_id=stage.agency_id,
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

                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,agency_id=stage.agency_id,
                                                                    is_automation=is_automation,
                                                                    shortlist=shortlist,
                                                                    # onhold=onhold,
                                                                    reject=reject)

                    if stage.stage.name == 'Paragraph MCQ Test':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,agency_id=stage.agency_id)

                    if stage.stage.name == 'Descriptive Test':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,agency_id=stage.agency_id)

                    if stage.stage.name == 'Coding Test':
                        models.WorkflowConfiguration.objects.create(workflow_stage=stage,agency_id=stage.agency_id)

                    if stage.stage.name == 'Interview':
                        interviewer = request.POST.getlist('interviewers')
                        interviewer_create=models.WorkflowConfiguration.objects.create(workflow_stage=stage,agency_id=stage.agency_id)
                        for user_id in interviewer:
                            interviewer_create.interviewer.add(User.objects.get(id=int(user_id)))
                workflow_obj.is_configured = True
                workflow_obj.save()
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"  
                all_internaluser = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(
                        user_id=request.user)).values_list('InternalUserid', flat=True)
                get_email=[]
                for j in all_internaluser:
                    get_email.append(User.objects.get(id=j).email)
                mail_subject = 'New Workflow Added'
                link=header+"://"+current_site.domain+"/agency/workflow_view/"+str(workflow_obj.id)
                html_content = render_to_string('company/email/workflow_create.html',{'username':request.user.first_name+' '+request.user.last_name,'workflowname':workflow_obj.name,'workflowid':workflow_id,'link':link  })
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=get_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send() 
                description = workflow_obj.name+" has been added to your workspace"
                all_internal_users=models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),InternalUserid__is_active=True)
                for i in all_internal_users:
                    if i.InternalUserid.id != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i.InternalUserid.id),verb="Create Workflow",
                                                                            description=description,image="/static/notifications/icon/company/Workflow.png",
                                                                            target_url=header+"://"+current_site.domain+"/agency/workflow_view/"+str(workflow_obj.id))
                if 'workflow_configure' in request.session:
                    del request.session['workflow_configure']
                return redirect('agency:workflow_list')
            context['internaluser']=internaluser
            context['workflow_name']= workflow_obj.name
            context['workflow_stages']= workflow_stages
            context['workflow_data']=workflow_data
            return render(request, 'agency/ATS/workflow_configuration.html',context)
        else:
            return render(request, 'accounts/404.html')
    else:
        return redirect('agency:agency_Profile')


# =======================================job creation

# ########################    JOB    ########################

def job_template_creation(request,jobtemplate_id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['if_template']=True
        # if 'get_template_job' in request.session:
        #     context['if_template']=True
        context['get_job_template'] = models.JobCreationTemplate.objects.get(id=jobtemplate_id)
        context['job_owner'] = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        context['job_types'] = CandidateModels.JobTypes.objects.all()
        context['template_category'] = models.TemplateCategory.objects.filter(stage=1,agency_id=models.Agency.objects.get(user_id=request.user.id))
        context['job_shift'] = CandidateModels.JobShift.objects.all()
        context['countries'] = CandidateModels.Country.objects.all()
        context['industry_types'] = CandidateModels.IndustryType.objects.all()
        context['departments'] = models.Department.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        
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

            job_id = models.JobCreation.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
            # for assign_id in assign_external_id:
            #     CompanyModels.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_external=True,recruiter_id=User.objects.get(id=int(assign_id)))
            # for assign_id in assign_internal_id:
            #     models.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id)))

            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http"  
            job_user=list(set([request.POST.get('job_owner'), request.POST.get('contact_person')]))
            for i in job_user:
                description = "New job "+job_id.job_title+" has been created by "+request.user.first_name+" "+request.user.last_name
                if i != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=i), verb="Job Create/publish",
                                description=description,image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                    job_id.id))
            return redirect('agency:workflow_selection', id=job_id.id)
        return render(request, 'agency/ATS/job_creation.html', context)
    else:
        return redirect('agency:agency_Profile')

def job_creation(request,jobid=None):
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
                # context['external_assign'] = models.CompanyAssignJob.objects.filter(job_id=models.JobCreation.objects.get(id=jobid),
                #                                                                     recruiter_type_external=True).values_list(
                #     'recruiter_id', flat=True)

                # context['internal_assign'] = models.CompanyAssignJob.objects.filter(job_id=models.JobCreation.objects.get(id=jobid),
                #                                                                     recruiter_type_internal=True).values_list(
                #     'recruiter_id', flat=True)
                # context['job_assign']=models.CompanyAssignJob.objects.filter(company_id=models.Company.objects.get(user_id=request.user.id),job_id=models.JobCreation.objects.get(id=jobid))
            context['job_owner'] = models.InternalUserProfile.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
            context['job_types'] = CandidateModels.JobTypes.objects.all()
            context['template_category'] = models.TemplateCategory.objects.filter(stage=CandidateModels.Stage_list.objects.get(name='Job Creation'),agency_id=models.Agency.objects.get(user_id=request.user.id))
            # context['job_status'] = CandidateModels.JobStatus.objects.all()
            context['job_shift'] = CandidateModels.JobShift.objects.all()
            context['countries'] = CandidateModels.Country.objects.all()
            context['industry_types'] = CandidateModels.IndustryType.objects.all()
            context['departments'] = models.Department.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        
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
                    job_create,update = models.JobCreation.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),id=jobid,defaults={
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
                    
                    for assign_id in request.POST.getlist('internal'):
                        print(assign_id)
                        models.AgencyAssignJob.objects.filter(job_id=job_create,agency_id=models.Agency.objects.get(user_id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id))).delete()
                        models.AgencyAssignJob.objects.create(job_id=job_create,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id)))
                    if job_create.is_publish:
                        result = models.AssociateJob.objects.filter(job_id=job_create).count()
                        count = models.AppliedCandidate.objects.filter(job_id=job_create).count()
                        # Notification
                        description = job_create.agency_id.agency_id.company_name + " Job Edit By Agency"
                        if job_create.contact_name.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=job_create.contact_name.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                                                                            job_create.id))
                        if job_create.job_owner.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=job_create.job_owner.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                                                                            job_create.id))
                        all_assign_users=models.CompanyAssignJob.objects.filter(job_id=job_create)
                        
                        for i in all_assign_users:
                            print(i.recruiter_type_external)
                            if i.recruiter_type_internal:
                                description = job_create.agency_id.agency_id.company_name + " Job Edit By Agency"
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Job Edit",
                                                                                        description=description,
                                                                                        target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                                                                            job_create.id))
                        if (count+result)==0:
                            return redirect('agency:workflow_selection', id=job_create)
                        else:
                            return redirect('agency:created_job_view', id=job_create)
                    else:
                        return redirect('agency:workflow_selection', id=job_create)
                else:
                    job_id = models.JobCreation.objects.create(agency_id=models.Agency.objects.get(user_id=request.user.id),
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
                    # for assign_id in assign_external_id:
                    #         models.CompanyAssignJob.objects.create(job_id=job_id,company_id=models.Company.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_external=True,recruiter_id=User.objects.get(id=int(assign_id)))
                    for assign_id in assign_internal_id:
                        models.AgencyAssignJob.objects.create(job_id=job_id,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id),recruiter_type_internal=True,recruiter_id=User.objects.get(id=int(assign_id)))
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                job_user=list(set([request.POST.get('job_owner'), request.POST.get('contact_person')]))
                for i in job_user:
                    description = "New job "+job_id.job_title+" has been created by "+request.user.first_name+" "+request.user.last_name
                    if i != request.user.id:
                        notify.send(request.user, recipient=User.objects.get(id=i), verb="Job Create/publish",
                                    description=description,image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                        job_id.id))
                return redirect('agency:workflow_selection', id=job_id.id)
            return render(request, 'agency/ATS/job_creation.html', context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')

def job_creation_select_template(request):
    if request.method=='POST':
        job_template = json.loads(request.body.decode('UTF-8'))
        print(job_template)
        get_templatejob_id=models.JobCreationTemplate.objects.get(agency_id=models.Agency.objects.get(user_id=request.user.id),category=models.TemplateCategory.objects.get(
                                                    id=int(job_template['category'])),
                                                    template=models.Template_creation.objects.get(
                                                    id=int(job_template['template'])))
        request.session['get_template_job']=get_templatejob_id.id
        data = {"status": "true"}
        data['url']='/agency/job_template_creation/'+str(get_templatejob_id)
        return JsonResponse(data)
        # return HttpResponseRedirect("company:job_template_creation",jobtemplate_id=get_templatejob_id)
        


def get_job_template(request):
    if request.method == 'POST':
        category_data = json.loads(request.body.decode('UTF-8'))
        print(category_data)
        template_data=[]
        get_job_template = models.Template_creation.objects.filter(category=models.TemplateCategory.objects.get(id=int(category_data['category'])),
            agency_id=models.Agency.objects.get(user_id=request.user.id))
        for template_get in get_job_template:
            template_data.append({'template_id':template_get.id,'template_name':template_get.name})
        print("============------", get_job_template)
        data = {}
        data['status'] = True
        data['get_job_template'] = template_data
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(False)

def workflow_selection(request, id):
    context={}
    workflows = models.Workflows.objects.filter(is_configured=True,agency_id=models.Agency.objects.get(user_id=request.user.id))
    context['workflows']= workflows
    job_obj = models.JobCreation.objects.get(id=id)
    if models.JobWorkflow.objects.filter(job_id=job_obj,agency_id=models.Agency.objects.get(user_id=request.user.id)).exists():
        context['selectedworkflows']=models.JobWorkflow.objects.get(job_id=job_obj,agency_id=models.Agency.objects.get(user_id=request.user.id))
    if request.method == 'POST':
        if request.POST.get('workflowtype')=='onthego':
            job_workflow_obj,created = models.JobWorkflow.objects.update_or_create(job_id=job_obj,agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                    defaults={'onthego':True, 'workflow_id':None,'user_id':User.objects.get(id=request.user.id)})
            if request.POST.get('application_review') == 'application_review':
                job_workflow_obj.is_application_review = True
                job_workflow_obj.save()
        if request.POST.get('workflowtype')=='withworkflow':
            workflow = models.Workflows.objects.get(id=request.POST.get('selected_workflow'))
            job_workflow_obj,created = models.JobWorkflow.objects.update_or_create(job_id=job_obj,agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                        defaults={'workflow_id':workflow,'withworkflow':True,'user_id':User.objects.get(id=request.user.id)})
            if request.POST.get('application_review') == 'application_review':
                job_workflow_obj.is_application_review = True
                job_workflow_obj.save()
        return redirect('agency:created_job_view', id=job_obj.id)
    return render(request, 'agency/ATS/workflow_selection.html', context)




def created_job_view(request, id):
    current_site = get_current_site(request)
    print(current_site.domain)
    print(request.get_host())
    print(request.headers)
    header=request.is_secure() and "https" or "http"
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        

        context['job_owner'] = models.InternalUserProfile.objects.filter(
            agency_id=models.Agency.objects.get(user_id=request.user.id))
        job_obj = models.JobCreation.objects.get(id=id)
        
        context['internal_assign'] = models.AgencyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True).values_list('recruiter_id',flat=True)
        # get_recruiter_internal=models.AgencyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True)
        # context['internal']=get_recruiter_internal
        context['job_obj']= job_obj
        context['active_job_count']=len(models.JobCreation.objects.filter(agency_id=job_obj.agency_id.id,close_job=False,close_job_targetdate=False,is_publish=True))
        context['close_job_count'] = len(models.JobCreation.objects.filter(agency_id=job_obj.agency_id.id, close_job=True))
        context['last_close_job'] = models.JobCreation.objects.filter(agency_id=job_obj.agency_id.id, close_job=True).order_by('-close_job_at').first()
        context['latest_10_job'] = models.JobCreation.objects.filter(agency_id=job_obj.agency_id.id,close_job=False,close_job_targetdate=False,is_publish=True).order_by('-publish_at')

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
                        mcq_template = models.ExamTemplate.objects.get(agency_id=stage.agency_id, template=stage.template,
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
                            agency_id=stage.agency_id,
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
                        image_template = models.ImageExamTemplate.objects.get(agency_id=stage.agency_id,
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

                        audio_template = models.AudioExamTemplate.objects.get(agency_id=stage.agency_id,
                                                                                stage=stage.stage,
                                                                                template=stage.template)

                        get_template_que = models.AudioExamQuestionUnit.objects.filter(template=audio_template.template)
                        total_marks = 0
                        for mark in get_template_que:
                            total_marks += int(mark.question_mark)
                        stage_dict['audio_marks'] = total_marks
                        stage_dict['data'] = audio_template

                    if stage.stage.name == 'Coding Test':

                        coding_template = models.CodingExamConfiguration.objects.get(agency_id=stage.agency_id,
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
                return redirect('agency:job_edit',job_obj.id)
            else:
                job_obj.is_publish = True
                job_obj.publish_at = datetime.datetime.now()
                job_obj.updated_at = datetime.datetime.now()
                job_obj.save()
                if not models.JobWorkflow.objects.filter(job_id=job_obj).exists():
                    job_workflow_obj,created = models.JobWorkflow.objects.update_or_create(job_id=job_obj,agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            defaults={'onthego':True, 'workflow_id':None,'user_id':User.objects.get(id=request.user.id)})
                    job_workflow_obj.save()
                # onthego change
                if job_workflow.onthego:
                    stage_obj = CandidateModels.Stage_list.objects.get(name='Job Applied')
                    models.OnTheGoStages.objects.update_or_create(job_id=job_obj,agency_id=job_obj.agency_id,stage=stage_obj,
                                                                    defaults={'user_id':User.objects.get(id=request.user.id),
                                                                            'stage_name':"Job Applied",'sequence_number':1})
                job_assign_recruiter = models.AgencyAssignJob.objects.filter(job_id=job_obj)
                for j in job_assign_recruiter:
                    if j.recruiter_type_internal:
                        print("==================",j)
                        get_recruiter=models.AgencyAssignJob.objects.get(id=j.id)
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
                            models.AssignInternal.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=job_obj,recruiter_id=User.objects.get(id=send_email.id),defaults={'user_id':User.objects.get(id=request.user.id),'send_email':True})
                        except:
                            print('not send')
                            models.AssignInternal.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),job_id=job_obj,recruiter_id=User.objects.get(id=send_email.id),defaults={'user_id':User.objects.get(id=request.user.id),'send_email':False})
                            continue
                # Notification
                description = "You have been assigned to  "+job_obj.job_title+" Job"
                job_assign_recruiter = models.AgencyAssignJob.objects.filter(job_id=job_obj)
                if job_obj.contact_name.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                                                                    job_obj.id))
                if job_obj.job_owner.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                                                                    job_obj.id))
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        description = "You have been assigned to  "+job_obj.job_title+" Job"
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/agency/created_job_view/" + str(
                                                                                    job_obj.id))
                    if i.recruiter_type_external :
                        description = "You have been assigned to  "+job_obj.job_title+" Job"
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Assign job",
                                                                                description=description,image="/static/notifications/icon/company/Assign.png",
                                                                                target_url=header+"://"+current_site.domain+"/agency/job_view/" + str(
                                                                                    job_obj.id))
                return redirect('agency:job_openings_table')
        return render(request, 'agency/ATS/job_view.html', context)
    else:
        return redirect('agency:agency_Profile')    

def assign_job(request):
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    if request.method=='POST':
        job_obj=models.JobCreation.objects.get(id=request.POST.get('job_obj'),agency_id=models.Agency.objects.get(user_id=request.user.id))
        for assign_id in request.POST.getlist('internal-selector-1'):
            models.AgencyAssignJob.objects.filter(job_id=job_obj,
                                                   agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                   recruiter_type_internal=True,
                                                   recruiter_id=User.objects.get(id=int(assign_id))).delete()
            models.AgencyAssignJob.objects.create(job_id=job_obj,
                                                   agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                   user_id=User.objects.get(id=request.user.id),
                                                   recruiter_type_internal=True,
                                                   recruiter_id=User.objects.get(id=int(assign_id)))
        if job_obj.is_publish:
            
            for j in request.POST.getlist('internal-selector-1'):
                get_external = models.AgencyAssignJob.objects.get(job_id=job_obj,
                                                                   agency_id=models.Agency.objects.get(
                                                                       user_id=request.user.id),
                                                                   user_id=User.objects.get(id=request.user.id),
                                                                   recruiter_type_internal=True,
                                                                   recruiter_id=User.objects.get(id=int(j)))
                if get_external.recruiter_type_internal:
                    get_recruiter = models.AgencyAssignJob.objects.get(id=get_external.id)
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
                            agency_id=models.Agency.objects.get(user_id=request.user.id), job_id=job_obj,
                            recruiter_id=User.objects.get(id=send_email.id),
                            defaults={'user_id': User.objects.get(id=request.user.id), 'send_email': True})
                    except:
                        print('not send')
                        models.AssignInternal.objects.update_or_create(
                            agency_id=models.Agency.objects.get(user_id=request.user.id), job_id=job_obj,
                            recruiter_id=User.objects.get(id=send_email.id),
                            defaults={'user_id': User.objects.get(id=request.user.id), 'send_email': False})
                        continue
        return redirect('agency:created_job_view', id=job_obj.id)



def unassign_recruiter(request):
    if request.method=='POST':
        getUserId = request.POST.get("getUserId")
        job_id = request.POST.get("job_id")
        getUsertype = request.POST.get("getUsertype")
        job_obj=models.JobCreation.objects.get(id=job_id)
        models.AgencyAssignJob.objects.filter(job_id=job_obj,
                                               agency_id=models.Agency.objects.get(user_id=request.user.id),
                                               recruiter_id=User.objects.get(id=getUserId)).delete()
        if getUsertype=='internal':
            models.AssignInternal.objects.filter(
                agency_id=models.Agency.objects.get(user_id=request.user.id), job_id=job_obj,
                recruiter_id=User.objects.get(id=getUserId)).delete()
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def internal_submit_candidate(request, id):
    context={}
    context['job_id']=models.JobCreation.objects.get(id=id)
    candidates = models.InternalCandidateBasicDetail.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
    context['candidates'] = candidates
    internal_candidate=''
    if request.method == 'POST':
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        job_obj = models.JobCreation.objects.get(id=int(id))
        context['jobid']=job_obj
        context['jobtype']='agency'
        internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=request.POST.get('selected_candidate'))
        context['edit_internal_candidate']=internal_candidate
        return render(request,'agency/ATS/applied_candidate_detail_form.html',context)
        # print('post>>>', request.POST.get('selected_candidate'))
        # job_obj = models.JobCreation.objects.get(id=int(id))
        # internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=request.POST.get('selected_candidate'))
        # fname = internal_candidate.first_name
        # lname = internal_candidate.last_name
        # email = internal_candidate.email
        # gender = internal_candidate.gender
        # resume = internal_candidate.resume
        # contact = internal_candidate.contact
        # secure_resume=internal_candidate.secure_resume
        # secure_resume_file=internal_candidate.secure_resume_file
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
        #                                        password=password, ip=ip, device_type=device_type,
        #                                        browser_type=browser_type,
        #                                        browser_version=browser_version, os_type=os_type,
        #                                        os_version=os_version,
        #                                        referral_number=generate_referral_code())

        #     mail_subject = 'Activate your account'
        #     current_site = get_current_site(request)
        #     header=request.is_secure() and "https" or "http"
        #     # print('domain----===========',current_site.domain)
        #     html_content = render_to_string('company/email/send_credentials.html', {'user': usr,
        #                                                                        'name': fname + ' ' + lname,
        #                                                                        'email': email,
        #                                                                        'domain': current_site.domain,
        #                                                                        'password': password, 
        #                                                                        'link':header+"://"+current_site.domain+"/candidate/applicant_create_account/"+str(usr.id)
        #                                                                        })
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
        #     toemail=[internal_candidate.email]
        #     mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
        #     html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
        #     from_email = settings.EMAIL_HOST_USER
        #     msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
        #     msg.attach_alternative(html_content, "text/html")
        #     # try:
        #     msg.send()
        #     internal_candidate.candidate_id = User.objects.get(email=internal_candidate.email)
        #     internal_candidate.save()
        # models.AssociateCandidateInternal.objects.update_or_create(agency_id=job_obj.agency_id,job_id=job_obj,candidate_id=internal_candidate.candidate_id,
        #         defaults={
        #             'internal_candidate_id':models.InternalCandidateBasicDetail.objects.get(id=internal_candidate.id)
        #         })
        # models.AppliedCandidate.objects.update_or_create(agency_id=job_obj.agency_id,job_id=job_obj,candidate=User.objects.get(email=email.lower()),
        #         defaults={
        #             'submit_type':'Agency'
        #         })
        # # models.AssociateJob.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),
        # #                                                             job_id=job_obj,
        # #                                                             internal_candidate_id=models.InternalCandidateBasicDetail.objects.get(id=internal_candidate.id),
        # #                                                             internal_user=models.InternalUserProfile.objects.get(InternalUserid=request.user.id),
        # #                                                             defaults={'user_id' : User.objects.get(id=request.user.id)
        # #                                                             })
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
        #                 models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj, stage=stage_list_obj,
        #                                                         sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
        #                 sequence_number = stage.sequence_number + 1
        #                 status = 0
        #             else:
        #                 status = 0
        #                 sequence_number = stage.sequence_number + 1
        #                 next_stage = stage.stage
        #             models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
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
        #             models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
        #                                                     candidate_id=internal_candidate.candidate_id,
        #                                                     job_id=job_obj, stage=stage.stage,
        #                                                     template=stage.template,
        #                                                     sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
        # internal_candidate = models.InternalCandidateBasicDetail.objects.get(id=request.POST.get('selected_candidate'))
        # if workflow.onthego:
        #     print("==========================onthego================================")
        #     onthego_stages = models.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

        #     if workflow.is_application_review:
        #         for stage in onthego_stages:
        #             if stage.sequence_number == 1:
        #                 status = 2
        #                 sequence_number = stage.sequence_number
        #                 models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj, stage=stage.stage,
        #                                                         template=stage.template,
        #                                                         sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

        #                 status = 1
        #                 sequence_number = stage.sequence_number + 1
        #                 stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
        #                 current_stage = stage_list_obj
        #                 next_stage_sequance=stage.sequence_number+1
        #                 models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
        #                                                         candidate_id=internal_candidate.candidate_id,
        #                                                         job_id=job_obj, stage=stage_list_obj,
        #                                                         sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
        #             else:
        #                 status = 0
        #                 sequence_number = stage.sequence_number + 1
        #                 current_stage = stage_list_obj
        #                 models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
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
        #             models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
        #                                                     candidate_id=internal_candidate.candidate_id,
        #                                                     job_id=job_obj, stage=stage.stage,
        #                                                     template=stage.template,
        #                                                     sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
        # action_required=''
        
        # if next_stage_sequance!=0:
        #     if models.CandidateJobStagesStatus.objects.filter(agency_id=job_obj.agency_id,
        #                                                     candidate_id=internal_candidate.candidate_id,
        #                                                     job_id=job_obj,
        #                                                     sequence_number=next_stage_sequance).exists():
        #         next_stage=models.CandidateJobStagesStatus.objects.get(agency_id=job_obj.agency_id,
        #                                                     candidate_id=internal_candidate.candidate_id,
        #                                                     job_id=job_obj,
        #                                                     sequence_number=next_stage_sequance).stage
        # if not current_stage==None:
        #     if current_stage.name=='Interview' :
        #         action_required='By Company/Agency'
        #     elif current_stage.name=='Application Review' :
                
        #         action_required='By Company'
        #     else:
        #         action_required='By Candidate'
        # if current_stage!='':
        #     models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=internal_candidate.candidate_id,agency_id=job_obj.agency_id,defaults={
        #                                             'current_stage':current_stage,'next_stage':next_stage,
        #                                             'action_required':action_required,'update_at':datetime.datetime.now()})
        # assign_job_internal = list(
        #     models.AgencyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
        #                                     agency_id=job_obj.agency_id).values_list(
        #         'recruiter_id', flat=True))
        # assign_job_internal.append(job_obj.job_owner.id)
        # assign_job_internal.append(job_obj.contact_name.id)
        # assign_job_internal = list(set(assign_job_internal))
        # title = job_obj.job_title
        # # chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(id=request.user.id).id, title=title,candidate_id=User.objects.get(id=internal_candidate.candidate_id.id))
        # # print(assign_job_internal)
        # # ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=internal_candidate.candidate_id.id).id)
        # # for i in assign_job_internal:
        # #     ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
        # # ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
        # candidate=User.objects.get(email=internal_candidate.email)
        # job_assign_recruiter = models.AgencyAssignJob.objects.filter(job_id=job_obj)
        # agency_name=models.Agency.objects.get(user_id=request.user.id).agency_id.company_name
        # current_site = get_current_site(request)
        # header=request.is_secure() and "https" or "http"
        # if not agency_name:
        #     agency_name=request.user.first_name+' '+request.user.last_name
        # description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
        # to_email=[]
        # to_email.append(job_obj.contact_name.email)
        # to_email.append(job_obj.job_owner.email)
        # if job_obj.contact_name.id != request.user.id:
        #     notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                 description=description,image="/static/notifications/icon/company/Candidate.png",
        #                                                                 target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                     job_obj.id))
        # if job_obj.job_owner.id != request.user.id:
        #     notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                 description=description,image="/static/notifications/icon/company/Candidate.png",
        #                                                                 target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                     job_obj.id))
        # all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        # for i in all_assign_users:
        #     if i.recruiter_type_internal:
        #         to_email.append(i.recruiter_id.email)
        #         if i.recruiter_id.id != request.user.id:
        #             notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                 description=description,image="/static/notifications/icon/company/Candidate.png",
        #                                                                 target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                     job_obj.id))
        # description="Your profile has been succesfully submitted for the job"+job_obj.job_title+" by "+agency_name
        # notify.send(request.user, recipient=User.objects.get(id=internal_candidate.candidate_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                 description=description,image="/static/notifications/icon/candidate/Application_Submission.png",
        #                                                                 target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
        # all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
        # stage_detail=''
        # if not current_stage==None:
        #     if current_stage.name=='Interview' :
        #         stage_detail='Interview'
        #         description="You have one application to review for the job "+job_obj.job_title
        #         for i in all_assign_users:
        #             if i.recruiter_type_internal:
        #                 if i.recruiter_id.id != request.user.id:
        #                     notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                         description=description,image="/static/notifications/icon/company/Application_Review.png",
        #                                                                         target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                             job_obj.id))
        #     elif current_stage.name=='Application Review':
        #         stage_detail='Application Review'
        #         description="You have one application to review for the job "+job_obj.job_title
        #         for i in all_assign_users:
        #             if i.recruiter_type_internal:
        #                 if i.recruiter_id.id != request.user.id:
        #                     notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
        #                                                                         description=description,image="/static/notifications/icon/company/Application_Review.png",
        #                                                                         target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
        #                                                                             job_obj.id))
        # to_email=list(set(to_email))
        # mail_subject = "New Candidate submission"
        # html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"New candidate has been submitted by "+request.user.first_name+" "+request.user.last_name+" – <a href="+header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(job_obj.id)+" >Applicant profile link.</a> Please login to review"})
        # from_email = settings.EMAIL_HOST_USER
        # msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=to_email)
        # msg.attach_alternative(html_content, "text/html")
        # # try:
        # msg.send()
        # return redirect('agency:created_job_view', id=job_obj.id)
    return render(request, "agency/ATS/internal_submit_candidate.html", context)




def job_applied_candidates_view(request, id):
    context = {}
    context = {}
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['SalaryView'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Salary':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        job_obj = models.JobCreation.objects.get(id=id)
        job_workflow_obj = models.JobWorkflow.objects.get(job_id=job_obj)
        candidates = models.AppliedCandidate.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                            job_id=job_obj)
        candidates_array = [i.candidate.id for i in candidates]
        
        candidate_job_apply_detail = CandidateModels.candidate_job_apply_detail.objects.filter(
            candidate_id__in=candidates_array)
        candidate_stages_data = []
        secure = False
        candidatetype = ''
        candidate_fname=''
        candidate_lname=''
        resume=''
        contactno=''
        requested=''

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
                                                        agency_id=job_obj.agency_id,
                                                        stage=stage_id,
                                                        stage_name=request.POST.get('stage_name'),
                                                        user_id=request.user,
                                                        template=template_id,
                                                        sequence_number=int(onthego_last_stages.sequence_number) + 1)
                    for candidate in candidates_array:
                        notify.send(request.user, recipient=User.objects.get(id=candidate), verb="New stage",
                                    description="New stage has been added to your profile for the job "+job_obj.job_title+". Please visit to appear for interview round.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/agency")
        agency_id = models.Agency.objects.get(user_id=request.user.id)
        for candidate_id in candidates_array:
            candidate_obj = User.objects.get(id=candidate_id)

            if request.method == 'POST':
                if 'add_stage_submit' in request.POST:
                    if flag:
                        if models.CandidateJobStagesStatus.objects.filter(candidate_id=User.objects.get(id=candidate_id),
                                                                        job_id=job_obj,template=template_id).exists():
                            print('Template Already assigned to this candidate')
                        else:
                            candidate_job_stages = models.CandidateJobStagesStatus.objects.filter(agency_id=agency_id,
                                                                                                candidate_id=candidate_obj,
                                                                                                job_id=job_obj).order_by('sequence_number')
                            candidate_job_last_stage = candidate_job_stages.last()

                            if candidate_job_last_stage.stage.name != 'Job Offer':
                                if candidate_job_last_stage.status != -1:
                                    status = 0
                                    if candidate_job_last_stage.action_performed or candidate_job_last_stage.stage.name == 'Job Applied':
                                        status = 1
                                    models.CandidateJobStagesStatus.objects.create(agency_id=agency_id,candidate_id=candidate_obj,
                                                                                job_id=job_obj,stage=new_created_stage.stage,
                                                                                template=new_created_stage.template,
                                                                                sequence_number=int(candidate_job_last_stage.sequence_number) + 1,
                                                                                status=status,custom_stage_name=request.POST.get('stage_name'))

            stages = models.CandidateJobStagesStatus.objects.filter(agency_id=agency_id,
                                                                    candidate_id=candidate_obj,
                                                                    job_id=job_obj).order_by('sequence_number')

            current_stage = ''
            if len(stages.filter(status=1))==0:
                current_stage = 'Waiting For Stage'
            else:
                current_stage = stages.filter(status=1)[0].stage.name
            # secure_resume
            # if candidate_id in agency_submit_candidate:
            #     candidatetype = 'External'
            # else:
            #     candidatetype = 'Internal'
            candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(
                candidate_id=User.objects.get(id=candidate_id))
            # if AgencyModels.CandidateSecureData.objects.filter(candidate_id=User.objects.get(id=candidate_id),job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id)).exists():
            #     data=AgencyModels.CandidateSecureData.objects.get(candidate_id=User.objects.get(id=candidate_id),job_id=job_obj,company_id=models.Company.objects.get(user_id=request.user.id))
                
            #     if data.is_accepted:
            #         candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(
            #             candidate_id=User.objects.get(id=candidate_id))
            #         resume = candidate_detail.resume.url
            #         contactno=candidate_detail.contact
            #         candidate_fname=candidate_detail.candidate_id.first_name+' '+candidate_detail.candidate_id.last_name
            #         secure = False
            #         requested=False
            #     elif data.is_request:
            #         get_agency=models.AssociateCandidateAgency.objects.get(candidate_id=User.objects.get(id=candidate_id),job_id=job_obj)
            #         agency_candidate_detail=AgencyModels.InternalCandidateBasicDetail.objects.get(candidate_id=User.objects.get(id=candidate_id),agency_id=get_agency.agency_id)
            #         secure = True
            #         requested = True
            #         resume = agency_candidate_detail.secure_resume_file.url
            #         candidate_fname=agency_candidate_detail.candidate_custom_id
            #     elif not data.is_request:
            #         get_agency = models.AssociateCandidateAgency.objects.get(candidate_id=User.objects.get(id=candidate_id),
            #                                                                  job_id=job_obj)
            #         agency_candidate_detail = AgencyModels.InternalCandidateBasicDetail.objects.get(
            #             candidate_id=User.objects.get(id=candidate_id), agency_id=get_agency.agency_id)
            #         secure = True
            #         requested = False
            #         if agency_candidate_detail.secure_resume_file:
            #             resume = agency_candidate_detail.secure_resume_file.url
            #         else:
            #             resume=agency_candidate_detail.resume.url
            #         candidate_fname=agency_candidate_detail.candidate_custom_id
            # else:
            resume = candidate_detail.resume.url
            contactno = candidate_detail.contact
            candidate_fname = candidate_detail.candidate_id.first_name + ' ' + candidate_detail.candidate_id.last_name
            candidate_lname = candidate_detail.candidate_id.last_name
            print("==============================",resume)
            data = {'id': User.objects.get(id=candidate_id), 'current_stage':current_stage,'stages': stages,'requested':requested, 'candidate_detail':candidate_detail,'secure': secure,'candidatetype':candidatetype,'contactno':contactno,'resume':resume,'candidate_fname':candidate_fname,'candidate_lname':candidate_lname}
            candidate_stages_data.append(data)
        
        context['candidates']= candidate_job_apply_detail
        context['candidate_stages_data']=candidate_stages_data
        context['job_obj']=job_obj
        context['job_id']= job_obj.id
        context['job_workflow_obj']=job_workflow_obj
        return render(request, "agency/ATS/internal-applied-candidate-view.html",context)
    else:
        return redirect('agency:agency_Profile')  



def job_close(request,jobid):
    job_obj=models.JobCreation.objects.get(id=jobid,agency_id=models.Agency.objects.get(user_id=request.user.id))
    job_obj.close_job=True
    job_obj.close_job_targetdate=True
    job_obj.close_job_at=datetime.datetime.now()
    job_obj.save()
    # Notification
    current_site = get_current_site(request)
    header=request.is_secure() and "https" or "http"
    to_email=[]
    job_assign_recruiter = models.AgencyAssignJob.objects.filter(job_id=job_obj)
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
    return redirect('agency:job_applied_candidates_view',id=jobid)



from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.safestring import mark_safe


def agency_portal_candidate_tablist(request, candidate_id, job_id):
    context = {}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['SalaryView'] = False
        context['permission'] = check_permission(request)
        for permissions in context['permission']:
            if permissions.permissionsmodel.modelname == 'Salary':
                print(permissions.permissionname, '====', permissions.permissionsmodel.modelname)
                if permissions.permissionname == 'View':
                    context['SalaryView'] = True
        job_obj = models.JobCreation.objects.get(id=job_id)
        candidate_obj = User.objects.get(id=candidate_id)
        agency_id = models.Agency.objects.get(user_id=request.user.id)
        job_workflow_obj = models.JobWorkflow.objects.get(job_id=job_obj)
        chat=''
        groupmessage=''
        uniquecode=''
        all_assign_users = models.AgencyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True)
        # if ChatModels.GroupChat.objects.filter(job_id=job_obj).exists():
        #     chat = ChatModels.GroupChat.objects.get(job_id=job_obj,candidate_id=candidate_obj)
        #     groupmessage=ChatModels.Message.objects.filter(chat=chat)
        #     uniquecode=mark_safe(json.dumps(chat.unique_code))
        #     channel_layer = get_channel_layer()
        #     async_to_sync(channel_layer.group_send)(
        #         f"chat_{chat.unique_code}",
        #         {
        #             'type': 'chat_activity',
        #             'message': json.dumps({'type': "join", 'first_name': request.user.id})
        #         }
        #     )
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
                    interview_template = models.InterviewTemplate.objects.get(agency_id=stage_obj.agency_id,
                                                                            template_id=stage_obj.template)
                    schedule_obj, created = models.InterviewSchedule.objects.update_or_create(candidate_id=candidate_obj,
                                                                                            job_id=job_obj,
                                                                                            agency_id=stage_obj.agency_id,
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
                                        job_obj.id)+"/agency")
                    for participant in request.POST.getlist('interviewers'):
                        participant_obj = User.objects.get(id=participant)
                        schedule_obj.participants.add(participant_obj)
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,agency_id=stage_obj.agency_id,defaults={
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
                    candidate_job_stages = models.CandidateJobStagesStatus.objects.filter(agency_id=agency_id,
                                                                                        candidate_id=candidate_obj,
                                                                                        job_id=job_obj).order_by('sequence_number')
                    candidate_job_last_stage = candidate_job_stages.last()

                    if candidate_job_last_stage.stage.name != 'Job Offer':
                        if candidate_job_last_stage.status != -1:
                            status = 0
                            if candidate_job_last_stage.action_performed or candidate_job_last_stage.stage.name == 'Job Applied':
                                status = 1
                            models.CandidateJobStagesStatus.objects.create(agency_id=agency_id,
                                                                        candidate_id=candidate_obj,
                                                                        job_id=job_obj, stage=stage_id,
                                                                        template=template_id,
                                                                        sequence_number=int(candidate_job_last_stage.sequence_number) + 1,
                                                                        status=status,custom_stage_name=request.POST.get('stage_name'))
                            notify.send(request.user, recipient=candidate_obj, verb="New stage",
                                    description="New stage has been added to your profile for the job "+job_obj.job_title+". Please visit to appear for interview round.",image="/static/notifications/icon/company/Job_Create.png",
                                    target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                        job_obj.id)+"/agency")
            elif 'withdraw_candidate' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                defaults={'withdraw_by':User.objects.get(id=request.user.id),'is_withdraw':True})
                models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,agency_id=agency_id,defaults={
                                                                    'withdraw':True,'update_at':datetime.datetime.now()})
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                notify.send(request.user, recipient=candidate_obj, verb="Withdraw",
                                description="You have withdrawn your application from Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/agency")
                job_assign_recruiter = models.AgencyAssignJob.objects.filter(job_id=job_obj)
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                if not current_stage==None:
                    for i in all_assign_users:
                        if i.recruiter_type_internal:
                            if i.recruiter_id.id != request.user.id:
                                notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Withdraw",
                                                                                    description=candidate_obj.first_name+" "+candidate_obj.last_name+" has been withdrawn your from Job"+str(job_obj.job_title),image="/static/notifications/icon/company/Application_Review.png",
                                                                                    target_url=header+"://"+current_site.domain+"/agency/agency_portal_candidate_tablist/"+str(candidate_obj.id)+"/" + str(
                                                                                        job_obj.id))
            elif 'hire_candidate' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                agency_id=agency_id,
                                                                defaults={
                                                                    'hire_by': User.objects.get(id=request.user.id),
                                                                    'is_hired': True})
                job_stages = models.CandidateJobStagesStatus.objects.filter(
                    agency_id=agency_id,
                    candidate_id=candidate_obj,
                    job_id=job_obj).order_by('sequence_number').last()
                job_workflow = models.JobWorkflow.objects.get(job_id=job_obj)
                if job_workflow.withworkflow:
                    job_stages.status = 1
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,agency_id=agency_id,defaults={
                                                                    'current_stage':job_stages.stage,'next_stage':None,
                                                                    'action_required':'By Agency','update_at':datetime.datetime.now()})
                    job_stages.save()
                if job_workflow.onthego:
                    job_offer_stage = CandidateModels.Stage_list.objects.get(name='Job Offer')
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,agency_id=agency_id,defaults={
                                                                    'current_stage':job_offer_stage,'next_stage':None,
                                                                    'action_required':'By Agency','update_at':datetime.datetime.now()})
                    models.CandidateJobStagesStatus.objects.create(agency_id=agency_id,candidate_id=candidate_obj,
                        job_id=job_obj,stage=job_offer_stage,sequence_number=int(job_stages.sequence_number) + 1,status=1,custom_stage_name='Job Offer')

            elif 'reenter_candidate' in request.POST:
                models.CandidateJobStatus.objects.update_or_create(candidate_id=candidate_obj,
                                                                job_id=job_obj,
                                                                agency_id=models.Agency.objects.get(
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
                                    job_id)+"/agency")

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
                            action_required='schedule interview By Agency'
                        else:
                            action_required='Perform '+ ' '+'By Candidate'
                        new_stage_status.save()
                        notify.send(request.user, recipient=candidate_obj, verb="Interview Round",
                                description="Please start your interview round : "+new_stage_status.custom_stage_name,image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/agency")
                if 'reject' in request.POST:
                    stage_obj.status = -1
                    stage_obj.action_performed = True
                    stage_obj.assessment_done = True
                    reject=True
                    current_stage=stage_obj.stage
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,agency_id=stage_obj.agency_id,defaults={
                                                                    'reject':True,
                                                                    'update_at':datetime.datetime.now()})
                    stage_obj.save()
                    notify.send(request.user, recipient=candidate_obj, verb="Application Rejected",
                                description="Sorry! Your profile has been rejected for the Job "+str(job_obj.job_title),image="/static/notifications/icon/company/Job_Create.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                    job_obj.id)+"/agency")
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
                models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=candidate_obj,agency_id=stage_obj.agency_id,defaults={
                                                                    'current_stage':current_stage,'currentcompleted':currentcompleted,'next_stage':next_stage,
                                                                    'action_required':action_required,'update_at':datetime.datetime.now()})
        candidate_detail = CandidateModels.candidate_job_apply_detail.objects.get(candidate_id=candidate_obj)
        internal_users = models.InternalUserProfile.objects.filter(agency_id=agency_id)
        stages_status = models.CandidateJobStagesStatus.objects.filter(agency_id=agency_id,
                                                                    candidate_id=candidate_obj,
                                                                    job_id=job_obj).order_by('sequence_number')
        interview_schedule_data = None
        job_offer_data = None
        custom_stage_template = None
        stages_data = []
        for stage in stages_status:
            stage_dict = {'stage': stage, 'result': ''}

            if stage.stage.name == 'Interview':
                print('\n\nin Interview')
                interview_schedule_obj = models.InterviewSchedule.objects.filter(candidate_id=candidate_obj,job_id=job_obj,
                                                        agency_id=stage.agency_id,
                                                        template=stage.template,
                                                        job_stages_id=stage)
                if interview_schedule_obj.exists():
                    interview_schedule_data = interview_schedule_obj[0]
            if stage.stage.name == 'Job Offer':
                print('\n\nin Job Offer')
                job_offer_obj = models.JobOffer.objects.filter(candidate_id=candidate_obj, job_id=job_obj,
                                                                                agency_id=stage.agency_id,
                                                                                job_stages_id=stage)
                if job_offer_obj.exists():
                    job_offer_data = job_offer_obj[0]
            if stage.stage.name == 'Custom':
                custom_stage_template = models.CustomTemplate.objects.get(agency_id=stage.agency_id,
                                                                        template=stage.template)
                print('custom_stage_template', custom_stage_template)

            if stage.status == 2 or stage.status == -1 or stage.status == 3:
                if stage.stage.name == 'JCR':
                    jcr_result = CandidateModels.JcrRatio.objects.get(agency_id=stage.agency_id,
                                                                    candidate_id=stage.candidate_id,
                                                                    job_id=job_obj,
                                                                    template=stage.template)
                    stage_dict['result'] = jcr_result

                if stage.stage.name == 'Prerequisites':
                    prerequisites_result = CandidateModels.Agency_PreRequisitesFill.objects.get(agency_id=stage.agency_id,
                                                                                        candidate_id=stage.candidate_id,
                                                                                        job_id=job_obj,
                                                                                        template=stage.template)
                    stage_dict['result'] = prerequisites_result

                if stage.stage.name == 'MCQ Test':
                    if not stage.reject_by_candidate:
                        mcq_test_result = CandidateModels.Agency_Mcq_Exam_result.objects.get(agency_id=stage.agency_id,
                                                                                    candidate_id=stage.candidate_id,
                                                                                    job_id=job_obj,
                                                                                    template=stage.template)
                        stage_dict['result'] = mcq_test_result
                    else:
                        stage_dict['result'] = None

                # if stage.stage.name == 'Descriptive Test':
                #     if not stage.reject_by_candidate:
                #         descriptive_result = CandidateModels.Descriptive_Exam_result.objects.get(agency_id=stage.agency_id,
                #                                                                                 candidate_id=stage.candidate_id,
                #                                                                                 job_id=job_obj,
                #                                                                                 template=stage.template)
                #         stage_dict['result'] = descriptive_result
                #     else:
                #         stage_dict['result'] = None

                if stage.stage.name == 'Image Test':
                    if not stage.reject_by_candidate:
                        image_result = CandidateModels.Agency_Image_Exam_result.objects.get(agency_id=stage.agency_id,
                                                                                    candidate_id=stage.candidate_id,
                                                                                    job_id=job_obj,
                                                                                    template=stage.template)
                        stage_dict['result'] = image_result
                    else:
                        stage_dict['result'] = None

                    
                # if stage.stage.name == 'Audio Test':
                #     if not stage.reject_by_candidate:
                #         audio_result = CandidateModels.AudioExamAttempt.objects.get(candidate_id=stage.candidate_id,
                #                                                                     agency_id=stage.agency_id,
                #                                                                     job_id=stage.job_id,audio_question_paper__exam_template__template=stage.template)
                #         stage_dict['result'] = audio_result
                #     else:
                #         stage_dict['result'] = None


                # if stage.stage.name == 'Coding Test':
                #     if not stage.reject_by_candidate:
                #         exam_config = models.CodingExamConfiguration.objects.get(template_id=stage.template)
                #         coding_result = CandidateModels.Coding_Exam_result.objects.get(candidate_id=stage.candidate_id,
                #                                                                     agency_id=stage.agency_id,
                #                                                                     template=stage.template,
                #                                                                     job_id=stage.job_id)
                #         stage_dict['result'] = coding_result
                #     else:
                #         stage_dict['result'] = None


                # if stage.stage.name == 'Custom':
                #     custom_results = models.CustomResult.objects.get(candidate_id=stage.candidate_id,agency_id=stage.agency_id,
                #                                                                    custom_template__template=stage.template,
                #                                                                    job_id=stage.job_id)
                #     print('custom_results', custom_results.scorecard_results.all())
                #     stage_dict['result'] = custom_results

            stages_data.append(stage_dict)

        collaboration_obj = models.Collaboration.objects.filter(agency_id=job_obj.agency_id, candidate_id=candidate_obj,
                                                                job_id=job_obj)

        candidate_job_status = None
        if models.CandidateJobStatus.objects.filter(candidate_id=candidate_obj, job_id=job_obj).exists():
            candidate_job_status = models.CandidateJobStatus.objects.get(candidate_id=candidate_obj, job_id=job_obj)

        candidate_apply_details = None
        if models.AppliedCandidate.objects.filter(candidate=candidate_obj,agency_id=job_obj.agency_id).exists():
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
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
        # if add_stage_submit:
        # if withdraw_candidate:
        # if hire_candidate=:
        # if reenter_candidate:
        if shortlist_candidate:
            description="Application Shortlisted: Your profile has been shortlisted, please wait for further instruction."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Application Shortlisted",
                        description=description,image="/static/notifications/icon/candidate/Shortlisted.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
            if not next_stage==None:
                if next_stage.name=="JCR":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="JCR",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                elif next_stage.name=="Prerequisites":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Prerequisites",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                elif next_stage.name=="MCQ Test":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="MCQ",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                elif next_stage.name=="Descriptive Test":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Descriptive",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                elif next_stage.name=="Image Test":
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Image",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                elif next_stage.name=="Audio Test": 
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Audio",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")   
                elif next_stage.name=="Coding Test": 
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Coding",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                elif next_stage.name=="Custom":    
                    description="Please start your interview round : Work Flow stage Name"
                    notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Custom",
                                description=description,image="/static/notifications/icon/candidate/mcq.png",
                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")

        if reject_candidate:
            description="Sorry! Your profile has been rejected for the Job "+job_obj.job_title
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Applicationn Rejected:",
                        description=description,image="/static/notifications/icon/candidate/Application_Rejected.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
        if onhold_candidate:
            description="Application Shortlisted: Your profile has been shortlisted, please wait for further instruction."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="Candidate submission",
                        description=description,image="/static/notifications/icon/candidate/Shortlisted.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
        if add_stage_submit:
            description="New stage has been added to your profile for the job "+job_obj.job_title+". Please visit to appear for interview round."
            notify.send(request.user, recipient=User.objects.get(id=candidate_obj.id),verb="New stage",
                        description=description,image="/static/notifications/icon/candidate/New stage.png",
                        target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
        context['job_obj']= job_obj
        context['candidate_obj']= candidate_obj
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
        context['candidate_education']=candidate_education
        context['candidate_experience']=candidate_experience
        context['candidate_certification']=candidate_certification
        context['candidate_award']=candidate_award
        context['candidate_portfolio']=candidate_portfolio
        context['candidate_preferences']=candidate_preferences
        context['chatObject']= chat
        context['groupmessage']=groupmessage 
        context['chat_id_json']= uniquecode
        return render(request, "agency/ATS/agency-portal-candidate-tablist.html", context)
    else:
        return redirect('agency:agency_Profile')




def job_view(request, id):
    context = {}
    job_obj = models.JobCreation.objects.get(id=id)
    context['job_obj']=job_obj
    context['active_job_count'] = len(
        models.JobCreation.objects.filter(agency_id=job_obj.agency_id, close_job=False,
                                                 close_job_targetdate=False,
                                                 is_publish=True))
    context['close_job_count'] = len(
        models.JobCreation.objects.filter(agency_id=job_obj.agency_id, close_job=True))
    context['last_close_job'] = models.JobCreation.objects.filter(agency_id=job_obj.agency_id,
                                                                         close_job=True).order_by(
        '-close_job_at').first()
    context['latest_10_job'] = models.JobCreation.objects.filter(agency_id=job_obj.agency_id,
                                                                        close_job=False,
                                                                        close_job_targetdate=False,
                                                                        is_publish=True).order_by(
        '-publish_at')
    if 'view_job' in request.session:
        del request.session['view_job']
        del request.session['job_type']
    if request.user.is_authenticated:
        if request.user.is_candidate:
            print("==========================")
            request.session['view_job']=job_obj.id
            request.session['job_type']='agency'
            return redirect('candidate:job_view')
    else:
        return render(request, 'agency/ATS/job-opening-view.html', context)


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
    agency = stage_id.agency_id
    total_questions = exam_config.total_question
    assignment_type = exam_config.assignment_type
    assessment_done = stage_id.assessment_done
    print('\n\n\nassignment_type', assignment_type)
    if exam_config.technology == 'backend':
        print('\n\nin backend section ')
        context = {}
        all_files = CandidateModels.AgencyCodingBackEndExamFill.objects.filter(candidate_id=candidate,job_id=stage_id.job_id,
                                                                         template=stage_id.template,
                                                                         agency_id=agency).order_by('exam_question_id')
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
                    CandidateModels.AgencyCodingScoreCardFill.objects.update_or_create(candidate_id=candidate,
                                                                                 agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                               agency_id=agency,
                                                                               template=stage_id.template,
                                                                               job_id=stage_id.job_id, defaults={
                        'coding_pdf': path + candidate.first_name + "coding.pdf"})

                # pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                return redirect('agency:agency_portal_candidate_tablist', candidate.id,stage_id.job_id.id)

            if 'marking_submit' in request.POST:
                coding_result = CandidateModels.AgencyCoding_Exam_result.objects.get(candidate_id=candidate,
                                                                               agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 agency_id=agency,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                # pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                models.Tracker.objects.update_or_create(job_id=stage_id.job_id,candidate_id=candidate,agency_id=agency,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
                return redirect('agency:agency_portal_candidate_tablist', candidate.id, stage_id.job_id.id)
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
        return render(request, "agency/ATS/back_end_view_code.html", context)
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
        all_front_end_codes = CandidateModels.AgencyCodingFrontEndExamFill.objects.filter(candidate_id=candidate,
                                                                                    job_id=stage_id.job_id,
                                                                                    template=stage_id.template,
                                                                                    agency_id=agency).order_by('exam_question_id')
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
                    CandidateModels.AgencyCodingScoreCardFill.objects.update_or_create(candidate_id=candidate,
                                                                                 agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 agency_id=agency,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                # pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                return redirect('agency:agency_portal_candidate_tablist', candidate.id,stage_id.job_id.id)

            if 'marking_submit' in request.POST:
                print('\n\nin marking_submit section ')
                coding_result = CandidateModels.AgencyCoding_Exam_result.objects.get(candidate_id=candidate,
                                                                               agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 agency_id=agency,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                # pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                models.Tracker.objects.update_or_create(job_id=stage_id.job_id,candidate_id=candidate,agency_id=agency,defaults={
                                                                'action_required':'Decision Making by agency','update_at':datetime.datetime.now()})
                return redirect('agency:agency_portal_candidate_tablist', candidate.id, stage_id.job_id.id)
        return render(request, "agency/ATS/front_end_code_view.html", context)




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
        if models.AgencyAssignJob.objects.filter(job_id=job_obj).exists():
            get_users = models.AgencyAssignJob.objects.filter(job_id=job_obj,recruiter_type_internal=True)
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


def collaboration(request):
    if request.method == 'POST':
        job_obj = models.JobCreation.objects.get(id=request.POST.get('job_id'))
        candidate_obj = User.objects.get(id=request.POST.get('candidate_id'))
        if request.FILES.get('attachfile-box'):
            attachment = request.FILES.get('attachfile-box')
        else:
            attachment = None
        collaboration_obj = models.Collaboration.objects.create(agency_id=job_obj.agency_id,
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




def descriptive_assessment(request):
    if request.method == 'POST':
        if 'assess' in request.POST:
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
            questions_obj = CandidateModels.AgencyDescriptive_Exam.objects.filter(candidate_id=stage_obj.candidate_id,
                                                            agency_id=stage_obj.agency_id,
                                                            job_id=stage_obj.job_id,template=stage_obj.template).order_by('id')
            print('questions_obj', questions_obj)
            return render(request, "agency/ATS/descriptive_assesment.html", {'questions_obj': questions_obj,'stage_id':stage_obj.id})
        if 'submit_marks' in request.POST:
            print('\n\n\nstggg', request.POST.get('stage'))
            print('\n\n\nmarksssssss', request.POST.getlist('marks_given'))
            marks_given = request.POST.getlist('marks_given')
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage'))
            exam_name = models.DescriptiveExamTemplate.objects.get(agency_id=stage_obj.agency_id,
                                                             template=stage_obj.template)
            questions_obj = CandidateModels.AgencyDescriptive_Exam.objects.filter(candidate_id=stage_obj.candidate_id,
                                                                            agency_id=stage_obj.agency_id,
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
            getresult, created = CandidateModels.AgencyDescriptive_Exam_result.objects.update_or_create(candidate_id=stage_obj.candidate_id,
                                                                                         agency_id=stage_obj.agency_id,
                                                                                         job_id=stage_obj.job_id,
                                                                                         template=stage_obj.template,
                                                                                         defaults={
                                                                                             'total_question': total_que,
                                                                                             'answered': ans_que,
                                                                                             'not_answered': no_ans_que,
                                                                                             'obain_time': 10,
                                                                                             'mcq_pdf': path + stage_obj.candidate_id.first_name + "Descriptive.pdf"})

            # pdfkit.from_string(a, output_path=path + stage_obj.candidate_id.first_name + "Descriptive.pdf")
            stage_obj.assessment_done = True
            stage_obj.save()
            # models.Tracker.objects.update_or_create(job_id=stage_obj.job_id,candidate_id=stage_obj.candidate_id,company_id=stage_obj.company_id,defaults={
            #                                                     'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
            return redirect('agency:agency_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,job_id=stage_obj.job_id.id)
    else:
        return HttpResponse(False)


def audio_video_assessment(request):
    if request.method == 'POST':
        if 'assess' in request.POST:
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage_id'))
            audio_attempt_obj = CandidateModels.AgencyAudioExamAttempt.objects.get(candidate_id=stage_obj.candidate_id,
                                                            agency_id=stage_obj.agency_id,
                                                            job_id=stage_obj.job_id,
                                                            audio_question_paper__exam_template__template=stage_obj.template)
            all_questions_obj = audio_attempt_obj.audio_question_attempts.all().order_by('id')
            return render(request, "agency/ATS/audio_video_assessment.html",
                          {'questions_obj': all_questions_obj,'stage_id':stage_obj.id,
                           'is_video':audio_attempt_obj.audio_question_paper.exam_template.is_video})
        if 'submit_marks' in request.POST:

            marks_given = request.POST.getlist('marks_given')
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=request.POST.get('stage'))
            exam_name = models.AudioExamTemplate.objects.get(agency_id=stage_obj.agency_id,
                                                             template=stage_obj.template)
            audio_attempt_obj = CandidateModels.AgencyAudioExamAttempt.objects.get(candidate_id=stage_obj.candidate_id,
                                                                            agency_id=stage_obj.agency_id,
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
            getresult, created = CandidateModels.AgencyAudioExamAttempt.objects.update_or_create(
                candidate_id=stage_obj.candidate_id,
                agency_id=stage_obj.agency_id,
                job_id=stage_obj.job_id,audio_question_paper__exam_template__template=stage_obj.template,
                defaults={
                    'mcq_pdf': path + stage_obj.candidate_id.first_name + "Audio.pdf"})

            # pdfkit.from_string(a, output_path=path + stage_obj.candidate_id.first_name + "Audio.pdf")
            # models.Tracker.objects.update_or_create(job_id=stage_obj.job_id,candidate_id=stage_obj.candidate_id,company_id=stage_obj.company_id,defaults={
            #                                                     'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
            return redirect('agency:agency_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,job_id=stage_obj.job_id.id)
    else:
        return HttpResponse(False)


# import requests


def agency_coding_assessment(request,id):
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
    agency = stage_id.agency_id
    total_questions = exam_config.total_question
    assignment_type = exam_config.assignment_type
    assessment_done = stage_id.assessment_done
    print('\n\n\nassignment_type', assignment_type)
    if exam_config.technology == 'backend':
        print('\n\nin backend section ')
        context = {}
        all_files = CandidateModels.AgencyCodingBackEndExamFill.objects.filter(candidate_id=candidate,job_id=stage_id.job_id,
                                                                         template=stage_id.template,
                                                                         agency_id=agency).order_by('exam_question_id')
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
                    CandidateModels.AgencyCodingScoreCardFill.objects.update_or_create(candidate_id=candidate,
                                                                                 agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                               agency_id=agency,
                                                                               template=stage_id.template,
                                                                               job_id=stage_id.job_id, defaults={
                        'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                return redirect('agency:agency_portal_candidate_tablist', candidate.id,stage_id.job_id.id)

            if 'marking_submit' in request.POST:
                coding_result = CandidateModels.AgencyCoding_Exam_result.objects.get(candidate_id=candidate,
                                                                               agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 agency_id=agency,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                models.Tracker.objects.update_or_create(job_id=stage_id.job_id,candidate_id=candidate,agency_id=agency,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
                return redirect('agency:agency_portal_candidate_tablist', candidate.id, stage_id.job_id.id)
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
        return render(request, "agency/ATS/back_end_view_code.html", context)
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
        all_front_end_codes = CandidateModels.AgencyCodingFrontEndExamFill.objects.filter(candidate_id=candidate,
                                                                                    job_id=stage_id.job_id,
                                                                                    template=stage_id.template,
                                                                                    agency_id=agency).order_by('exam_question_id')
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
                    CandidateModels.AgencyCodingScoreCardFill.objects.update_or_create(candidate_id=candidate,
                                                                                 agency_id=agency,
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
                getresult, created = CandidateModels.AgencyCoding_Exam_result.objects.update_or_create(candidate_id=candidate,
                                                                                                 agency_id=agency,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                return redirect('company:company_portal_candidate_tablist', candidate.id,stage_id.job_id.id)

            if 'marking_submit' in request.POST:
                print('\n\nin marking_submit section ')
                coding_result = CandidateModels.AgencyCoding_Exam_result.objects.get(candidate_id=candidate,
                                                                               agency_id=agency,
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
                                                                                                 agency_id=agency,
                                                                                                 template=stage_id.template,
                                                                                                 job_id=stage_id.job_id,
                                                                                                 defaults={
                                                                                                     'coding_pdf': path + candidate.first_name + "coding.pdf"})

                pdfkit.from_string(a, output_path=path + candidate.first_name + "coding.pdf")
                models.Tracker.objects.update_or_create(job_id=stage_id.job_id,candidate_id=candidate,agency_id=agency,defaults={
                                                                'action_required':'Decision Making by Company','update_at':datetime.datetime.now()})
                return redirect('agency:agency_portal_candidate_tablist', candidate.id, stage_id.job_id.id)
        return render(request, "agency/ATS/front_end_code_view.html", context)


def send_offer(request,id):
    if request.method == 'POST':
        if models.CandidateJobStagesStatus.objects.filter(id=id).exists():
            print('request.POST)',request.POST.get('offer-letter'))
            print('request.files)',request.FILES.get('offer-letter'))
            user_obj = User.objects.get(id=request.user.id)
            stage_obj = models.CandidateJobStagesStatus.objects.get(id=id)
            job_offer_obj = models.JobOffer.objects.create(agency_id=stage_obj.agency_id,
                                                           candidate_id=stage_obj.candidate_id,
                                                           user_id=user_obj,job_id=stage_obj.job_id,
                                                           job_stages_id=stage_obj,
                                                           candidate_name=request.POST.get('candidate-name'),
                                                           bond=request.POST.get('bond'),
                                                           NDA=request.POST.get('nda'),
                                                           offer_letter=request.FILES.get('offer-letter'))
            negotiation_obj = models.OfferNegotiation.objects.create(designation=request.POST.get('designation'),
                                                                     annual_ctc=request.POST.get('annual-ctc'),
                                                                     notice_period=request.POST.get('notice-period'),
                                                                     joining_date=request.POST.get('joining-date'),
                                                                     other_details=request.POST.get('offer-other-details'),
                                                                     from_company=True)
            job_offer_obj.negotiations.add(negotiation_obj)
            stage_obj.assessment_done = True
            stage_obj.save()
            models.Tracker.objects.update_or_create(job_id=job_offer_obj.job_id,candidate_id=job_offer_obj.candidate_id,agency_id=job_offer_obj.agency_id,defaults={
                                                                'action_required':'Negotiation By Company/Candidate','update_at':datetime.datetime.now()})
            current_site = get_current_site(request)
            header=request.is_secure() and "https" or "http" 
            notify.send(request.user, recipient=User.objects.get(id=job_offer_obj.candidate_id.id), verb="Hire",
                            description="Congratulation! You have been Hired for Job "+job_offer_obj.job_title+". Please accept the offer Letter.",image="/static/notifications/icon/company/Job_Create.png",
                            target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/" + str(
                                job_offer_obj.job_id))
            return redirect('agency:agency_portal_candidate_tablist', candidate_id=stage_obj.candidate_id.id,
                            job_id=stage_obj.job_id.id)
        else:
            return HttpResponse('False')
    else:
        return HttpResponse(False)




def candidate_negotiate_offer(request,id):
    context={}
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
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
        return render(request, 'agency/ATS/candidate_negotiate_offer.html', context)
    else:
        return redirect('agency:agency_Profile')

def notification_list(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        return render(request,"agency/ATS/notification_list.html",context)
    else:
        return redirect('agency:agency_Profile')


def daily_submission(request):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['candidates'] = models.DailySubmission.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),create_at__startswith=datetime.date.today())
        return render(request,"agency/ATS/daily_submission.html",context)
    else:
        return redirect('agency:agency_Profile')

def submit_candidate_daily(request,submitid):
    if request.method=='POST':
        if models.DailySubmission.objects.filter(id=submitid).exists():
            getdata=models.DailySubmission.objects.get(id=submitid)
            getdata.applied=True
            getdata.save()
            if not User.objects.filter(email=getdata.internal_candidate_id.email.lower()).exists():
                password = get_random_string(length=12)
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
                usr = User.objects.apply_candidate(email=getdata.internal_candidate_id.email.lower(), first_name=getdata.internal_candidate_id.first_name, last_name=getdata.internal_candidate_id.last_name,
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
                                                                                'name': usr.first_name + ' ' + usr.last_name,
                                                                                'email': usr.email,
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
                getdata.internal_candidate_id.candidate_id = User.objects.get(email=getdata.internal_candidate_id.email.lower())
                getdata.internal_candidate_id.save()
                add_candidate, create = CandidateModels.candidate_job_apply_detail.objects.update_or_create(
                    candidate_id=getdata.internal_candidate_id.candidate_id, defaults={
                        'gender': getdata.internal_candidate_id.gender,
                        'resume': getdata.internal_candidate_id.resume,
                        'contact': getdata.internal_candidate_id.contact,
                        'designation': getdata.internal_candidate_id.designation,
                        'notice': getdata.internal_candidate_id.notice,
                        'ctc': getdata.internal_candidate_id.ctc,
                        'expectedctc': getdata.internal_candidate_id.expectedctc,
                        'total_exper': getdata.internal_candidate_id.total_exper})

                for i in getdata.internal_candidate_id.skills.all():
                    print(type(int(i.id)))
                    main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                    add_candidate.skills.add(main_skill_obj.id)
                for i in getdata.internal_candidate_id.prefered_city.all():
                    main_city_obj = CandidateModels.City.objects.get(id=i.id)
                    add_candidate.prefered_city.add(main_city_obj.id)
                add_candidate.save()
            else:
                if not CandidateModels.candidate_job_apply_detail.objects.filter(candidate_id = getdata.internal_candidate_id.candidate_id).exists():
                    add_candidate,create=CandidateModels.candidate_job_apply_detail.objects.update_or_create(candidate_id =getdata.internal_candidate_id.candidate_id,defaults={
                                                                                    'gender' :getdata.internal_candidate_id.gender,
                                                                                    'resume' : getdata.internal_candidate_id.resume,
                                                                                    'contact' : getdata.internal_candidate_id.contact,
                                                                                    'designation' : getdata.internal_candidate_id.designation,
                                                                                    'notice' : getdata.internal_candidate_id.notice,
                                                                                    'ctc' : getdata.internal_candidate_id.ctc,
                                                                                    'expectedctc' : getdata.internal_candidate_id.expectedctc,
                                                                                    'total_exper' :  getdata.internal_candidate_id.total_exper})
                    for i in getdata.internal_candidate_id.skills.all():
                        print(type(int(i.id)))
                        main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                        add_candidate.skills.add(main_skill_obj.id)
                    for i in getdata.internal_candidate_id.prefered_city.all():
                        main_city_obj = CandidateModels.City.objects.get(id=i.id)
                        add_candidate.prefered_city.add(main_city_obj.id)
                    add_candidate.save()
                
                getdata.internal_candidate_id.candidate_id = User.objects.get(email=getdata.internal_candidate_id.email)
                getdata.internal_candidate_id.save()
                getdata.candidate_id=User.objects.get(email=getdata.email)
                getdata.save()
            if getdata.job_type=='company':
                job_obj=getdata.company_job_id
                add_company_daily_submit,update=CompanyModels.DailySubmission.objects.update_or_create(candidate_id=getdata.candidate_id,company_job_id=job_obj,defaults={
                    'company_id':job_obj.company_id,
                    'user_id':User.objects.get(id=request.user.id),
                    'job_type':'company',
                    'agency_id':models.Agency.objects.get(user_id=request.user),
                    'internal_candidate_id_agency':getdata.internal_candidate_id,
                    'internal_user_agency':getdata.internal_user,
                    'applied':True,
                    'candidate_custom_id':getdata.candidate_custom_id,
                    'first_name':getdata.first_name,
                    'last_name':getdata.last_name,
                    'email':getdata.email,
                    'gender':getdata.gender,
                    'resume':getdata.resume,
                    'secure_resume':getdata.secure_resume,
                    'secure_resume_file':getdata.secure_resume_file,
                    'contact':getdata.contact,
                    'designation':getdata.designation,
                    'current_city':getdata.current_city,
                    'notice':getdata.notice,
                    'source':getdata.source,
                    'ctc':getdata.ctc,
                    'expectedctc':getdata.expectedctc,
                    'total_exper':getdata.total_exper,
                    'profile_pic':getdata.profile_pic,
                    'verify':True,
                    'verified':True,
                })
                for i in getdata.internal_candidate_id.skills.all():
                    print(type(int(i.id)))
                    main_skill_obj = CandidateModels.Skill.objects.get(id=int(i.id))
                    add_company_daily_submit.skills.add(main_skill_obj.id)
                for i in getdata.internal_candidate_id.prefered_city.all():
                    main_city_obj = CandidateModels.City.objects.get(id=i.id)
                    add_company_daily_submit.prefered_city.add(main_city_obj.id)
                add_company_daily_submit.save()
                toemail=[getdata.internal_candidate_id.email]
                mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
                html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
                msg.attach_alternative(html_content, "text/html")
                # try:
                msg.send()
                CompanyModels.AssociateCandidateAgency.objects.update_or_create(company_id=job_obj.company_id,job_id=job_obj,agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),candidate_id=getdata.internal_candidate_id.candidate_id,
                        defaults={
                            'agency_internal_id':models.InternalCandidateBasicDetail.objects.get(id=getdata.internal_candidate_id.id)
                        })
                CompanyModels.AppliedCandidate.objects.update_or_create(company_id=job_obj.company_id,dailysubmission=add_company_daily_submit,job_id=job_obj,candidate=getdata.internal_candidate_id.candidate_id,
                        defaults={
                            'submit_type':'Agency'
                        })
                if getdata.internal_candidate_id.secure_resume:
                    models.CandidateSecureData.objects.update_or_create(
                                                            agency_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),
                                                            job_id=job_obj,
                                                            company_id=job_obj.company_id,
                                                            candidate_id=getdata.internal_candidate_id.candidate_id,
                                                            defaults={'user_id': User.objects.get(
                                                                id=request.user.id)
                                                            })
                models.AssociateJob.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                                                                            job_id=job_obj,
                                                                            internal_candidate_id=getdata.internal_candidate_id,
                                                                            internal_user=models.InternalUserProfile.objects.get(InternalUserid=request.user.id),
                                                                            defaults={'user_id' : User.objects.get(id=request.user.id)
                                                                            })
                workflow = CompanyModels.JobWorkflow.objects.get(job_id=job_obj)
                current_stage=None
                currentcompleted=False
                next_stage = None
                next_stage_sequance=0
                # onthego change
                if workflow.withworkflow:
                    print("==========================withworkflow================================")
                    workflow_stages = CompanyModels.WorkflowStages.objects.filter(workflow=workflow.workflow_id).order_by('sequence_number')
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
                                CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                        job_id=job_obj, stage=stage_list_obj,
                                                                        sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                                sequence_number = stage.sequence_number + 1
                                status = 0
                            else:
                                status = 0
                                sequence_number = stage.sequence_number + 1
                                next_stage = stage.stage
                            CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
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
                            else:
                                status = 0
                            CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=stage.sequence_number,status=status,custom_stage_name=stage.stage_name)
                if workflow.onthego:
                    print("==========================onthego================================")
                    onthego_stages = CompanyModels.OnTheGoStages.objects.filter(job_id=job_obj).order_by('sequence_number')

                    if workflow.is_application_review:
                        for stage in onthego_stages:
                            if stage.sequence_number == 1:
                                status = 2
                                sequence_number = stage.sequence_number
                                CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                        job_id=job_obj, stage=stage.stage,
                                                                        template=stage.template,
                                                                        sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                                status = 1
                                sequence_number = stage.sequence_number + 1
                                stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
                                current_stage = stage_list_obj
                                next_stage_sequance=stage.sequence_number+1
                                CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                        job_id=job_obj, stage=stage_list_obj,
                                                                        sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                            else:
                                status = 0
                                sequence_number = stage.sequence_number + 1
                                current_stage = stage_list_obj
                                CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
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
                            else:
                                status = 0
                            CompanyModels.CandidateJobStagesStatus.objects.create(company_id=stage.company_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
                action_required=''
                
                if next_stage_sequance!=0:
                    if CompanyModels.CandidateJobStagesStatus.objects.filter(company_id=job_obj.company_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj,
                                                                    sequence_number=next_stage_sequance).exists():
                        next_stage=CompanyModels.CandidateJobStagesStatus.objects.get(company_id=job_obj.company_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj,
                                                                    sequence_number=next_stage_sequance).stage
                if not current_stage==None:
                    if current_stage.name=='Interview' :
                        action_required='By Company/Agency'
                    elif current_stage.name=='Application Review' :
                        
                        action_required='By Company'
                    else:
                        action_required='By Candidate'
                if current_stage!='':
                    CompanyModels.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=getdata.internal_candidate_id.candidate_id,company_id=job_obj.company_id,defaults={
                                                            'current_stage':current_stage,'next_stage':next_stage,
                                                            'action_required':action_required,'update_at':datetime.datetime.now()})
                assign_job_internal = list(
                    CompanyModels.CompanyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
                                                    company_id=job_obj.company_id).values_list(
                        'recruiter_id', flat=True))
                assign_job_internal.append(job_obj.job_owner.id)
                assign_job_internal.append(job_obj.contact_name.id)
                assign_job_agency_internal=list(models.AssignJobInternal.objects.filter(job_id=job_obj).values_list(
                                    'internal_user_id__InternalUserid__id', flat=True))
                assign_job_internal.extend(assign_job_agency_internal)
                assign_job_internal = list(set(assign_job_internal))
                title = job_obj.job_title
                chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(id=request.user.id).id, title=title,candidate_id=User.objects.get(id=getdata.internal_candidate_id.candidate_id.id))
                print(assign_job_internal)
                ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=getdata.internal_candidate_id.candidate_id.id).id)
                for i in assign_job_internal:
                    ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
                ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
                candidate=User.objects.get(email=getdata.internal_candidate_id.email)
                job_assign_recruiter = CompanyModels.CompanyAssignJob.objects.filter(job_id=job_obj)
                agency_name=models.Agency.objects.get(user_id=request.user.id).agency_id.company_name
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                if not agency_name:
                    agency_name=request.user.first_name+' '+request.user.last_name
                description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
                to_email=[]
                to_email.append(job_obj.contact_name.email)
                to_email.append(job_obj.job_owner.email)
                if job_obj.contact_name.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
                if job_obj.job_owner.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        to_email.append(i.recruiter_id.email)
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
                description="Your profile has been succesfully submitted for the job"+job_obj.job_title+" by "+agency_name
                notify.send(request.user, recipient=User.objects.get(id=getdata.internal_candidate_id.candidate_id.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/candidate/Application_Submission.png",
                                                                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+'/agency')
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                stage_detail=''
                if not current_stage==None:
                    if current_stage.name=='Interview' :
                        stage_detail='Interview'
                        description="You have one application to review for the job "+job_obj.job_title
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                        description=description,image="/static/notifications/icon/company/Application_Review.png",
                                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                            job_obj.id))
                    elif current_stage.name=='Application Review':
                        stage_detail='Application Review'
                        description="You have one application to review for the job "+job_obj.job_title
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
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
            if getdata.job_type=='agency':
                job_obj=getdata.agency_job_id
                toemail=[getdata.internal_candidate_id.email]
                mail_subject = request.user.first_name+" "+request.user.last_name+" has Submitted your Application"
                html_content = render_to_string('company/email/job_assign_email.html', {'image':"https://bidcruit.com/static/assets/img/email/4.png",'email_data':"Your application has been submitted by "+request.user.first_name+" "+request.user.last_name+" to "+job_obj.job_title})
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=toemail)
                msg.attach_alternative(html_content, "text/html")
                # try:
                msg.send()
                models.AssociateCandidateInternal.objects.update_or_create(agency_id=job_obj.agency_id,job_id=job_obj,candidate_id=getdata.internal_candidate_id.candidate_id,
                    defaults={
                        'internal_candidate_id':models.InternalCandidateBasicDetail.objects.get(id=getdata.internal_candidate_id.id)
                    })
                models.AppliedCandidate.objects.update_or_create(agency_id=job_obj.agency_id,job_id=job_obj,candidate=User.objects.get(email=getdata.internal_candidate_id.email.lower()),
                        defaults={
                            'submit_type':'Agency'
                        })
                # models.AssociateJob.objects.update_or_create(agency_id=models.Agency.objects.get(user_id=request.user.id),
                #                                                             job_id=job_obj,
                #                                                             internal_candidate_id=models.InternalCandidateBasicDetail.objects.get(id=internal_candidate.id),
                #                                                             internal_user=models.InternalUserProfile.objects.get(InternalUserid=request.user.id),
                #                                                             defaults={'user_id' : User.objects.get(id=request.user.id)
                #                                                             })
                workflow = models.JobWorkflow.objects.get(job_id=job_obj)
                current_stage=None
                currentcompleted=False
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
                                models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                        job_id=job_obj, stage=stage_list_obj,
                                                                        sequence_number=stage.sequence_number, status=status,custom_stage_name='Application Review')
                                sequence_number = stage.sequence_number + 1
                                status = 0
                            else:
                                status = 0
                                sequence_number = stage.sequence_number + 1
                                next_stage = stage.stage
                            models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
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
                            else:
                                status = 0
                            models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
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
                                models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                        job_id=job_obj, stage=stage.stage,
                                                                        template=stage.template,
                                                                        sequence_number=sequence_number, status=status,custom_stage_name=stage.stage_name)

                                status = 1
                                sequence_number = stage.sequence_number + 1
                                stage_list_obj = CandidateModels.Stage_list.objects.get(name="Application Review")
                                current_stage = stage_list_obj
                                next_stage_sequance=stage.sequence_number+1
                                models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                        job_id=job_obj, stage=stage_list_obj,
                                                                        sequence_number=sequence_number, status=status,custom_stage_name='Application Review')
                            else:
                                status = 0
                                sequence_number = stage.sequence_number + 1
                                current_stage = stage_list_obj
                                models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                        candidate_id=getdata.internal_candidate_id.candidate_id,
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
                            else:
                                status = 0
                            models.CandidateJobStagesStatus.objects.create(agency_id=stage.agency_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj, stage=stage.stage,
                                                                    template=stage.template,
                                                                    sequence_number=stage.sequence_number, status=status,custom_stage_name=stage.stage_name)
                action_required=''
                
                if next_stage_sequance!=0:
                    if models.CandidateJobStagesStatus.objects.filter(agency_id=job_obj.agency_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj,
                                                                    sequence_number=next_stage_sequance).exists():
                        next_stage=models.CandidateJobStagesStatus.objects.get(agency_id=job_obj.agency_id,
                                                                    candidate_id=getdata.internal_candidate_id.candidate_id,
                                                                    job_id=job_obj,
                                                                    sequence_number=next_stage_sequance).stage
                if not current_stage==None:
                    if current_stage.name=='Interview' :
                        action_required='By Company/Agency'
                    elif current_stage.name=='Application Review' :
                        
                        action_required='By Company'
                    else:
                        action_required='By Candidate'
                if current_stage!='':
                    models.Tracker.objects.update_or_create(job_id=job_obj,candidate_id=getdata.internal_candidate_id.candidate_id,agency_id=job_obj.agency_id,defaults={
                                                            'current_stage':current_stage,'next_stage':next_stage,
                                                            'action_required':action_required,'update_at':datetime.datetime.now()})
                assign_job_internal = list(
                    models.AgencyAssignJob.objects.filter(job_id=job_obj, recruiter_type_internal=True,
                                                    agency_id=job_obj.agency_id).values_list(
                        'recruiter_id', flat=True))
                assign_job_internal.append(job_obj.job_owner.id)
                assign_job_internal.append(job_obj.contact_name.id)
                assign_job_internal = list(set(assign_job_internal))
                title = job_obj.job_title
                # chat = ChatModels.GroupChat.objects.create(job_id=job_obj, creator_id=User.objects.get(id=request.user.id).id, title=title,candidate_id=User.objects.get(id=internal_candidate.candidate_id.id))
                # print(assign_job_internal)
                # ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=internal_candidate.candidate_id.id).id)
                # for i in assign_job_internal:
                #     ChatModels.Member.objects.create(chat_id=chat.id, user_id=User.objects.get(id=i).id)
                # ChatModels.Message.objects.create(chat=chat,author=request.user,text='Create Group')
                candidate=User.objects.get(email=getdata.internal_candidate_id.email)
                job_assign_recruiter = models.AgencyAssignJob.objects.filter(job_id=job_obj)
                agency_name=models.Agency.objects.get(user_id=request.user.id).agency_id.company_name
                current_site = get_current_site(request)
                header=request.is_secure() and "https" or "http"
                if not agency_name:
                    agency_name=request.user.first_name+' '+request.user.last_name
                description = "New candidate "+candidate.first_name+" "+candidate.last_name+" has been submitted to Job "+job_obj.job_title+" By"+request.user.first_name+" "+request.user.last_name
                to_email=[]
                to_email.append(job_obj.contact_name.email)
                to_email.append(job_obj.job_owner.email)
                if job_obj.contact_name.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.contact_name.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
                if job_obj.job_owner.id != request.user.id:
                    notify.send(request.user, recipient=User.objects.get(id=job_obj.job_owner.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                for i in all_assign_users:
                    if i.recruiter_type_internal:
                        to_email.append(i.recruiter_id.email)
                        if i.recruiter_id.id != request.user.id:
                            notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/company/Candidate.png",
                                                                                target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                    job_obj.id))
                description="Your profile has been succesfully submitted for the job"+job_obj.job_title+" by "+agency_name
                notify.send(request.user, recipient=User.objects.get(id=getdata.internal_candidate_id.candidate_id.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                description=description,image="/static/notifications/icon/candidate/Application_Submission.png",
                                                                                target_url=header+"://"+current_site.domain+"/candidate/applied_job_detail/"+ str(job_obj.id)+"/agency")
                all_assign_users=job_assign_recruiter.filter(job_id=job_obj)
                stage_detail=''
                if not current_stage==None:
                    if current_stage.name=='Interview' :
                        stage_detail='Interview'
                        description="You have one application to review for the job "+job_obj.job_title
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
                                                                                        description=description,image="/static/notifications/icon/company/Application_Review.png",
                                                                                        target_url=header+"://"+current_site.domain+"/company/company_portal_candidate_tablist/"+str(candidate.id)+"/" + str(
                                                                                            job_obj.id))
                    elif current_stage.name=='Application Review':
                        stage_detail='Application Review'
                        description="You have one application to review for the job "+job_obj.job_title
                        for i in all_assign_users:
                            if i.recruiter_type_internal:
                                if i.recruiter_id.id != request.user.id:
                                    notify.send(request.user, recipient=User.objects.get(id=i.recruiter_id.id),verb="Candidate submission to job" + str(job_obj.id),
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
        return redirect('agency:daily_submission')

def internal_candidate_basic_detail(request,int_cand_detail_id=None):
    context={}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['source']=CandidateModels.Source.objects.all()
        context['notice_period']= CandidateModels.NoticePeriod.objects.all()
        context['countries']= CandidateModels.Country.objects.all()
        context['Add'] = False
        context['Edit'] = False
        context['View'] = True
        context['permission'] = check_permission(request)
        context['categories'] = models.CandidateCategories.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id))
        context['active_connections'] = models.CompanyAgencyConnection.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),is_accepted=True,is_rejected=False)#here will be filter query later
        if models.JobCreation.objects.filter(agency_id=models.Agency.objects.get(user_id=request.user.id),is_publish=True,close_job=False).exists():
            context['agency']=models.Agency.objects.get(user_id=request.user.id)
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
                if models.InternalCandidateBasicDetail.objects.filter(email=email).exists():
                    edit_internal_candidate=models.InternalCandidateBasicDetail.objects.get(email=email,agency_id=models.Agency.objects.get(user_id=request.user.id))
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

                models.InternalCandidateBasicDetail.objects.update_or_create(email=email,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                    'user_id' : User.objects.get(id=request.user.id),
                    'candidate_custom_id' : employee_id,
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
                add_skill=models.InternalCandidateBasicDetail.objects.get(email=email,agency_id = models.Agency.objects.get(user_id=request.user.id))
                for i in request.POST.getlist('source'):
                    if i.isnumeric():
                        main_source_obj = CandidateModels.Source.objects.get(id=i)
                        add_skill.source=main_source_obj
                    else:
                        source_cre=CandidateModels.Source.objects.create(name=i)
                        add_skill.source=source_cre
                for i in request.POST.getlist('tags'):
                    if i.isnumeric():
                        main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_skill.tags.add(main_skill_obj)
                    else:
                        tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                        main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                        add_skill.categories.add(main_categ_obj)
                if User.objects.filter(email=email.lower()).exists():
                    add_skill.candidate_id=User.objects.get(email=email.lower())
                add_skill.save()
                job_id=request.POST.get('job').split('-')
                jobid=job_id[1]
                jobtype=job_id[0]
                if jobtype=='company':
                    models.DailySubmission.objects.update_or_create(email=email,company_job_id=CompanyModels.JobCreation.objects.get(id=jobid),internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                        'job_type':'company',
                        'internal_user' : models.InternalUserProfile.objects.get(InternalUserid=User.objects.get(id=request.user.id)),
                        'candidate_custom_id' : employee_id,
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
                        'secure_resume':secure_resume,
                        'expectedctc' : expectedctc,
                        'total_exper' : total_exper,
                        'update_at':datetime.datetime.now()
                    })
                    add_deatil=models.DailySubmission.objects.get(email=email,company_job_id=CompanyModels.JobCreation.objects.get(id=jobid),internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id))
                    for i in request.POST.getlist('source'):
                        if i.isnumeric():
                            main_source_obj = CandidateModels.Source.objects.get(id=i)
                            add_deatil.source=main_source_obj
                        else:
                            source_cre=CandidateModels.Source.objects.create(name=i)
                            add_deatil.source=source_cre
                    for i in request.POST.getlist('tags'):
                        if i.isnumeric():
                            main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                            add_deatil.tags.add(main_skill_obj)
                        else:
                            tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                            main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                            add_deatil.categories.add(main_categ_obj)
                    add_deatil.save()
                    if secure_resume_get=="Secure-Resume":
                        return redirect("agency:internal_redact_resume",internal_candidate_id = add_deatil.id)
                    else:
                        mail_subject = '"Verify Detail" from Bidcruit'
                        current_site = get_current_site(request)
                        html_content = render_to_string('accounts/verify_detail.html', {'user': add_deatil,
                                                                                            'url':'verify_detail',
                                                                                            'email': email,
                                                                                            'domain': current_site.domain,
                                                                                            'uid': urlsafe_base64_encode(
                                                                                                force_bytes(add_deatil.pk))})
                        to_email = add_deatil.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                elif jobtype=='agency':
                    models.DailySubmission.objects.update_or_create(email=email,agency_job_id=models.JobCreation.objects.get(id=jobid),internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id),defaults={
                        'job_type':'AGENCY',
                        'internal_user' : models.InternalUserProfile.objects.get(InternalUserid=User.objects.get(id=request.user.id)),
                        'candidate_custom_id' : employee_id,
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
                        'secure_resume':secure_resume,
                        'expectedctc' : expectedctc,
                        'total_exper' : total_exper,
                        'update_at':datetime.datetime.now()
                    })
                    add_deatil=models.DailySubmission.objects.get(email=email,agency_job_id=models.JobCreation.objects.get(id=jobid),internal_candidate_id=add_skill,agency_id = models.Agency.objects.get(user_id=request.user.id))
                    for i in request.POST.getlist('source'):
                        if i.isnumeric():
                            main_source_obj = CandidateModels.Source.objects.get(id=i)
                            add_deatil.source=main_source_obj
                        else:
                            source_cre=CandidateModels.Source.objects.create(name=i)
                            add_deatil.source=source_cre
                    for i in request.POST.getlist('tags'):
                        if i.isnumeric():
                            main_skill_obj = models.Tags.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                            add_deatil.tags.add(main_skill_obj)
                        else:
                            tag_cre=models.Tags.objects.create(name=i,agency_id=models.Agency.objects.get(user_id=request.user.id),user_id=User.objects.get(id=request.user.id))
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
                            main_categ_obj = models.CandidateCategories.objects.get(id=i,agency_id=models.Agency.objects.get(user_id=request.user.id))
                            add_deatil.categories.add(main_categ_obj)
                    if verifydata:
                        add_deatil.verify=True
                        add_deatil.verified=True
                    add_deatil.save()
                    if secure_resume_get=="Secure-Resume":
                        return redirect("agency:internal_redact_resume",internal_candidate_id = add_deatil.id)
                    else:

                        mail_subject = '"Verify Detail" from Bidcruit'
                        current_site = get_current_site(request)
                        html_content = render_to_string('accounts/verify_detail.html', {'user': add_deatil,
                                                                                            'url':'verify_detail',
                                                                                            'email': email,
                                                                                            'domain': current_site.domain,
                                                                                            'uid': urlsafe_base64_encode(
                                                                                                force_bytes(add_deatil.pk))})
                        to_email = add_deatil.email
                        from_email = settings.EMAIL_HOST_USER
                        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                if secure_resume_get=="Secure-Resume":
                    return redirect("agency:internal_redact_resume",internal_candidate_id = add_deatil.id)
                else:
                    return redirect('agency:daily_submission')

            return render(request,'agency/ATS/internal_candidate_basic_form.html',context)
        else:
            return render(request, 'agency/ATS/not_permoission.html', context)
    else:
        return redirect('agency:agency_Profile')


def internal_redact_resume(request,internal_candidate_id):
    internal_candidate = get_object_or_404(models.DailySubmission,pk=internal_candidate_id)
    context = {}
    context['agencytype']= agencytype(models.Agency.objects.get(user_id=request.user.id))
    context['profile']=checkprofile(models.Agency.objects.get(user_id=request.user.id))
    if checkprofile(models.Agency.objects.get(user_id=request.user.id)):
        context['internal_candidate'] = internal_candidate
        return render(request,"agency/ATS/internal_redact_resume.html",context)
    else:
        return redirect('agency:agency_Profile')

def internal_save_redacted_resume(request,internal_candidate_id):
    daily_submit_candidate = get_object_or_404(models.DailySubmission,pk=internal_candidate_id)
    file_name = get_file_name(daily_submit_candidate.resume.url)
    data = json.loads(request.body.decode('UTF-8'))
    redacted_resume_blob = data['pdf_blob']
    media_path = 'media/'
    redacted_file_path = media_path+file_name
    redacted_resume = open(redacted_file_path,'wb+')
    redacted_resume.write(base64.b64decode(redacted_resume_blob))
    redacted_resume.close()
    daily_submit_candidate.secure_resume_file.name = redacted_file_path[len(media_path):]
    daily_submit_candidate.save()
    internal_candidate = get_object_or_404(models.InternalCandidateBasicDetail,pk=daily_submit_candidate.internal_candidate_id.id)
    file_name = get_file_name(internal_candidate.resume.url)
    data = json.loads(request.body.decode('UTF-8'))
    redacted_resume_blob = data['pdf_blob']
    media_path = 'media/'
    redacted_file_path = media_path+file_name
    redacted_resume = open(redacted_file_path,'wb+')
    redacted_resume.write(base64.b64decode(redacted_resume_blob))
    redacted_resume.close()
    internal_candidate.secure_resume_file.name = redacted_file_path[len(media_path):]
    internal_candidate.save()

    
    mail_subject = '"Verify Detail" from Bidcruit'
    current_site = get_current_site(request)
    html_content = render_to_string('accounts/verify_detail.html', {'user': daily_submit_candidate,
                                                                        'url':'verify_detail',
                                                                        'email': daily_submit_candidate.email,
                                                                        'domain': current_site.domain,
                                                                        'uid': urlsafe_base64_encode(
                                                                            force_bytes(daily_submit_candidate.pk))})
    to_email = daily_submit_candidate.email
    from_email = settings.EMAIL_HOST_USER
    msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    # file = open('myfile.dat', 'w+')
    return HttpResponse("done")


def get_job(request):
    companyid = request.POST.get("companyid")
    job_type = request.POST.get("job_type")
    candidateid = request.POST.get("candidateid")
    data=[]
    if job_type=='company':
        if candidateid!='':
            appliedjob=CompanyModels.AppliedCandidate.objects.filter(candidate=User.objects.get(id=candidateid)).values_list('job_id__id')
            jobs=CompanyModels.AssignExternal.objects.filter(~Q(job_id__in=appliedjob),company_id=CompanyModels.Company.objects.get(id=companyid),recruiter_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),is_accepted=True,is_rejected=False)
            for job in jobs:
                data.append({'id':'company-'+str(job.job_id.id),'title':job.job_id.job_title})
        else:
            jobs=CompanyModels.AssignExternal.objects.filter(company_id=CompanyModels.Company.objects.get(id=companyid),recruiter_id=models.Agency.objects.get(user_id=User.objects.get(id=request.user.id)),is_accepted=True,is_rejected=False)
            for job in jobs:
                data.append({'id':'company-'+str(job.job_id.id),'title':job.job_id.job_title})
    elif job_type=='agency':
        if candidateid!='':
            appliedjob=models.AppliedCandidate.objects.filter(candidate=User.objects.get(id=candidateid)).values_list('job_id__id')
            internaljobs=models.JobCreation.objects.filter(~Q(job_id__in=appliedjob),agency_id=models.Agency.objects.get(id=companyid),is_publish=True,close_job=False)
            for job in internaljobs:
                data.append({'id':'agency-'+str(job.id),'title':job.job_title})
        else:
            internaljobs=models.JobCreation.objects.filter(agency_id=models.Agency.objects.get(id=companyid),is_publish=True,close_job=False)
            for job in internaljobs:
                data.append({'id':'agency-'+str(job.id),'title':job.job_title})
        
    return JsonResponse({'data':data}, safe=False)