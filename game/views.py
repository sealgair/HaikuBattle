from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.widgets import RadioSelect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

from friends.models import Friendship
from game.models import Game, Player, Haiku, Turn

class BuildHaikuForm(forms.ModelForm):
    class Meta:
        model = Haiku
        exclude = ['player', 'turn']

    def __init__(self, data={}, player=None, *args, **kwargs):
        super(BuildHaikuForm, self).__init__(data, *args, **kwargs)
        self.player = player
        self.fields['phrase1'].queryset = self.player.hand.filter(syllables=5)
        self.fields['phrase2'].queryset = self.player.hand.filter(syllables=7)
        self.fields['phrase3'].queryset = self.player.hand.filter(syllables=5)

    def clean(self):
        cleaned_data = super(BuildHaikuForm, self).clean()
        if 'phrase1' in cleaned_data and 'phrase3' in cleaned_data and\
           cleaned_data['phrase1'] == cleaned_data['phrase3']:
            raise forms.ValidationError("Cannot use the same phrase twice")
        return cleaned_data

    def save(self, commit=True):
        haiku = super(BuildHaikuForm, self).save(commit=False)
        haiku.player = self.player
        if commit:
            haiku.save()
        return haiku

class ChooseHaikuForm(forms.Form):
    choices = forms.ModelChoiceField(
        queryset=Haiku.objects.order_by('?'),
        empty_label=None,
        widget=RadioSelect
    )

    def __init__(self, data={}, turn=None, *args, **kwargs):
        super(ChooseHaikuForm, self).__init__(data, *args, **kwargs)
        self.turn = turn
        self.fields['choices'].queryset = self.turn.haiku_set.all()

    def save(self):
        self.turn.advance(self.cleaned_data['choices'])

def build_haiku(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = get_object_or_404(Player, game=game, user=request.user.id)

    if request.method == "POST":
        form = BuildHaikuForm(data=request.POST, player=player)
        if form.is_valid():
            form.save()
            hotseat = request.session.get('hotseat', [])
            for hs_user in hotseat:
                #first check to see if any players in the hotseat are composing
                if game.players.get(user=hs_user).is_composing():
                    return redirect(
                        reverse('game.views.next_hotseat_player',
                            kwargs={'game_id': game_id, 'user_id': hs_user.id}
                        )
                    )
            if game.current_turn.judge.user in hotseat:
                #then check to see if the judge is in the hotseat
                return redirect(
                    reverse('game.views.next_hotseat_player',
                        kwargs={'game_id': game_id, 'user_id': hs_user.id}
                    )
                )
            #otherwise leave the current player authenticated
            return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))
    else:
        form = BuildHaikuForm(player=player)

    context = {
        'game': game,
        'player': player,
        'form': form,
        'syllable_5': player.hand.filter(syllables=5),
        'syllable_7': player.hand.filter(syllables=7),
    }
    return render_to_response(
        "game/build_haiku.html",
        context_instance=RequestContext(request, context)
    )

def judge(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    turn = game.current_turn

    if request.method == "POST":
        form = ChooseHaikuForm(data=request.POST, turn=turn)
        if form.is_valid():
            form.save()
            return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))
    else:
        form = ChooseHaikuForm(turn=turn)

    context = {
        'game': game,
        'form': form
    }
    return render_to_response(
        "game/judge_waiting.html",
        context_instance=RequestContext(request, context)
    )

@login_required
def game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = get_object_or_404(Player, game=game, user=request.user.id)
    context = {
        'game': game
    }
    if game.judge == player:
        return judge(request, game_id)
    elif game.current_turn.haiku_set.filter(player=player).exists():
        context['haiku'] = game.current_turn.haiku_set.get(player=player)
        return render_to_response(
            "game/build_haiku_success.html",
            context_instance=RequestContext(request, context)
        )
    else:
        return build_haiku(request, game_id)

@login_required
def turn(request, turn_id):
    turn = get_object_or_404(Turn, id=turn_id)
    context = {
        'game': turn.game,
        'turn': turn
    }
    return render_to_response(
        "game/turn.html",
        context_instance=RequestContext(request, context)
    )

class InviteForm(forms.Form):
    friend = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
        widget=RadioSelect
    )

    def __init__(self, *args, **kwargs):
        self.game = kwargs.pop('game')
        self.user = kwargs.pop('user')
        super(InviteForm, self).__init__(*args, **kwargs)
        self.fields['friend'].queryset = Friendship.objects.friends_for_user(
            self.user
        ).exclude(
            player__game=self.game
        )

    def save(self):
        new_user = self.cleaned_data['friend']
        self.game.players.create(user=new_user)

@login_required
def invite(request, game_id):
    context = {}
    game = get_object_or_404(Game, id=game_id)
    if request.method == "POST":
        form = InviteForm(request.POST, game=game, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))
    else:
        form = InviteForm(game=game, user=request.user)

    context['form'] = form
    return render_to_response(
        "game/invite_player.html",
        context_instance=RequestContext(request, context)
    )

@login_required
def quit(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.method == "POST":
        if request.POST['confirm'] == 'YES':
            game.players.filter(user=request.user).delete()
            return redirect(reverse('dashboard.views.player_dashboard'))
        else:
            return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))
    return render_to_response("game/quit_confirm.html",
        context_instance=RequestContext(request, {
            'game': game
        })
    )

@login_required
def add_hotseat_player(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST);
        if form.is_valid():
            hotseat_user = form.get_user()
            hotseat = request.session.get('hotseat', [])
            if hotseat_user in hotseat or hotseat_user == request.user:
                messages.info(request, "{0} is already in the hotseat lineup".format(hotseat_user))
            elif not game.players.filter(user=hotseat_user).exists():
                messages.info(request, "{0} isn't playing in this game".format(hotseat_user))
            else:
                hotseat.append(hotseat_user)
            request.session['hotseat'] = hotseat
            return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))
    else:
        form = AuthenticationForm()
    return render_to_response("game/add_hotseat_player.html",
        context_instance=RequestContext(request, {
            'game': game,
            'form': form
        })
    )

@login_required
def remove_hotseat_player(request, game_id, user_id):
    hotseat = request.session.get('hotseat', [])
    for hs_user in hotseat:
        if hs_user.id == int(user_id):
            hotseat.remove(hs_user)
            request.session['hotseat'] = hotseat
            break
    return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))

@login_required
def next_hotseat_player(request, game_id, user_id=None):
    if 'hotseat' in request.session:
        hotseat = request.session.get('hotseat', [])

        hs_user = None
        if user_id is not None:
            for u in hotseat:
                if u.id == int(user_id):
                    hs_user = u
                    break
        if hs_user == None:
            hs_user = hotseat[0]
        hotseat.remove(hs_user)

        request.user.backend = hs_user.backend
        hotseat.append(request.user) #add old user to end of hotseat
        login(request, hs_user) #switch logged in user to next in hotseat
        request.session['hotseat'] = hotseat
        messages.info(request, "It's {0}'s turn now".format(hs_user))
    return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))