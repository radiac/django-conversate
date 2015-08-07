# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Room'
        db.create_table(u'conversate_room', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'conversate', ['Room'])

        # Adding model 'RoomUser'
        db.create_table(u'conversate_roomuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conversate.Room'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('has_focus', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_spoke', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('inactive_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_mail_alert', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('colour', self.gf('django.db.models.fields.CharField')(default='000000', max_length=6)),
            ('alert', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('mail_alert', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'conversate', ['RoomUser'])

        # Adding model 'Message'
        db.create_table(u'conversate_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['conversate.Room'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conversate_messages', to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'conversate', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Room'
        db.delete_table(u'conversate_room')

        # Deleting model 'RoomUser'
        db.delete_table(u'conversate_roomuser')

        # Deleting model 'Message'
        db.delete_table(u'conversate_message')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'conversate.message': {
            'Meta': {'ordering': "('timestamp',)", 'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['conversate.Room']"}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conversate_messages'", 'to': u"orm['auth.User']"})
        },
        u'conversate.room': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Room'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'conversate_rooms'", 'symmetrical': 'False', 'through': u"orm['conversate.RoomUser']", 'to': u"orm['auth.User']"})
        },
        u'conversate.roomuser': {
            'Meta': {'ordering': "('room', 'user__username')", 'object_name': 'RoomUser'},
            'alert': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'colour': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '6'}),
            'has_focus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_mail_alert': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_spoke': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mail_alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conversate.Room']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['conversate']