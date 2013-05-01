from friends.models import Friendship

def friend_requests(request):
    return {
        'confirm_friend_count': Friendship.objects.filter(
            to_user=request.user,
            confirmed=False
        ).count()
    }