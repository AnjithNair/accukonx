from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)

class Follower(models.Model):
    users = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)



class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_follow_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_follow_requests", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    hide = models.BooleanField(default=False)