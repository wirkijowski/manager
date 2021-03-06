# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UsersServicesParams'
        db.create_table(u'control_usersservicesparams', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('users_service', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user-params', to=orm['api.UsersServices'])),
            ('services_param', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ServiceParams'])),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal(u'api', ['UsersServicesParams'])

        # Adding model 'UsersServiceParamsHistory'
        db.create_table('usersserviceparamshistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('users_service_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.UsersServicesHistory'])),
            ('service_param', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ServiceParams'])),
            ('service_param_value', self.gf('django.db.models.fields.FloatField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'api', ['UsersServiceParamsHistory'])


        # Changing field 'ServiceParams.description'
        db.alter_column('serviceparams', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ServiceParams.max_value'
        db.alter_column('serviceparams', 'max_value', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'ServiceParams.min_value'
        db.alter_column('serviceparams', 'min_value', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'ServiceParams.step_value'
        db.alter_column('serviceparams', 'step_value', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'ServiceParams.sort_order'
        db.alter_column('serviceparams', 'sort_order', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'ParamUnits.unit'
        db.alter_column('paramunits', 'unit', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True))
        # Adding field 'UsersServices.name'
        db.add_column('usersservices', 'name',
                      self.gf('django.db.models.fields.CharField')(default=' ', max_length=60),
                      keep_default=False)

        # Adding field 'UsersServices.description'
        db.add_column('usersservices', 'description',
                      self.gf('django.db.models.fields.TextField')(max_length=255, null=True),
                      keep_default=False)


        # Changing field 'UsersServices.admin_reason'
        db.alter_column('usersservices', 'admin_reason', self.gf('django.db.models.fields.TextField')(max_length=255, null=True))

        # Changing field 'UsersServices.customers_description'
        db.alter_column('usersservices', 'customers_description', self.gf('django.db.models.fields.CharField')(max_length=60))

    def backwards(self, orm):
        # Deleting model 'UsersServicesParams'
        db.delete_table(u'control_usersservicesparams')

        # Deleting model 'UsersServiceParamsHistory'
        db.delete_table('usersserviceparamshistory')


        # Changing field 'ServiceParams.description'
        db.alter_column('serviceparams', 'description', self.gf('django.db.models.fields.TextField')(default=' '))

        # Changing field 'ServiceParams.max_value'
        db.alter_column('serviceparams', 'max_value', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'ServiceParams.min_value'
        db.alter_column('serviceparams', 'min_value', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'ServiceParams.step_value'
        db.alter_column('serviceparams', 'step_value', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'ServiceParams.sort_order'
        db.alter_column('serviceparams', 'sort_order', self.gf('django.db.models.fields.IntegerField')(default=1))

        # Changing field 'ParamUnits.unit'
        db.alter_column('paramunits', 'unit', self.gf('django.db.models.fields.CharField')(max_length=4, primary_key=True))
        # Deleting field 'UsersServices.name'
        db.delete_column('usersservices', 'name')

        # Deleting field 'UsersServices.description'
        db.delete_column('usersservices', 'description')


        # Changing field 'UsersServices.admin_reason'
        db.alter_column('usersservices', 'admin_reason', self.gf('django.db.models.fields.TextField')(default=' ', max_length=255))

        # Changing field 'UsersServices.customers_description'
        db.alter_column('usersservices', 'customers_description', self.gf('django.db.models.fields.TextField')(max_length=255))

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
        u'api.paramunits': {
            'Meta': {'object_name': 'ParamUnits', 'db_table': "'paramunits'"},
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'})
        },
        u'api.serviceparams': {
            'Meta': {'object_name': 'ServiceParams', 'db_table': "'serviceparams'"},
            'available_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'min_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'params'", 'to': u"orm['api.Services']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'step_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ParamUnits']"}),
            'unit_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'api.services': {
            'Meta': {'object_name': 'Services', 'db_table': "'services'"},
            'available_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'base_price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'tax_class': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.TaxClass']"})
        },
        u'api.taxclass': {
            'Meta': {'object_name': 'TaxClass', 'db_table': "'taxclass'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'api.usersservicedomains': {
            'Meta': {'object_name': 'UsersServiceDomains', 'db_table': "'usersservicedomains'"},
            'fqdn': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users_service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user-domains'", 'to': u"orm['api.UsersServices']"})
        },
        u'api.usersserviceparamshistory': {
            'Meta': {'object_name': 'UsersServiceParamsHistory', 'db_table': "'usersserviceparamshistory'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'service_param': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ServiceParams']"}),
            'service_param_value': ('django.db.models.fields.FloatField', [], {}),
            'users_service_history': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.UsersServicesHistory']"})
        },
        u'api.usersservices': {
            'Meta': {'object_name': 'UsersServices', 'db_table': "'usersservices'"},
            'admin_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'admin_reason': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True'}),
            'change': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'customers_description': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Services']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'api.usersserviceshistory': {
            'Meta': {'object_name': 'UsersServicesHistory', 'db_table': "'usersserviceshistory'"},
            'active_from': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'active_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'users_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.UsersServices']"})
        },
        u'api.usersservicesparams': {
            'Meta': {'object_name': 'UsersServicesParams'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'services_param': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ServiceParams']"}),
            'users_service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user-params'", 'to': u"orm['api.UsersServices']"})
        }
    }

    complete_apps = ['api']