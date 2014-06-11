from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.contrib import messages

from friends.models import Friendship

@login_required
def add_friend(request):
    friends = Friendship.objects.friends_for_user(request.user)
    context = {
        'friends': friends
    }
    if request.method == "POST":
        search = request.POST['friend_search']
        try:
            new_friends = User.objects.filter(Q(email__iexact=search) | Q(username__iexact=search))
            for new_friend in new_friends:
                if new_friend in friends:
                    messages.info(request, "You're already friends with {0}.".format(new_friend.username))
                else:
                    Friendship.objects.create(from_user=request.user, to_user=new_friend)
                    messages.info(request, "You have invited {0} to be friends with you.".format(new_friend.username))
        except User.DoesNotExist:
            messages.info(request, "Couldn't find anybody called {0}.".format(search))
        except User.DoesNotExist:
            messages.info(request, "Found multiple users called {0}, please be more specific.".format(search))

        return redirect(request.path)

    else:
        return render_to_response("friends/add_friends.html",
            context_instance=RequestContext(request, context)
        )

@login_required
def confirm_friend(request):
    pending_friendships = Friendship.objects.filter(to_user=request.user, confirmed=False)
    context = {
        'pending_friendships': pending_friendships
    }
    if request.method == "POST":
        friendship = pending_friendships.get(id=request.POST['confirm_id'])
        friendship.confirmed = True
        friendship.save()
        messages.info(request, "You are now friends with {0}".format(friendship.from_user.username))
        return redirect(request.path)
    else:
        return render_to_response("friends/confirm_friend.html",
            context_instance=RequestContext(request, context)
        )