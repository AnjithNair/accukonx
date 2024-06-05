from django.urls import path

from apps.users.views import *
urlpatterns = [
    path("register/", UserSignUp.as_view()),
    path("login/", CustomLoginView.as_view()),
    path("lookup/", SearchUser.as_view()),
    path("list/friends/", ListFollowers.as_view()),
    path("list/pending/requests/", ListPendingRequests.as_view()),
    path("send/follow-request/", SendRequest.as_view()),
    path("follow-request/response/", RespondRequest.as_view()),
]
