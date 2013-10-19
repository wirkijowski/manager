# coding: utf-8

from django.db import models
from django.contrib.auth.models import User

class TaxClass(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'taxclass'
    
    def __unicode__(self):
        return self.title

class Services(models.Model):
    service_name = models.CharField(max_length=60,primary_key=True)
    available_to = models.DateTimeField(blank=True,null=True)
    tax_class = models.ForeignKey(TaxClass)
    base_price = models.FloatField()
    description = models.TextField()

    class Meta:
        db_table = 'services'

    def __unicode__(self):
        return self.service_name

class ParamUnits(models.Model):
    unit = models.CharField(max_length=4,primary_key=True)

    class Meta:
        db_table = 'paramunits'

class ServiceParams(models.Model):
    service = models.ForeignKey(Services, related_name='params')
    param_name = models.CharField(max_length=60)
    description = models.TextField()
    min_value = models.FloatField()
    max_value = models.FloatField()
    step_value = models.FloatField()
    unit = models.ForeignKey(ParamUnits)
    unit_price = models.FloatField()
    available_to = models.DateTimeField(null=True,blank=True)
    sort_order = models.IntegerField()

    class Meta:
        db_table = 'serviceparams'

    def __unicode__(self):
        return self.param_name


class UsersServices(models.Model):
    user = models.ForeignKey(User)
    service = models.ForeignKey(Services)
    customers_description = models.TextField(max_length=255)
    admin_disabled = models.BooleanField(default=False)
    admin_reason = models.TextField(max_length=255)
    deleted = models.BooleanField(default=False)
    change = models.BooleanField(default=True)
    price = models.FloatField(default=0.0)

    class Meta:
        db_table = 'usersservices'


class UsersServiceDomains(models.Model):
    users_service = models.ForeignKey(UsersServices)
    fqdn = models.URLField(unique=True)

    class Meta:
        db_table = 'usersservicedomains'



class UsersServicesHistory(models.Model):
    users_service = models.ForeignKey(UsersServices)
    active_from = models.DateTimeField(auto_now_add=True)
    active_to = models.DateTimeField(null=True)
    price = models.FloatField()

    class Meta:
        db_table = 'usersserviceshistory'


class UsersServiceParamsHistory(models.Model):
    users_service_history = models.ForeignKey(UsersServicesHistory)
    service_param = models.ForeignKey(ServiceParams)
    service_param_value = models.FloatField()
    price = models.FloatField()

    class Meta:
        db_table = 'usersserviceparamshistory'





