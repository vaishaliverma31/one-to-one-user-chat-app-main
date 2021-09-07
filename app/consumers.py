from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from asgiref.sync import async_to_sync
import json
from .models import User
from .models import Thread, Message
from channels.auth import login

class chatroom(WebsocketConsumer,AsyncConsumer, Thread):
    from channels.db import database_sync_to_async
    def connect(self):
            self.room_name = self.scope['url_route']['kwargs']['username']
            other_username=self.scope['url_route']['kwargs']['username']
            self.room_group_name = 'room_%s' % self.room_name
            me = self.scope['user']

            other_user=User.objects.get(username=other_username)
            self.thread_obj=Thread.objects.get_or_create_personal_thread(me, other_user)
            self.room_name=f'personal_thread_{self.thread_obj.id}'
            self.update_user_status(me, 'online')
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        self.update_user_status(user, 'offline')

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        print(text_data)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type':'chat_message',
                'message': text_data,
            }
        )

    def chat_message(self, event):
        message = event['message']
        data = json.loads(message)
        user=self.scope['user']
        id=User.objects.get(username=user)
        id1=id.id
        self.store_message(data['message'])
        self.send(text_data=json.dumps({
            'message': data['message'],
            'image':data['image'],
            'video':data['video'],
            'id':id1

        }))
    def update_user_status(self, user, status):
        return User.objects.filter(pk=user.pk).update(status=status)

    def store_message(self, text):
        Message.objects.create(
            thread=self.thread_obj,
            sender=self.scope['user'],
            text=text
        )

