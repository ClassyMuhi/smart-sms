import urllib.parse
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token["user_id"]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_parameters = urllib.parse.parse_qs(query_string)
        token = query_parameters.get("token", [None])[0]

        if not token:
            scope["user"] = AnonymousUser()
        else:
            try:
                # This will verify the token's validity
                UntypedToken(token)
                import jwt
                from django.conf import settings
                # decoded the JWT token
                decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                scope["user"] = await get_user(decoded_data)
            except (InvalidToken, TokenError, jwt.DecodeError) as e:
                scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
