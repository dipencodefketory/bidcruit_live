from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
import json
from channels.db import database_sync_to_async
from chat.models import GroupChat, Message,MessageModel,PrivateChat
import datetime

from accounts.models import User

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat = await self.get_chat()
        self.chat_room_id = f"chat_{self.chat_id}"
        self.group_name = "{}".format(self.user.id)

        if self.chat:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )


            await self.send({
                'type': 'websocket.accept'
            })
        else:
            await self.send({
                'type': 'websocket.close'
            })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()

    async def websocket_receive(self, event):
        text_data = event.get('text', None)
        bytes_data = event.get('bytes', None)

        if text_data:
            text_data_json = json.loads(text_data)
            text = text_data_json['text']

            await self.create_message(text)
            print('send message')
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': json.dumps({'type': "msg",'time':str(datetime.datetime.now().strftime("%H:%M %p")), 'sender': self.user.first_name, 'text': text}),
                    'sender_channel_name': self.channel_name
                }
            )

    async def chat_message(self, event):
        message = event['message']

        if self.channel_name != event['sender_channel_name']:
            await self.send({
                'type': 'websocket.send',
                'text': message
            })

    async def chat_activity(self, event):
        message = event['message']

        await self.send({
            'type': 'websocket.send',
            'text': message
        })

    @database_sync_to_async
    def get_chat(self):
        try:
            chat = GroupChat.objects.get(unique_code=self.chat_id)
            return chat
        except GroupChat.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, text):
        Message.objects.create(chat_id=self.chat.id, author_id=self.user.id, text=text)



class ChatPrivate(AsyncConsumer):
    async def websocket_connect(self, event):
        self.user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat = await self.get_chat()
        self.chat_room_id = f"chat_{self.chat_id}"

        if self.chat:
            await self.channel_layer.group_add(
                self.chat_room_id,
                self.channel_name
            )

            await self.send({
                'type': 'websocket.accept'
            })
        else:
            await self.send({
                'type': 'websocket.close'
            })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.chat_room_id,
            self.channel_name
        )
        raise StopConsumer()

    async def websocket_receive(self, event):
        text_data = event.get('text', None)
        bytes_data = event.get('bytes', None)

        if text_data:
            text_data_json = json.loads(text_data)
            text = text_data_json['text']
            print('=================', text)

            await self.create_message(text)

            await self.channel_layer.group_send(
                self.chat_room_id,
                {
                    'type': 'chat_message',
                    'message': json.dumps({'type': "msg", 'time': str(datetime.datetime.now().strftime("%H:%M %p")),
                                           'sender': self.user.first_name, 'text': text}),
                    'sender_channel_name': self.channel_name
                }
            )

    async def chat_message(self, event):
        message = event['message']

        if self.channel_name != event['sender_channel_name']:
            await self.send({
                'type': 'websocket.send',
                'text': message
            })

    async def chat_activity(self, event):
        message = event['message']

        await self.send({
            'type': 'websocket.send',
            'text': message
        })

    @database_sync_to_async
    def get_chat(self):
        try:
            chat = PrivateChat.objects.get(unique_code=self.chat_id)
            return chat
        except PrivateChat.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, text):
        MessageModel.objects.create(chat_id=self.chat.id, author_id=self.user.id, body=text)


from channels.generic.websocket import AsyncWebsocketConsumer
class Chat_chat(AsyncConsumer):
    async def websocket_connect(self, event):
        self.user = self.scope["session"]["_auth_user_id"]
        # self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat=''
        # self.chat = await self.get_chat()
        # self.chat_room_id = f"chat_{self.chat_id}"
        self.group_name = "{}".format(self.user)

        if self.group_name:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.send({
                'type': 'websocket.accept'
            })
        else:
            await self.send({
                'type': 'websocket.close'
            })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()

    async def websocket_receive(self, event):
        text_data = event.get('text', None)
        text_data_json = json.loads(text_data)
        chat_type = text_data_json.get('chat_type', None)
        chat_id = text_data_json.get('chat_id', None)
        text = text_data_json.get('text', None)

        print("============",chat_type,"==============",chat_id,"=========",text)
        if text_data:
            text = text_data_json['text']
            if chat_type=='group':
                self.chat = await self.group_chat(chat_id=chat_id)
                await self.group_message(text)
            if chat_type=='private':
                self.chat = await self.private_chat(chat_id=chat_id)
                await self.private_message(text)
        # return 'send message'
        #     await self.channel_layer.group_send(
        #         self.group_name,
        #         {
        #             'type': 'chat_message',
        #             'message': json.dumps({'type': "msg",'time':str(datetime.datetime.now().strftime("%H:%M %p")), 'sender': self.user.id, 'text': text}),
        #             'sender_channel_name': self.channel_name
        #         }
        #     )

    async def chat_message(self, event):
        message = event['message']

        if self.channel_name != event['sender_channel_name']:
            await self.send({
                'type': 'websocket.send',
                'text': message
            })

    async def chat_activity(self, event):
        message = event['message']

        await self.send({
            'type': 'websocket.send',
            'text': message
        })

    @database_sync_to_async
    def group_chat(self,chat_id):
        try:
            chat = GroupChat.objects.get(unique_code=chat_id)
            return chat
        except GroupChat.DoesNotExist:
            return None

    @database_sync_to_async
    def group_message(self, text):
        Message.objects.create(chat_id=self.chat.id, author_id=self.user, text=text)

    @database_sync_to_async
    def private_chat(self,chat_id):
        try:
            chat = PrivateChat.objects.get(unique_code=chat_id)
            return chat
        except PrivateChat.DoesNotExist:
            return None

    @database_sync_to_async
    def private_message(self, text):
        MessageModel.objects.create(chat_id=self.chat.id, author_id=self.user, body=text)

    async def recieve_group_message(self, event):
        message = event['message']
        print("self",event)
        # Send message to WebSocket
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(event),

        })