from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User, AnonymousUser
from channels.db import database_sync_to_async


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            encoded_string = scope["query_string"]
            query_string = encoded_string.decode()
            token_str = query_string.split("token=")[-1]
            access = AccessToken(token_str)
            user_id = access["user_id"]

            user = await database_sync_to_async(User.objects.get)(id=user_id)
            scope["user"] = user
        except User.DoesNotExist:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
