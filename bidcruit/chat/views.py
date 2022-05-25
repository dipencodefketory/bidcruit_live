from django.shortcuts import render, HttpResponse, redirect
from . import models
import json
from django.core import serializers
from agency import models as AgencyModels
from agency.views import checkprofile,agencytype
def get_message(request):
    data={}
    if request.method=='POST':
        groupid = request.POST.get("chat_id")
        get_type=request.POST.get('type')
        print(get_type)
        if get_type=='group':
            models.Message.objects.filter(chat=models.GroupChat.objects.get(unique_code=groupid)).update(read=True)
            data['message'] = serializers.serialize("json", models.Message.objects.filter(chat=models.GroupChat.objects.get(unique_code=groupid)))
            group_title= models.GroupChat.objects.get(unique_code=groupid)
            data['Group_title'] = group_title.title
            data['status']=True
            data['chat_id']=group_title.unique_code
            print(data['message'])
            return HttpResponse(json.dumps(data))
        elif get_type=='private':
            data['message'] = serializers.serialize("json", models.MessageModel.objects.filter(chat=models.PrivateChat.objects.get(unique_code=groupid)))
            group_title = models.MessageModel.objects.filter(chat=models.PrivateChat.objects.get(unique_code=groupid)).last()
            chat = models.PrivateChat.objects.get(unique_code=groupid)
            if chat.user1==request.user:
                data['Group_title'] =chat.user2.first_name
                data['userid'] = chat.user2.id
            if chat.user2==request.user:
                data['Group_title'] =chat.user1.first_name
                data['userid'] = chat.user1.id
            data['status'] = True
            data['chat_id'] = group_title.chat.unique_code
            return HttpResponse(json.dumps(data))
        else:
            data['status'] = False
            HttpResponse(json.dumps(data))
    else:
        data['status'] = False
        return HttpResponse(json.dumps(data))




def chatlist(request,uniqueid=None):
    context={}
    if request.user.is_candidate:
        context['base']="candidate/base.html"
    if request.user.is_company:
        context['base']='company/base.html'
    if request.user.is_agency:
        context['base']='agency/base.html'
        context['profile']=checkprofile(AgencyModels.Agency.objects.get(user_id=request.user.id))
        context['agencytype']= agencytype(AgencyModels.Agency.objects.get(user_id=request.user.id))
        if checkprofile(AgencyModels.Agency.objects.get(user_id=request.user.id)):
            pass
        else:
            return redirect('agency:agency_Profile') 
    if uniqueid:
        context['privatesinglechat']=models.PrivateChat.objects.get(unique_code=uniqueid)
    private_chat=models.PrivateChat.objects.filter(Q(user1=User.objects.get(id=request.user.id)) | Q(user2=request.user.id)).values_list('id')
    private_msg = models.MessageModel.objects.filter(chat__in=private_chat).order_by('chat','-date_created').distinct('chat')
    context['private_chat'] = models.MessageModel.objects.filter(id__in=private_msg).order_by('-date_created')
    group_chat_list = models.Member.objects.filter(user=request.user.id).values_list('chat')
    messags=models.Message.objects.filter(chat__in=group_chat_list).order_by('chat','-date_created').distinct('chat')
    messags = models.Message.objects.filter(id__in=messags).order_by('-date_created')
    context['group_chat']=messags
    return render(request,'chat/chat.html',context)


from datetime import datetime
from django import http
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import get_user_model
User = get_user_model()
from candidate.models import CandidateProfile
from company.models import CompanyProfile


def get_unread_messages(request):
    users = User.objects.all()
    print('\n\n\nget_unread_messages',users)
    # messages = MessageModel.objects.filter(recipient=request.user.id)
    # unread_message_no_list = []
    unread_message_no_list = {}
    for i in users:
        messages = models.MessageModel.objects.filter(user=i, recipient=request.user)
        count = 0
        for j in messages:
            if j.message_read == False:
                count += 1

        # unread_message_no_list.append({i.id:count})
        unread_message_no_list[i.id] = count
    print(unread_message_no_list)

    return HttpResponse(json.dumps(unread_message_no_list))


def update_unread_messages(request, id):
    print("IIIIDDDD", id)
    print(request.user)
    print(User.objects.get(id=id))
    messages = models.MessageModel.objects.filter(user=User.objects.get(id=id), recipient=request.user,request_status=1)
    print(messages)
    for m in messages:
        m.message_read = True
        m.save()

    return HttpResponse("done")


def get_user_image(request,email):
    print('\n\n\nemail >>>>>>>>>>>>',email)
    user = User.objects.get(email=email)
    if user.is_candidate:
        profiles = CandidateProfile.objects.filter(candidate_id=user.id)
        for i in profiles:
            if i.profile_id.active:
                return HttpResponse(i.user_image.url)
        return HttpResponse("/media/difference.jpg")
    else:

        company_profile = CompanyProfile.objects.filter(company_id=user.id)
        if company_profile.exists():
            print(CompanyProfile.objects.get(company_id=user.id).company_logo.url)
            return HttpResponse(CompanyProfile.objects.get(company_id=user.id).company_logo.url)
        else:
            return HttpResponse("/media/difference.jpg")
        # return HttpResponse(CompanyProfile.objects.get(company_id=user.id).company_logo.url)

