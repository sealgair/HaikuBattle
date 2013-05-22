from django.contrib import messages

from notifications.models import Notification

class NotificationMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            for notification in Notification.objects.filter(recipient=request.user):
                messages.info(request, notification.text)
