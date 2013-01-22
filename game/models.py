from django.db import models
from django.contrib.auth.models import User
from django.db.models import Min

SYLLABLE_AMOUNTS = {
    5: 16,
    7: 8
}

class Dictionary(models.Model):
    """
    """
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

class Phrase(models.Model):
    """
    """
    text = models.CharField(max_length=256)
    syllables = models.IntegerField()
    dictionary = models.ForeignKey(Dictionary, related_name="phrases")

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ['syllables', 'id']

class Game(models.Model):
    """
    """
    seen_phrases = models.ManyToManyField(Phrase, related_name="seen_by")

    def save(self, *args, **kwargs):
        super(Game, self).save(*args, **kwargs)
        if self.players.count() > 0 and not self.turns.exists():
            self.turns.create(number=1)

    @property
    def current_turn(self):
        if self.turns.exists():
            return self.turns.order_by('-number')[0]

    @property
    def judge(self):
        if self.current_turn:
            return self.current_turn.judge

    @property
    def next_judge(self):
        if self.players.exists():
            first_turn = self.players.aggregate(t=Min('turn_order'))['t']
            if self.judge:
                next_turn = self.judge.turn_order + 1
                if not self.players.filter(turn_order=next_turn).exists():
                    next_turn = first_turn
            else:
                next_turn = first_turn
            return self.players.get(turn_order=next_turn)

    def available_phrases(self):
        return Phrase.objects.exclude(seen_by=self)

    def advance_turn(self):
        if self.current_turn.winner:
            judge_turn = self.judge.turn_order
            next_players = self.players.filter(turn_order__gt=judge_turn)
            if not next_players.exists():
                next_players = self.players.all()
            next_player = next_players[0]

            self.turns.create(number=self.current_turn.number+1)
            self.current_turn.judge = next_player
            self.save()

            for player in self.players.all():
                player.save() #rebuild hands

    def last_winning_haiku(self):
        if self.turns.count() > 1:
            last_turn = self.turns.order_by('-number')[1]
            return last_turn.winner

    def pending_players(self):
        return self.players.exclude(id=self.judge.id)\
            .exclude(haiku__in=self.current_turn.haiku_set.all())

    def past_turns(self):
        return self.turns.exclude(id=self.current_turn.id).order_by('-number')

class Turn(models.Model):
    """
    """
    game = models.ForeignKey(Game, related_name="turns")
    judge = models.ForeignKey("Player", null=True, related_name="judged_turn") #saved for posterity
    number = models.PositiveSmallIntegerField()
    winner = models.ForeignKey('Haiku', null=True, related_name="won_turns")

    def waiting_count(self):
        return self.game.players.exclude(id=self.game.judge.id)\
            .exclude(haiku__in=self.haiku_set.all()).count()

    def still_waiting(self):
        return self.waiting_count() > 0

    def advance(self, winning_haiku):
        self.winner = winning_haiku
        self.save()
        self.game.advance_turn()

    def save(self, *args, **kwargs):
        if not self.judge:
            self.judge = self.game.next_judge
        super(Turn, self).save(*args, **kwargs)

class Player(models.Model):
    """
    """
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game, related_name="players")
    turn_order = models.IntegerField()
    hand = models.ManyToManyField(Phrase)

    class Meta:
        unique_together = (
            ("user", "game"),
            ("user", "game", "turn_order")
        )
        ordering = ['game', 'turn_order']

    @property
    def score(self):
        return Turn.objects.filter(winner__player=self).count()

    def fill_hand(self):
        for s in (5,7):
            while self.hand.filter(syllables=s).count() < SYLLABLE_AMOUNTS[s]:
                potentials = self.game.available_phrases().filter(syllables=s)
                if potentials:
                    new_phrase = potentials.order_by('?')[0]
                    self.hand.add(new_phrase)
                    self.game.seen_phrases.add(new_phrase)
                else: return

    def other_players(self):
        return self.game.players.exclude(id=self.id)

    def render_other_players(self):
        other_players = list(self.other_players().values_list('user__username', flat=True))
        if len(other_players) == 0:
            return ""
        if len(other_players) == 1:
            return other_players[0]
        else:
            return "{0} & {1}".format(", ".join(other_players[:-1]), other_players[-1])

    def my_turn(self):
        if self.game.current_turn.judge == self:
            return self.game.pending_players().count() <= 0
        else:
            return self in self.game.pending_players()

    def save(self, *args, **kwargs):
        if self.turn_order is None:
            self.turn_order = self.game.players.aggregate(m=models.Max('turn_order'))['m'] or 0
            self.turn_order += 1

        super(Player, self).save(*args, **kwargs)

        self.fill_hand()

    def is_composing(self):
        "Returns true if the game is waiting on this player to compose a haiku"
        return self in self.game.pending_players()

    def __unicode__(self):
        return unicode(self.user)

class Haiku(models.Model):
    """
    """
    player = models.ForeignKey(Player)
    turn = models.ForeignKey(Turn)
    phrase1 = models.ForeignKey(Phrase, related_name="haiku_phrase1", null=True)
    phrase2 = models.ForeignKey(Phrase, related_name="haiku_phrase2", null=True)
    phrase3 = models.ForeignKey(Phrase, related_name="haiku_phrase3", null=True)

    def __unicode__(self):
        return u"{0} / {1} / {2}".format(self.phrase1, self.phrase2, self.phrase3)

    def as_br(self):
        return u"{0}<br/>{1}</br>{2}</br>".format(self.phrase1, self.phrase2, self.phrase3)

    class Meta:
        unique_together = [
            ('player', 'turn')
        ]

    def save(self, *args, **kwargs):
        created = not self.pk
        try: self.turn
        except Turn.DoesNotExist:
            self.turn = self.player.game.current_turn
        super(Haiku, self).save(*args, **kwargs)

        if created:
            self.player.hand.remove(self.phrase1)
            self.player.hand.remove(self.phrase2)
            self.player.hand.remove(self.phrase3)