from django.db.models import Q
def create_privatemsg(request,type_chat,id):
    
    if not models.PrivateChat.objects.filter(Q(user1=User.objects.get(id=id)) & Q(user2=request.user)|Q(user1=request.user) & Q(user2=User.objects.get(id=id))).exists():
        chat = models.PrivateChat.objects.create(creator_id=request.user.id, user1=request.user,user2=User.objects.get(id=id))
        models.MessageModel.objects.create(chat=chat, author=request.user,body="New Message")
        if type_chat=="company":
            return redirect("company:chat",chat.unique_code)
        if type_chat=="agency":
            return redirect("agency:chat",chat.unique_code)
    else:
        chat = models.PrivateChat.objects.create(creator_id=request.user.id, user1=request.user,user2=User.objects.get(id=id))
        if type_chat=="company":
            return redirect("company:chat",chat.unique_code)
        if type_chat=="agency":
            return redirect("agency:chat",chat.unique_code)



import math
from django.utils import timezone
def get_chat(request):
    private_chat=models.PrivateChat.objects.filter(Q(user1=User.objects.get(id=request.user.id)) | Q(user2=request.user.id)).values_list('id')
    private_msg = models.MessageModel.objects.filter(chat__in=private_chat).order_by('chat','-date_created').distinct('chat')
    private_chat = models.MessageModel.objects.filter(id__in=private_msg,message_read=False).order_by('-date_created')
    chat=[]
    for i in private_chat:
        message_date=''
        if i.date_created:
            now = timezone.now()
            diff = now - i.date_created
            if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
                seconds = diff.seconds
                if seconds == 1:
                    message_date = str(seconds) + "second ago"
                else:
                    message_date = str(seconds) + " seconds ago"
            if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
                minutes = math.floor(diff.seconds / 60)
                if minutes == 1:
                    message_date = str(minutes) + " minute ago"
                else:
                    message_date = str(minutes) + " minutes ago"
            if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
                hours = math.floor(diff.seconds / 3600)
                if hours == 1:
                    message_date = str(hours) + " hour ago"
                else:
                    message_date = str(hours) + " hours ago"
            # 1 day to 30 days
            if diff.days >= 1 and diff.days < 30:
                days = diff.days
                if days == 1:
                    message_date = str(days) + " day ago"
                else:
                    message_date = str(days) + " days ago"
            if diff.days >= 30 and diff.days < 365:
                months = math.floor(diff.days / 30)
                if months == 1:
                    message_date = str(months) + " month ago"
                else:
                    message_date = str(months) + " months ago"
            if diff.days >= 365:
                years = math.floor(diff.days / 365)
                if years == 1:
                    message_date = str(years) + " year ago"
                else:
                    message_date = str(years) + " years ago"
        else:
            message_date = ''
        chat.append({'message':i.body,'group-name':'','author' : i.author.first_name,'date':message_date})

    group_chat_list = models.Member.objects.filter(user=request.user.id).values_list('chat')
    messags=models.Message.objects.filter(chat__in=group_chat_list).order_by('chat','-date_created').distinct('chat')
    messags = models.Message.objects.filter(id__in=messags).order_by('-date_created')
    # context['group_chat']=messags
    for i in messags:
        message_date = ''
        if i.date_created:
            now = timezone.now()
            diff = now - i.date_created
            if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
                seconds = diff.seconds
                if seconds == 1:
                    message_date = str(seconds) + "second ago"
                else:
                    message_date = str(seconds) + " seconds ago"
            if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
                minutes = math.floor(diff.seconds / 60)
                if minutes == 1:
                    message_date = str(minutes) + " minute ago"
                else:
                    message_date = str(minutes) + " minutes ago"
            if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
                hours = math.floor(diff.seconds / 3600)
                if hours == 1:
                    message_date = str(hours) + " hour ago"
                else:
                    message_date = str(hours) + " hours ago"
            # 1 day to 30 days
            if diff.days >= 1 and diff.days < 30:
                days = diff.days
                if days == 1:
                    message_date = str(days) + " day ago"
                else:
                    message_date = str(days) + " days ago"
            if diff.days >= 30 and diff.days < 365:
                months = math.floor(diff.days / 30)
                if months == 1:
                    message_date = str(months) + " month ago"
                else:
                    message_date = str(months) + " months ago"
            if diff.days >= 365:
                years = math.floor(diff.days / 365)
                if years == 1:
                    message_date = str(years) + " year ago"
                else:
                    message_date = str(years) + " years ago"
        else:
            message_date = ''
        chat.append({'message': i.text,'group-name':i.chat.title, 'author': i.author.first_name, 'date': message_date})
    return JsonResponse({
        "message": chat,

    }, status=201)


