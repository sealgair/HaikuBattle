from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from game.models import Player, Game

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
        game = Game.objects.create()
        player = Player.objects.create(user_id=request.user.id, game=game)
        player.judged_game_id = game.id
        game_formset = GameInlineFormset(request.POST, instance=game)
        if game_formset.is_valid():
            game.save()
            game_formset.save()
            game.save() #again, to populate the game's data with the new players
            response = redirect(reverse('game.views.game', kwargs={'game_id': game.id}))
    elif request.method == "GET":
        game_formset = GameInlineFormset(instance=Game())
        player_games = Player.objects.filter(user=request.user.id)

    if response is None:
        context = {
            "game_formset": game_formset,
            "player_games": player_games
        }
        response = render_to_response('dashboard/player_dashboard.html', RequestContext(request, context))

    return response



