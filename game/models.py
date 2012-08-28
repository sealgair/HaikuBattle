from django.db import models
from django.contrib.auth.models import User

SYLLABLE_AMOUNTS = {
    5: 16,
    7: 8
}

class Dictionary(models.Model):
    """
    """
    name = models.CharField(max_length=256)

class Phrase(models.Model):
    """
    """
    text = models.CharField(max_length=256)
    syllables = models.IntegerField()
    dictionary = models.ForeignKey(Dictionary, related_name="phrases")

    def __unicode__(self):
        return self.text

class Game(models.Model):
    """
    """

    def save(self, *args, **kwargs):
        if self.id and self.judge is None:
            first_turn = self.players.aggregate(t=models.Min('turn_order'))['t']
            self.judge = self.players.get(turn_order=first_turn)
        super(Game, self).save(*args, **kwargs)
        if not self.turns.exists():
            self.turns.create(number=1)

    @property
    def current_turn(self):
        return self.turns.order_by('-number')[0]

    @property
    def judge(self):
        return self.current_turn.judge

    def advance_turn(self):
        current_turn = self.current_turn
        if current_turn.winner:
            self.turns.create(number=current_turn.number+1)
            this_turn = self.players.aggregate(t=models.Min('turn_order'))['t']
            try:
                self.turn.judge = self.players.get(turn_order=this_turn+1)
            except Player.DoesNotExist:
                self.turn.judge = self.players.get(turn_order=0)
            self.save()

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
        self.judge = self.game.judge
        self.save()
        self.game.advance_turn()

    def save(self, *args, **kwargs):
        self.judge = self.game.judge
        super(Turn, self).save(*args, **kwargs)

class Player(models.Model):
    """
    """
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game, related_name="players")
    score = models.IntegerField(default=0)
    turn_order = models.IntegerField()
    hand = models.ManyToManyField(Phrase)

    class Meta:
        unique_together = (
            ("user", "game"),
            ("user", "game", "turn_order")
        )

    def save(self, *args, **kwargs):
        if self.turn_order is None:
            self.turn_order = self.game.players.aggregate(m=models.Max('turn_order'))['m'] or 0
            self.turn_order += 1

        super(Player, self).save(*args, **kwargs)

        for s in (5,7):
            while self.hand.filter(syllables=s).count() < SYLLABLE_AMOUNTS[s]:
                potentials = Phrase.objects.filter(syllables=s).exclude(id__in=self.hand.all())
                if potentials:
                    self.hand.add(potentials.order_by('?')[0])
                else: return

class Haiku(models.Model):
    """
    """
    player = models.ForeignKey(Player)
    turn = models.ForeignKey(Turn)
    phrase1 = models.ForeignKey(Phrase, related_name="haiku_phrase1", null=True)
    phrase2 = models.ForeignKey(Phrase, related_name="haiku_phrase2", null=True)
    phrase3 = models.ForeignKey(Phrase, related_name="haiku_phrase3", null=True)

    def __unicode__(self):
        return "{0} / {1} / {2}".format(self.phrase1, self.phrase2, self.phrase3)

    def as_br(self):
        return "{0}<br/>{1}</br>{2}</br>".format(self.phrase1, self.phrase2, self.phrase3)

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