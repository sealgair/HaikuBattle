# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Dictionary'
        db.create_table('game_dictionary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('game', ['Dictionary'])

        # Adding model 'Phrase'
        db.create_table('game_phrase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('syllables', self.gf('django.db.models.fields.IntegerField')()),
            ('dictionary', self.gf('django.db.models.fields.related.ForeignKey')(related_name='phrases', to=orm['game.Dictionary'])),
        ))
        db.send_create_signal('game', ['Phrase'])

        # Adding model 'Game'
        db.create_table('game_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('game', ['Game'])

        # Adding M2M table for field seen_phrases on 'Game'
        db.create_table('game_game_seen_phrases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('game', models.ForeignKey(orm['game.game'], null=False)),
            ('phrase', models.ForeignKey(orm['game.phrase'], null=False))
        ))
        db.create_unique('game_game_seen_phrases', ['game_id', 'phrase_id'])

        # Adding model 'Turn'
        db.create_table('game_turn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='turns', to=orm['game.Game'])),
            ('judge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='judged_turn', null=True, to=orm['game.Player'])),
            ('number', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='won_turns', null=True, to=orm['game.Haiku'])),
        ))
        db.send_create_signal('game', ['Turn'])

        # Adding model 'Player'
        db.create_table('game_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='players', to=orm['game.Game'])),
            ('turn_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('game', ['Player'])

        # Adding unique constraint on 'Player', fields ['user', 'game']
        db.create_unique('game_player', ['user_id', 'game_id'])

        # Adding unique constraint on 'Player', fields ['user', 'game', 'turn_order']
        db.create_unique('game_player', ['user_id', 'game_id', 'turn_order'])

        # Adding M2M table for field hand on 'Player'
        db.create_table('game_player_hand', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('player', models.ForeignKey(orm['game.player'], null=False)),
            ('phrase', models.ForeignKey(orm['game.phrase'], null=False))
        ))
        db.create_unique('game_player_hand', ['player_id', 'phrase_id'])

        # Adding model 'Haiku'
        db.create_table('game_haiku', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['game.Player'])),
            ('turn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['game.Turn'])),
            ('phrase1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='haiku_phrase1', null=True, to=orm['game.Phrase'])),
            ('phrase2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='haiku_phrase2', null=True, to=orm['game.Phrase'])),
            ('phrase3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='haiku_phrase3', null=True, to=orm['game.Phrase'])),
        ))
        db.send_create_signal('game', ['Haiku'])

        # Adding unique constraint on 'Haiku', fields ['player', 'turn']
        db.create_unique('game_haiku', ['player_id', 'turn_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Haiku', fields ['player', 'turn']
        db.delete_unique('game_haiku', ['player_id', 'turn_id'])

        # Removing unique constraint on 'Player', fields ['user', 'game', 'turn_order']
        db.delete_unique('game_player', ['user_id', 'game_id', 'turn_order'])

        # Removing unique constraint on 'Player', fields ['user', 'game']
        db.delete_unique('game_player', ['user_id', 'game_id'])

        # Deleting model 'Dictionary'
        db.delete_table('game_dictionary')

        # Deleting model 'Phrase'
        db.delete_table('game_phrase')

        # Deleting model 'Game'
        db.delete_table('game_game')

        # Removing M2M table for field seen_phrases on 'Game'
        db.delete_table('game_game_seen_phrases')

        # Deleting model 'Turn'
        db.delete_table('game_turn')

        # Deleting model 'Player'
        db.delete_table('game_player')

        # Removing M2M table for field hand on 'Player'
        db.delete_table('game_player_hand')

        # Deleting model 'Haiku'
        db.delete_table('game_haiku')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'game.dictionary': {
            'Meta': {'object_name': 'Dictionary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'game.game': {
            'Meta': {'object_name': 'Game'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seen_phrases': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'seen_by'", 'symmetrical': 'False', 'to': "orm['game.Phrase']"})
        },
        'game.haiku': {
            'Meta': {'unique_together': "[('player', 'turn')]", 'object_name': 'Haiku'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'haiku_phrase1'", 'null': 'True', 'to': "orm['game.Phrase']"}),
            'phrase2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'haiku_phrase2'", 'null': 'True', 'to': "orm['game.Phrase']"}),
            'phrase3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'haiku_phrase3'", 'null': 'True', 'to': "orm['game.Phrase']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Player']"}),
            'turn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Turn']"})
        },
        'game.phrase': {
            'Meta': {'ordering': "['syllables', 'id']", 'object_name': 'Phrase'},
            'dictionary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phrases'", 'to': "orm['game.Dictionary']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'syllables': ('django.db.models.fields.IntegerField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'game.player': {
            'Meta': {'ordering': "['game', 'turn_order']", 'unique_together': "(('user', 'game'), ('user', 'game', 'turn_order'))", 'object_name': 'Player'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'players'", 'to': "orm['game.Game']"}),
            'hand': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['game.Phrase']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'turn_order': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'game.turn': {
            'Meta': {'object_name': 'Turn'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'turns'", 'to': "orm['game.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'judge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'judged_turn'", 'null': 'True', 'to': "orm['game.Player']"}),
            'number': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'won_turns'", 'null': 'True', 'to': "orm['game.Haiku']"})
        }
    }

    complete_apps = ['game']