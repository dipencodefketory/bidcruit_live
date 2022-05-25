from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from company.models import InterviewSchedule,CandidateJobStagesStatus,InterviewTemplate

groups ={}
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = str(self.scope['url_route']['kwargs']['link'])
        print("self scope",self.scope)
        if str(self.scope['url_route']['kwargs']['link']) not in groups:
            groups[str(self.scope['url_route']['kwargs']['link'])] = []

        print("self.scope",self.scope)
        print("connect was called")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
            )

        await self.accept()

    async def disconnect(self,close_code):
        print("disconnected",self.room_group_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # print("disconnected")

    # async def websocket_disconnect(self, event):
    #     print("disconnected")
    #     await self.channel_layer.group_discard(
    #         self.chat_room_id,
    #         self.channel_name
    #     )
    #     raise StopConsumer()


    async def receive(self,text_data):
        receive_dict = json.loads(text_data)
        print("\n\n\n\n\n\nreceive was called")
        print("received message",receive_dict)
        message = receive_dict['message']

        action = receive_dict['action']

        if (action == 'new-offer') or (action == 'new-answer'):
            print("NEW OFFFFFFFERRRRRRRRRRR OR ANSSSWEEEEEER")
            receiver_channel_name = receive_dict['message']['receiver_channel_name']
            print("receiver channel name",receiver_channel_name)
            receive_dict['message']['receiver_channel_name'] = self.channel_name
            
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type":"send.sdp",
                    "receive_dict":receive_dict
                }
            )
            print("\n\n\n\n\n\n\n\n\n\n\n\n just before return statemetn\n\n\n\n\n\n\n\n\n\n")
            return
        elif(action == 'end-meeting'):
            print('\n\n end-meeting',receive_dict)
            # receiver_channel_name = receive_dict['message']['receiver_channel_name']
            # print("receiver channel name", receiver_channel_name)
            # receive_dict['message']['receiver_channel_name'] = self.channel_name
            receive_dict['end-meeting'] = True
            await sync_to_async(end_interview, thread_sensitive=True)(receive_dict['link'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send.sdp",
                    "receive_dict": receive_dict
                }
            )
            return

        receive_dict['message']['receiver_channel_name'] = self.channel_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":"send.sdp",
                "receive_dict":receive_dict
            }
        )

    async def send_sdp(self,event):
        print("send sdp was called")

        print("event" ,event)
        receive_dict = event['receive_dict']

        print("message calledededede")
        await self.send(text_data=json.dumps(receive_dict))


def end_interview(link):
    interview_obj = InterviewSchedule.objects.get(interview_link=link)
    interview_obj.is_completed = True
    interview_obj.save()
    interview_obj.job_stages_id.status = 2
    interview_obj.job_stages_id.save()
