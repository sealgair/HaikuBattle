from friends.models import Friendship

def friend_requests(request):
    if request.user.is_authenticated():
        return {
            'confirm_friend_count': Friendship.objects.filter(
                to_user=request.user,
                confirmed=False
            ).count()
        }
    else:
        return {}