x__author__ = 'courtf'

from django.contrib import admin
from game.models import Dictionary, Phrase, Game, Player

class PhraseAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'syllables', 'dictionary']
    list_editable = ['text', 'dictionary']

class PhraseInline(admin.TabularInline):
    model = Phrase

class DictionaryAdmin(admin.ModelAdmin):
    inlines = [PhraseInline ]

class PlayerInline(admin.TabularInline):
    model = Player
    exclude = ['turn_order', 'hand']

class GameAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]

admin.site.register(Dictionary, DictionaryAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Phrase, PhraseAdmin)
