from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]


class ChatSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "name", "members", "is_group"]

    def get_name(self, obj):
        if obj.name and obj.is_group:
            return obj.name

        elif obj.is_group:
            members = obj.members.all()
            return ", ".join([m.username for m in members])
        else:
            other_user = obj.members.exclude(id=self.context["request"].user.id).first()
            return other_user.username if other_user else "Me"


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "timestamp"]
