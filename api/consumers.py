import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Chat, Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):

        self.user = self.scope["user"]

        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f"chat_{self.chat_id}"
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        self.accept()

    def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message")

        # Saving Message in DB
        if message_text:
            chat = Chat.objects.get(id=self.chat_id)

            message_obj = Message.objects.create(
                chat=chat,
                sender=self.user,
                content=message_text,
            )

        # Broadcasting Message to all users in this group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender": self.user.id,
                "timestamp": str(message_obj.timestamp),
            },
        )

    def chat_message(self, event):
        self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name,
        )
