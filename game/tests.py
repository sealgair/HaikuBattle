"""
"""
from django.contrib.auth.models import User

from django.test import TestCase
from game.models import Game, Player

class TestGame(TestCase):
    """
    """
    def setUp(self):
        """
        Make some Users
        """
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

        self.assertEqual(1, game.current_turn.number)
        self.assertEqual("user0", game.judge.user.username)
