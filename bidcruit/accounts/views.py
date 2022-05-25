from django.contrib.auth.forms import PasswordResetForm
from bidcruit import settings
import re
import json
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import datetime
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from . import models
import pyotp
from .tokens import account_activation_token
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
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

from django.core.files import File
from candidate import models as candidate_model
from company import models as CompanyModels
from django.contrib import messages
User = get_user_model()
from smtplib import SMTPException
from notifications.models import Notification
def bidcruit_home(request):
    if request.user.is_authenticated:
        if request.user.is_candidate:
            return redirect('candidate:home')
        elif request.user.is_company:
            return redirect('company:dashbord')
        elif request.user.is_agency:
            return redirect('agency:agency_Profile')
    return render(request, 'accounts/home.html')
def candidate_home(request):
    if request.user.is_authenticated:
        if request.user.is_candidate:
            return redirect('candidate:home')
        elif request.user.is_company:
            return redirect('company:dashbord')
        elif request.user.is_agency:
            return redirect('agency:agency_Profile')
    return render(request, 'accounts/candidate.html')
def recruiters_home(request):
    if request.user.is_authenticated:
        if request.user.is_candidate:
            return redirect('candidate:home')
        elif request.user.is_company:
            return redirect('company:dashbord')
        elif request.user.is_agency:
            return redirect('agency:agency_Profile')
    return render(request, 'accounts/recruiters.html')

def company_home(request):
    if request.user.is_authenticated:
        if request.user.is_candidate:
            return redirect('candidate:home')
        elif request.user.is_company:
            return redirect('company:dashbord')
        elif request.user.is_agency:
            return redirect('agency:agency_Profile')
    return render(request, 'accounts/company.html')

def interviewer_home(request):
    if request.user.is_authenticated:
        if request.user.is_candidate:
            return redirect('candidate:home')
        elif request.user.is_company:
            return redirect('company:dashbord')
        elif request.user.is_agency:
            return redirect('agency:agency_Profile')
    return render(request, 'accounts/interviewer.html')
def agency_home(request):
    if request.user.is_authenticated:
        if request.user.is_candidate:
            return redirect('candidate:home')
        elif request.user.is_company:
            return redirect('company:dashbord')
        elif request.user.is_agency:
            return redirect('agency:agency_Profile')
    return render(request, 'accounts/recruitment-agency.html')
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
        user_id = User.objects.get(email=email)
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
            if request.user_agent.is_mobile:
                device_type = "Mobile"
            if request.user_agent.is_tablet:
                device_type = "Tablet"
            if request.user_agent.is_pc:
                device_type = "PC"
            browser_type = request.user_agent.browser.family
            os_type = request.user_agent.os.family
            user = User.objects.get(email=email)
            login(request, user)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            chk_register_detail = models.User.objects.get(email=request.user.email)
            if ip != chk_register_detail.ip:
                mail_subject = 'Security Alert'
                html_content = render_to_string('accounts/login_change_ip_email.html', {'user': user,'ip': ip,'device':device_type,'browser':browser_type,'os':os_type })
                to_email = request.user.email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            if request.user.is_candidate:
                if 'view_job' in request.session:
                    return redirect('candidate:job_view')
                else:
                    return redirect('candidate:home')
            elif request.user.is_company:
                return redirect('company:dashbord')
            elif request.user.is_agency:
                return redirect('agency:agency_Profile')
            # otp = generateOTP(request)
            # models.LoginDetail.objects.create(user_id=User.objects.get(email=email), otp=otp, ip=ip,
            #                                   device_type=device_type, browser_type=browser_type,
            #                                   browser_version=browser_version, os_type=os_type,
            #                                   os_version=os_version)
            # mail_subject = 'OTP'
            # html_content = render_to_string('accounts/acc_otp_email.html', {'user': user,
            #                                                                 'otp': otp})
            # to_email = email
            # from_email = settings.EMAIL_HOST_USER
            # msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
            # msg.attach_alternative(html_content, "text/html")
            # try:
            #     msg.send()
            # except BadHeaderError:
            #     messages.error(request, 'Invalid header found.')
            #     return render(request, 'accounts/signinpassword.html')
            # except SMTPException as e:
            #     messages.error(request,  e)
            #     return render(request, 'accounts/signinpassword.html')
            # except:
            #     messages.error(request, 'Mail sending failed, Please check your internet connection !!')
            #     return render(request, 'accounts/signinpassword.html')
            # return redirect('accounts:verify_otp')
        elif user is None:
            if user_id is not None and user_id.check_password(password):
                messages.error(request, 'Please verify your email account. A link has been sent to '+email)
            else:
                messages.error(request, 'Invalid login details given')
            return render(request, 'accounts/signinpassword.html')
        else:
            return HttpResponse('Something Went Wrong')
    else:
        return render(request, 'accounts/signinpassword.html')


