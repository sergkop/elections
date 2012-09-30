# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'ElectionUIKs', fields ['election', 'uik']
        db.delete_unique('elections_electionuiks', ['election_id', 'uik_id'])

        # Removing unique constraint on 'UIK', fields ['tik', 'date', 'number']
        db.delete_unique('elections_uik', ['tik_id', 'date', 'number'])

        # Removing unique constraint on 'ElectionTIKs', fields ['election', 'tik']
        db.delete_unique('elections_electiontiks', ['election_id', 'tik_id'])

        # Deleting model 'ElectionTIKs'
        db.delete_table('elections_electiontiks')

        # Deleting model 'UIK'
        db.delete_table('elections_uik')

        # Deleting model 'ElectionUIKs'
        db.delete_table('elections_electionuiks')

        # Adding model 'ElectionLocation'
        db.create_table('elections_electionlocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['elections.Election'])),
            ('tik', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'])),
        ))
        db.send_create_signal('elections', ['ElectionLocation'])

        # Adding unique constraint on 'ElectionLocation', fields ['election', 'tik']
        db.create_unique('elections_electionlocation', ['election_id', 'tik_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ElectionLocation', fields ['election', 'tik']
        db.delete_unique('elections_electionlocation', ['election_id', 'tik_id'])

        # Adding model 'ElectionTIKs'
        db.create_table('elections_electiontiks', (
            ('tik', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'])),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['elections.Election'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('elections', ['ElectionTIKs'])

        # Adding unique constraint on 'ElectionTIKs', fields ['election', 'tik']
        db.create_unique('elections_electiontiks', ['election_id', 'tik_id'])

        # Adding model 'UIK'
        db.create_table('elections_uik', (
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('tik', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'])),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('tvd', self.gf('django.db.models.fields.BigIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('elections', ['UIK'])

        # Adding unique constraint on 'UIK', fields ['tik', 'date', 'number']
        db.create_unique('elections_uik', ['tik_id', 'date', 'number'])

        # Adding model 'ElectionUIKs'
        db.create_table('elections_electionuiks', (
            ('uik', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['elections.UIK'])),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['elections.Election'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('elections', ['ElectionUIKs'])

        # Adding unique constraint on 'ElectionUIKs', fields ['election', 'uik']
        db.create_unique('elections_electionuiks', ['election_id', 'uik_id'])

        # Deleting model 'ElectionLocation'
        db.delete_table('elections_electionlocation')


    models = {
        'elections.election': {
            'Meta': {'object_name': 'Election'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'vrn': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        },
        'elections.electionlocation': {
            'Meta': {'unique_together': "(('election', 'tik'),)", 'object_name': 'ElectionLocation'},
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['elections.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tik': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Location']"})
        },
        'locations.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'country_related'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'postcode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'in_region'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'region_code': ('django.db.models.fields.IntegerField', [], {}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'tik': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'in_tik'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'tvd': ('django.db.models.fields.BigIntegerField', [], {}),
            'vrnkomis': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'vrnorg': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'x_coord': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'y_coord': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['elections']