from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from chat.models import MessageModel
from rest_framework.serializers import ModelSerializer, CharField
User = get_user_model()


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.email', read_only=True)
    recipient = CharField(source='recipient.email')

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, email=validated_data['recipient']['email'])
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body','message_read')


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email','id','first_name','last_name','company_name','is_candidate','is_company')