def user_login_email(request):
    getviewjoburl=request.META.get('HTTP_REFERER')
    if not getviewjoburl==None:
        get_job=getviewjoburl.split('/')
        if 'view_job' in get_job:
            print('======================')
            request.session['view_job'] = get_job[-1]
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['email'] = email
        # request.session['email'] = email
        return redirect('accounts:user_login_password')
    return render(request, 'accounts/signin.html')


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
    models.LoginDetail.objects.create(user_id=User.objects.get(id=request.session['user_id']), otp=otp, ip=ip,
                                      device_type=device_type, browser_type=browser_type,
                                      browser_version=browser_version, os_type=os_type,
                                      os_version=os_version)
    try:
        mail_subject = 'OTP.'
        html_content = render_to_string('accounts/acc_otp_email.html', {'user': user,
                                                                        'otp': otp})
        to_email = user.email
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except BadHeaderError:
        print("email not send")
    return render(request, 'accounts/signinotp.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        login_otp = models.LoginDetail.objects.filter(user_id=request.session['user_id']).order_by(
            '-create_at').first()
        if login_otp.otp == otp:
            if request.user_agent.is_mobile:
                device_type = "Mobile"
            if request.user_agent.is_tablet:
                device_type = "Tablet"
            if request.user_agent.is_pc:
                device_type = "PC"
            browser_type = request.user_agent.browser.family
            os_type = request.user_agent.os.family
            user = User.objects.get(id=login_otp.user_id.id)
            login(request, user)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            chk_register_detail = models.User.objects.get(email=request.user.email)
            if ip != chk_register_detail.ip:
                mail_subject = 'Security Alert'
                html_content = render_to_string('accounts/login_change_ip_email.html', {'user': user,'ip': ip,'device':device_type,'browser':browser_type,'os':os_type })
                to_email = request.user.email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            if request.user.is_candidate:
                if 'view_job' in request.session:
                    return redirect('candidate:job_view')
                else:
                    return redirect('candidate:home')
            elif request.user.is_company:
                return redirect('company:dashbord')
            elif request.user.is_agency:
                return redirect('agency:agency_Profile')
        else:
            messages.error(request, 'Invalid OTP.')
            return render(request, 'accounts/signinotp.html')
    return render(request, 'accounts/signinotp.html')




def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        if user.is_candidate:
            candidate_model.CandidateSEO.objects.create(candidate_id=User.objects.get(id=user.id))
        return redirect('accounts:signin')
    else:
        return HttpResponse('Activation link is invalid!')



def activate_account_confirmation(request,name,email):
    context={'email':email,'name':name}
    return render(request, 'accounts/activate_account_confirmation.html',context)
    

@login_required(login_url="/")
def user_logout(request):
    logout(request)
    return redirect('bidcruit_home')


def handler404(request, *args, **argv):
    response = render(request, 'accounts/404.html')
    response.status_code = 404
    return response
def handler500(request, *args, **argv):
    response = render(request, 'accounts/500.html')
    response.status_code = 500
    return response

def back_to_home(request):
    print("back to home was called")
    if request.user.is_authenticated:
        if request.user.is_company:
            print("user is from company")
            return redirect('company:home')
        elif request.user.is_candidate:
            print("user is from candidate group")
            return redirect('candidate:home')
    else:
        print("no user is logged in")
        return redirect('bidcruit_home')



# ATS
def apply_job_cadidate_sendotp(request):
    data = {}
    if not request.user.is_authenticated:
        if request.method == 'POST':
            email = request.POST.get('email')
            if User.objects.filter(email=request.POST['email']).exists():
                data['message'] = "email already exists"
            else:
                otp = generateOTP(request)
                models.VerifyCandidateEmail.objects.update_or_create(email=email,defaults={'otp': otp})

                mail_subject = 'Varification Otp Send.'
                html_content = render_to_string('accounts/send_varification_otp.html', {'email': email,'otp':otp})
                to_email = email
                from_email = settings.EMAIL_HOST_USER
                msg = EmailMultiAlternatives(mail_subject, mail_subject, from_email, to=[to_email])
                msg.attach_alternative(html_content, "text/html")
                try:
                    data['status'] = True
                    msg.send()
                    return HttpResponse(json.dumps(data))
                except BadHeaderError:
                    data['status'] = False
                    data['message'] = 'Invalid header found.'
                except SMTPException as e:
                    data['status'] = False
                    data['message'] = e
                except:
                    data['status'] = False
                    data['message'] = 'Mail sending failed, Please check your internet connection !!'
                return HttpResponse(json.dumps(data))
            return HttpResponse(json.dumps(data))
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps(data))


def job_apply_verify_otp(request):
    data = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        get_verify_otp = models.VerifyCandidateEmail.objects.get(email=email)
        print(otp)
        print(email)
        print(get_verify_otp.otp)

        if str(get_verify_otp.otp) == str(otp):
            data['status'] = True
            data['message'] ='Verify OTP.'
        else:
            data['status'] = False
            data['message'] ='Invalid OTP.'
    return HttpResponse(json.dumps(data))



def read_message(request,notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.unread = False
    notification.save()
    print(notification.data['target_url'])
    return redirect(notification.data['target_url'])