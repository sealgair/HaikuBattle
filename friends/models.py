from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max

class FriendshipManager(models.Manager):
    def friendships_for_user(self, user):
        return Friendship.objects.filter(Q(from_friend=user) | Q(to_friend=user))

    def friends_for_user(self, user, confirmed_only=False):
        friends = User.objects.exclude(id=user.id)
        if confirmed_only:
            friends = friends.filter(
                invited_friends__confirmed=True,
                invitee_friends__confirmed=True
            )
        friends = friends.filter(
            Q(invited_friends__to_user=user) |
            Q(invitee_friends__from_user=user)
        )
        for f in friends:
            f.confirmed = f.invitee_friends.get(from_user=user).confirmed
        return friends

class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='invited_friends')
    to_user = models.ForeignKey(User, related_name='invitee_friends')
    confirmed = models.BooleanField(default=False)

    objects = FriendshipManager()

    class Meta:
        unique_together = [
            ('from_user', 'to_user')
        ]