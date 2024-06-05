from rest_framework import serializers
from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings
from django.contrib.auth import get_user_model
from allauth.account.utils import setup_user_email

from apps.users.models import FollowRequest, Follower, User

def email_address_exists(email, exclude_user=None):
    from allauth.account import app_settings as account_settings
    from allauth.account.models import EmailAddress

    emailaddresses = EmailAddress.objects
    if exclude_user:
        emailaddresses = emailaddresses.exclude(user=exclude_user)
    ret = emailaddresses.filter(email__iexact=email).exists()
    if not ret:
        email_field = account_settings.USER_MODEL_EMAIL_FIELD
        if email_field:
            users = get_user_model().objects
            if exclude_user:
                users = users.exclude(pk=exclude_user.pk)
            ret = users.filter(**{email_field + "__iexact": email}).exists()
    return ret


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    ("A user is already registered with this e-mail address.")
                )
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def get_cleaned_data(self):
        username = self.validated_data.get("email", "").split("@")[0]
        return {
            "username": username,
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        return user


class UserNameListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    class Meta:
        model = User
        fields = ["full_name", "id"]

class SendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowRequest
        fields = "__all__"

class ListFriendSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    id =serializers.SerializerMethodField()
    def get_id(self, obj):
        return obj.follower.id
    def get_full_name(self, obj):
        return f"{obj.follower.first_name} {obj.follower.last_name}"
    class Meta:
        model = Follower
        fields = ["full_name", "id"]

class PendingRequestSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    ids =serializers.SerializerMethodField()
    def get_ids(self, obj):
        return obj.from_user.id
    def get_full_name(self, obj):
        return f"{obj.from_user.first_name} {obj.from_user.last_name}"
    class Meta:
        model = FollowRequest
        fields = ["full_name", "ids"]