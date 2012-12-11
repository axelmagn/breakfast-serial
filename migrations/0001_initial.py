# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CacheModel'
        db.create_table('bserial_cachemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('bserial', ['CacheModel'])

        # Adding model 'Book'
        db.create_table('bserial_book', (
            ('cachemodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['bserial.CacheModel'], unique=True, primary_key=True)),
            ('asin', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal('bserial', ['Book'])


    def backwards(self, orm):
        # Deleting model 'CacheModel'
        db.delete_table('bserial_cachemodel')

        # Deleting model 'Book'
        db.delete_table('bserial_book')


    models = {
        'bserial.book': {
            'Meta': {'object_name': 'Book', '_ormbases': ['bserial.CacheModel']},
            'asin': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'cachemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bserial.CacheModel']", 'unique': 'True', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'bserial.cachemodel': {
            'Meta': {'object_name': 'CacheModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['bserial']