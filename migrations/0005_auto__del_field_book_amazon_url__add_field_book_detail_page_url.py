# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Book.amazon_url'
        db.delete_column('bserial_book', 'amazon_url')

        # Adding field 'Book.detail_page_url'
        db.add_column('bserial_book', 'detail_page_url',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Book.amazon_url'
        db.add_column('bserial_book', 'amazon_url',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Book.detail_page_url'
        db.delete_column('bserial_book', 'detail_page_url')


    models = {
        'bserial.book': {
            'Meta': {'object_name': 'Book'},
            'asin': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'cover_lg_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cover_md_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cover_sm_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'detail_page_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['bserial']