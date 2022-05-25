from django.db import models
from accounts.models import User

from datetime import datetime
import random
from company.models import JobCreation
from django.utils import timezone
class Messages(models.Model):
    description = models.TextField()
    sender_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    time = models.TimeField(auto_now_add=True,null=True)
    seen = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"To: {self.receiver_name} From: {self.sender_name}"

    class Meta:
        ordering = ('timestamp',)


class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.IntegerField()

    def __str__(self):
        return f"{self.friend}"





def UniqueGenerator(length=10):
    source = "abcdefghijklmnopqrztuvwxyz"
    result = ""
    for _ in range(length):
        result += source[random.randint(0, length)]
    return result

# Create your models here.
class GroupChat(models.Model):
    job_id=models.ForeignKey(JobCreation,related_name="job_GroupChat",on_delete=models.CASCADE)
    creator = models.ForeignKey(User, related_name="creator_GroupChat",on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    unique_code = models.CharField(max_length=10, default=UniqueGenerator)
    date_created = models.DateTimeField(default=datetime.now)
    candidate_id=models.ForeignKey(User,related_name="Chatgroup_candidate",on_delete=models.CASCADE)

class Member(models.Model):
    chat = models.ForeignKey(GroupChat, related_name="Member_GroupChat",on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_GroupChat", on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=datetime.now)

class Message(models.Model):
    read=models.BooleanField(default=False)
    chat = models.ForeignKey(GroupChat,related_name="Message_GroupChat", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="author_GroupChat", on_delete=models.CASCADE)
    text = models.TextField(default="")
    date_created = models.DateTimeField(default=datetime.now)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            'type': 'recieve_group_message',
            'chat_type':'group',
            'sender_name':self.author.first_name+' '+self.author.last_name,
            'time': str(datetime.utcnow()),
            'message': '{}'.format(self.text),
            "unique_code": self.chat.unique_code
        }
        member=Member.objects.filter(chat=self.chat)
        channel_layer = get_channel_layer()
        print("a======================",channel_layer)
        for i in member:
            if not i.user==self.author:
                async_to_sync(channel_layer.group_send)("{}".format(i.user.id), notification)
        # print("user.id {}".format(self.user.id))
        # print("user.id {}".format(self.recipient.id))

        # async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
        # async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.text = self.text.strip()  # Trimming whitespaces from the body
        super(Message, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()






from django.contrib.auth import get_user_model
from django.db.models import (Model, TextField, IntegerField, BooleanField, DateTimeField, ForeignKey,
                              CASCADE, TextField,ManyToManyField)

from asgiref.sync import async_to_sync
# from bidcruit.accounts import models
from channels.layers import get_channel_layer
User = get_user_model()


class PrivateChat(models.Model):
    creator = models.ForeignKey(User, related_name="creator_PrivateChat",on_delete=models.CASCADE)
    unique_code = models.CharField(max_length=10, default=UniqueGenerator)
    user1 = ForeignKey(User, on_delete=CASCADE, verbose_name='user',
                      related_name='from_user', db_index=True)
    user2 = ForeignKey(User, on_delete=CASCADE, verbose_name='recipient',
                           related_name='to_user', db_index=True)
    date_created = models.DateTimeField(default=datetime.now)


class MessageModel(Model):
    chat = models.ForeignKey(PrivateChat, related_name="Message_MessageModel", on_delete=models.CASCADE)
    timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
                              db_index=True)
    body = TextField('body')
    author = models.ForeignKey(User, related_name="author_MessageModel", on_delete=models.CASCADE)
    message_read = BooleanField(default=False)
    request_status = IntegerField(null=True, default=0)
    date_created = models.DateTimeField(default=datetime.now)

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            'type': 'recieve_group_message',
            'chat_type': 'private',
            'sender_name': self.author.first_name + ' ' + self.author.last_name,
            'time': str(datetime.utcnow()),
            'message': '{}'.format(self.body),
            "unique_code": self.chat.unique_code
        }

        channel_layer = get_channel_layer()
        member = PrivateChat.objects.get(id=self.chat.id)
        if member.user1==self.author:
            print('444444444444444444444444444444444444',member.user1.id,"=========",self.author.id)
            async_to_sync(channel_layer.group_send)("{}".format(member.user2.id), notification)
        if member.user2==self.author:
            print('5555555555555555555555555555555555555555', member.user2.id, "=========", self.author.id)
            async_to_sync(channel_layer.group_send)("{}".format(member.user1.id), notification)

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()

