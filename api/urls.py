from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("chats/", views.get_chats, name="get-chats"),
    path("create/dm/", views.create_dm, name="create-dm"),
    path("create/group/", views.create_group, name="create-group"),
    path("chat/<chat_id>/", views.get_messages, name="get-messages"),
    path("add/<chat_id>/", views.add_member, name="add-member"),
    path("user/search/", views.search_user, name="search-user"),
]
