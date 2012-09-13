"""
"""
from django.contrib.auth.models import User

from django.test import TestCase
from game.models import Game, Player, Dictionary, Phrase, Haiku

class TestGame(TestCase):
    """
    """
    def setUp(self):
        """
        Make a dictionary and some Users
        """
        dictionary = Dictionary.objects.create()
        for i in range(100):
            Phrase.objects.create(text="phrase {0}".format(i), syllables=7, dictionary=dictionary)
        for i in range(200):
            Phrase.objects.create(text="phrase {0}".format(i), syllables=5, dictionary=dictionary)

        for i in range(5):
            User.objects.create_user("user{0}".format(i), "user{0}@a.com".format(i), "test")


    def test_play_game(self):
        """
        Make a new game, and play a few turns
        """
        game = Game.objects.create()
        for user in User.objects.order_by('username'):
            Player.objects.create(game=game, user=user)
        game.save()

        # make sure the game is set up right
        self.assertEqual(1, game.turns.count())
        self.assertEqual(1, game.current_turn.number)
        self.assertEqual("user0", game.judge.user.username)
        for player in game.players.all():
            self.assertEqual(24, player.hand.count())

        # play a round
        self.assertEqual(4, game.pending_players().count())
        for player in game.players.exclude(id=game.judge.id):
            Haiku.objects.create(
                turn=game.current_turn,
                player=player,
                phrase1=player.hand.filter(syllables=5)[0],
                phrase2=player.hand.filter(syllables=7)[0],
                phrase3=player.hand.filter(syllables=5)[1]
            )
        self.assertEqual(0, game.pending_players().count())
        game.current_turn.advance(game.current_turn.haiku_set.all()[0])

        #make sure turn advanced properly
        self.assertEqual(2, game.turns.count())
        self.assertEqual(2, game.current_turn.number)
        self.assertEqual("user1", game.judge.user.username)
        for player in game.players.all():
            self.assertEqual(24, player.hand.count())
