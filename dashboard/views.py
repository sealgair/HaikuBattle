from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from dashboard.forms import AccountInfoForm

from game.models import Player, Game
from friends.models import Friendship

@login_required(login_url='/accounts/login/')
def player_dashboard(request):
    """
    """
    GameInlineFormset = inlineformset_factory(Game, Player, fields=('user', ),
        can_delete=False, extra=6)

    game_formset = None
    player_games = None
    response = None

    if request.method == 'POST':
        user_ids = request.POST.getlist('player_ids')
        users = User.objects.filter(id__in=user_ids)
        if users:
            game = Game.objects.create()
            player = Player.objects.create(user_id=request.user.id, game=game)
            player.judged_game_id = game.id
            for user in users:
                Player.objects.create(user=user, game=game)
            game.save() #again, to populate the game's data with the new players
            response = redirect(reverse('game.views.game', kwargs={'game_id': game.id}))
    elif request.method == "GET":
        game_formset = GameInlineFormset(instance=Game())
        player_games = Player.objects.filter(user=request.user.id, game__done=False)

    if response is None:
        context = {
            "game_formset": game_formset,
            "player_games": player_games,
            "friends": Friendship.objects.friends_for_user(request.user, confirmed_only=True)
        }
        response = render_to_response('dashboard/player_dashboard.html', RequestContext(request, context))

    return response


def account_info(request):
    context = {}
    if request.method == 'POST':
        form = AccountInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.info(request, "Account info saved successfully")
            return redirect(reverse('dashboard.views.account_info'))
    else:
        form = AccountInfoForm(instance=request.user)
    context = {
        'form': form
    }
    return render_to_response(
        'dashboard/account_info.html',
        RequestContext(request, context)
    )