from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max

class FriendshipManager(models.Manager):
    def friendships_for_user(self, user):
        if user.is_anonymous():
            return []
        return Friendship.objects.filter(Q(from_friend=user) | Q(to_friend=user))

    def friends_for_user(self, user, confirmed_only=False):
        if user.is_anonymous():
            return []
        friends = User.objects.exclude(id=user.id)
        if confirmed_only:
            friends = friends.filter(
                Q(invited_friends__to_user=user, invited_friends__confirmed=True) |
                Q(invitee_friends__from_user=user, invitee_friends__confirmed=True)
            )
        else:
            friends = friends.filter(
                Q(invited_friends__to_user=user) |
                Q(invitee_friends__from_user=user)
            )
        for f in friends:
            try:
                f.confirmed = f.invitee_friends.get(from_user=user).confirmed
            except Friendship.DoesNotExist:
                f.confirmed = f.invited_friends.get(to_user=user).confirmed
        return friends

class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='invited_friends')
    to_user = models.ForeignKey(User, related_name='invitee_friends')
    confirmed = models.BooleanField(default=False)

    objects = FriendshipManager()

    def __unicode__(self):
        s = u"from {0} to {1}".format(self.from_user, self.to_user)
        if not self.confirmed:
            s += u" unconfirmed"
        return s

    class Meta:
        unique_together = [
            ('from_user', 'to_user')
        ]