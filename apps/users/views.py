import json
from django.shortcuts import get_object_or_404
from django.db import transaction
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework import status
from apps.users.authentication import CustomAuthentication
from apps.users.filters import UserSearchFilter
from apps.users.pagination import ReportsPaginator
from .models import FollowRequest, Follower, User
from .serializers import ListFriendSerializer, PendingRequestSerializer, RegisterSerializer, SendRequestSerializer, UserNameListSerializer
from dj_rest_auth.views import LoginView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class CustomLoginView(LoginView):

    def post(self, request, *args, **kwargs):
        email = request.data["email"]
        response = dict()
        self.user = User.objects.get(email=email)
        if User.objects.get(email=email).is_active == False:
            return Response(
                {"Auth_Error": "Account is Currently Deactive"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        refresh = RefreshToken.for_user(self.user)
        response["refresh"] = str(refresh)
        response["access"] = str(refresh.access_token)
        user = User.objects.get(email=self.user.email)
        response["user"] = defaultdict(dict)
        response["user"]["email"] = user.email
        response["user"]["username"] = user.username
        response["user"]["first_name"] = user.first_name
        response["user"]["last_name"] = user.last_name
        return Response(response)


class UserSignUp(APIView):
    serializer_classes = RegisterSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serialize = self.serializer_classes(data=data)
        if serialize.is_valid():
            serialize.save(request)
            return Response({"success": "Account Created Successfully!"})
        else:
            return Response(serialize.errors)


class SearchUser(APIView):
    filter_class = UserSearchFilter
    serializer_class = UserNameListSerializer
    paginator_class = ReportsPaginator
    authentication_classes = [CustomAuthentication]

    def get(self, request, *args, **kwargs):
        self.queryset = User.objects.exclude(email=request.user.email).order_by("-id")
        if self.filter_class:
            self.queryset = self.filter_class(request.GET, queryset=self.queryset).qs
        if self.paginator_class:
            paginator = self.paginator_class()
            page = paginator.paginate_queryset(self.queryset, request)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


class SendRequest(APIView):
    throttle_scope = 'custom_scope'
    authentication_classes = [CustomAuthentication]
    serializer_classes = SendRequestSerializer
    def post(self, request, *args, **kwargs):
        data = request.data
        data["from_user"] = request.user.id
        serialize = self.serializer_classes(data=data)
        if serialize.is_valid():
            serialize.save()
            print(serialize.data)
            return Response({"success" : "Friend Request Sent Successfully!"})
        else:
            return Response(serialize.errors, status=status.HTTP_404_BAD_REQUEST)
        

class ListFollowers(APIView):
    authentication_classes = [CustomAuthentication]
    serializer_classes = ListFriendSerializer
    
    def get(self, request, *args, **kwargs):
        users = Follower.objects.filter(users=request.user)
        serializer = self.serializer_classes(users, many=True)
        return Response(serializer.data)


class ListPendingRequests(APIView):
    authentication_classes = [CustomAuthentication]
    serializer_classes = PendingRequestSerializer
    
    def get(self, request, *args, **kwargs):
        obj = FollowRequest.objects.filter(to_user=request.user, hide=False, accepted=False)
        serializer = self.serializer_classes(obj, many=True)
        return Response(serializer.data)

class RespondRequest(APIView):
    authentication_classes = [CustomAuthentication]
    
    def post(self, request, *args, **kwargs):
        user_id = request.data["id"]
        status = request.data["status"]
        with transaction.atomic():
            follow_request = get_object_or_404(FollowRequest, from_user_id=user_id, to_user=request.user)
            if status:
                follow_request.accepted = True
                follow_request.save()
                follow_request.to_user.followers_count += 1
                follow_request.from_user.following_count += 1
                follow_request.to_user.save()
                follow_request.from_user.save()

                Follower.objects.create(users=follow_request.to_user, follower=follow_request.from_user)
                Follower.objects.create(follower=follow_request.to_user, users=follow_request.from_user)
            else:
                follow_request.hide = True
                follow_request.save()
        return Response({"message": "Follow request responded"})

# • API to send/accept/reject friend request
# • API to list friends(list of users who have accepted friend request)
# • List pending friend requests(received friend request)
# • Users can not send more than 3 friend requests within a minute.