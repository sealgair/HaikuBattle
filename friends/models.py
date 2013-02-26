from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

class FriendshipManager(models.Manager):
    def friendships_for_user(self, user):
        if user.is_anonymous():
            return []
        return Friendship.objects.filter(Q(from_user=user) | Q(to_user=user))

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
        friends = friends.distinct()
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

@receiver(post_save, sender=User)
def rando_friendship(sender, instance, created, **kwargs):
    "Automatically create friendshings from rando to all new players"
    if created:
        rando_user = User.objects.get(id=settings.RANDOM_PLAYER_ID)
        Friendship.objects.create(
            from_user=rando_user,
            to_user=instance,
            confirmed=True
        )

@receiver(pre_save, sender=Friendship)
def rando_friend(sender, instance, **kwargs):
    "Rando always accepts friend requests"
    if instance.to_user.id == settings.RANDOM_PLAYER_ID:
        instance.confirmed = True
