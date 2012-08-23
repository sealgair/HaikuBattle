from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.widgets import RadioSelect, RadioFieldRenderer
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
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
        queryset=Haiku.objects.all(),
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
            return redirect(reverse('game.views.game', kwargs={'game_id': game_id}))
    else:
        form = BuildHaikuForm(player=player)

    context = {
        'game': game,
        'player': player,
        'form': form
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