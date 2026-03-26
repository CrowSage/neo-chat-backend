from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Chat, Message
from .serializers import UserSerializer, ChatSerializer, MessageSerializer


# Registration View
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email", "")
    password = request.data.get("password")

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken!"}, status=400)

    User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "Account Created Successfully!"}, status=200)


# Return all chats the logged-in user is a memeber of
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chats(request):
    chats = Chat.objects.filter(members=request.user).distinct()

    if chats.exists():
        serializer = ChatSerializer(chats, many=True, context={"request": request})
        return Response(serializer.data)

    return Response([])


# Create a DM between logged-in user and another user
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_dm(request):

    user = request.user
    username = request.data.get("other_user")

    other_user = User.objects.filter(username=username).first()

    if not other_user:
        return Response({"message": "User not found!"}, status=404)

    # Chat Exist??

    chat_exist = Chat.objects.filter(
        is_group=False,
        members=user,
    ).filter(members=other_user)

    if chat_exist.exists():
        return Response({"message": "Chat already exists!"})

    # Creating chat
    chat = Chat.objects.create(is_group=False)
    chat.members.add(user, other_user)

    return Response({"chat_id": chat.id})


# Create a group chat with a name and multiple members
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_group(request):

    creator = request.user
    group_name = request.data.get("group_name", "")
    usernames = request.data.get("members", [])

    users = User.objects.filter(username__in=usernames).exclude(id=creator.id)

    # Creating group
    group = Chat.objects.create(name=group_name, is_group=True)
    group.members.add(creator, *users)

    return Response({"message": "Group created successfully!"})


# Get messages of chat
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_messages(request, chat_id):

    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"message": "Chat not Found!"}, status=404)

    if not chat.members.filter(id=request.user.id).exists():
        return Response({"message": "You are not a member of this chat!"}, status=403)

    messages = chat.message_set.order_by("timestamp")
    serializer = MessageSerializer(messages, many=True)

    return Response(serializer.data)


# Add member to group
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_member(request, chat_id):

    # Finding User to Add
    username = request.data.get("username")
    user = User.objects.filter(username=username).first()

    if not user:
        return Response({"message": "User not found!"}, status=404)

    # Finding Chat/group
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"message": "Chat not Found!"}, status=404)

    # Checking if requesting user is part of chat/group
    if not chat.members.filter(id=request.user.id).exists():
        return Response({"message": "You are not a member of this chat!"}, status=403)

    # Checking if its a group
    if not chat.is_group:
        return Response(
            {"message": "DM cannot contain more then 2 members"}, status=400
        )

    chat.members.add(user)

    return Response({"message": "User added sucessfully!"}, status=200)


# Search through users
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_user(request):
    query = request.GET.get("q", "").strip()

    # Getting users
    if query:
        result_users = User.objects.filter(username__icontains=query).exclude(
            id=request.user.id
        )
    else:
        result_users = User.objects.none()

    serializer = UserSerializer(result_users, many=True)
    return Response(serializer.data)
