from .models import User
from rest_framework import authentication
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenBackendError


class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if "Authorization" not in request.headers:
            raise ValidationError({"error": "please login"})
        elif (
            request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1] == None
        ):
            raise ValidationError({"error": "please login"})

        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
        except TokenBackendError:
            raise ValidationError({"error": "Token Expired or Invalid Token"})

        user_data = User.objects.get(id=valid_data["user_id"])
        request.user = user_data
        return (user_data, None)