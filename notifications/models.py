from django.db import models
from django.contrib.auth.models import User

class NotificationType(models.Model):
    name = models.CharField(max_length=64)
    template = models.TextField()

    def send(self, recipient, context=None):
        if context == None:
            context = {}
        context['recipient'] = recipient

        Notification.objects.create(
            recipient=recipient,
            notification_type=self
        )


class NotificationPreference(models.Model):
    notification_type = models.ForeignKey(NotificationType)
    user = models.ForeignKey(User)
    allowed = models.BooleanField(default=True)


class Notification(models.Model):
    notification_type = models.ForeignKey(NotificationType)
    recipient = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    seen = models.DateTimeField(null=True)
