from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Chat(models.Model):
    name = models.TextField(max_length=50, null=True)
    is_group = models.BooleanField()
    members = models.ManyToManyField(User)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)
