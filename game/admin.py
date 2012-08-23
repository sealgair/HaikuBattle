__author__ = 'courtf'

from django.contrib import admin
from game.models import Dictionary, Phrase, Game, Player

class PhraseInline(admin.TabularInline):
    model = Phrase

class DictionaryAdmin(admin.ModelAdmin):
    inlines = [PhraseInline ]

class PlayerInline(admin.TabularInline):
    model = Player
    exclude = ['turn_order', 'score', 'hand']

class GameAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    exclude = ['judge']

admin.site.register(Dictionary, DictionaryAdmin)
admin.site.register(Game, GameAdmin)


