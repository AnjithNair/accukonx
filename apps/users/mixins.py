from django.contrib.auth.hashers import make_password
from .models import User
from random import randint


class RegisterMixins:

    def encode_password(self, password):
        encoded = make_password(password)
        return encoded

    def new_user_data(self, data: dict):
        password = data.pop("password")
        data["password"] = self.encode_password(password)
        return data