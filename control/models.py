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


class ServiceType(models.Model):
    service_type = models.CharField(max_length=60)

    class Meta:
        db_table = 'servicetype'


class Service(models.Model):
    service_type = models.ForeignKey(ServiceType)
    available_to = models.DateTimeField(blank=True,null=True)
    tax_class = models.ForeignKey(TaxClass)
    price = models.FloatField()

    class Meta:
        db_table = 'service'



class ServiceParamType(models.Model):
    param_type = models.TextField()
 
    class Meta:
        db_table = 'serviceparamtype'

   
class ServiceParam(models.Model):
    service = models.ForeignKey(Service)
    service_param_type = models.ForeignKey(ServiceParamType)
    name = models.CharField(max_length=60)
    description = models.TextField()
    price = models.FloatField()
    available_to = models.DateTimeField(null=True,blank=True)
    sort_order = models.IntegerField()

    class Meta:
        db_table = 'serviceparam'


class ServiceParamValue(models.Model):
    service_param = models.ForeignKey(ServiceParam)
    name = models.CharField(max_length=60)
    description = models.TextField()
    value = models.TextField()
    price = models.FloatField(default=0.0)
    available_to = models.DateTimeField(null=True, blank=True)
    sort_order = models.IntegerField()

    class Meta:
        db_table = 'serviceparamvalue'


class UsersService(models.Model):
    user = models.ForeignKey(User)
    service = models.ForeignKey(Service)
    customers_description = models.TextField(max_length=255)
    admin_disabled = models.BooleanField(default=False)
    admin_reason = models.TextField(max_length=255)
    deleted = models.BooleanField(default=False)
    change = models.BooleanField(default=True)
    price = models.FloatField(default=0.0)

    class Meta:
        db_table = 'usersservice'


class UsersServiceDomain(models.Model):
    users_service = models.ForeignKey(UsersService)
    fqdn = models.URLField()

    class Meta:
        db_table = 'usersservicedomain'



class UsersServiceHistory(models.Model):
    users_service = models.ForeignKey(UsersService)
    active_from = models.DateTimeField(auto_now_add=True)
    active_to = models.DateTimeField(null=True)
    price = models.FloatField()

    class Meta:
        db_table = 'usersservicehistory'


class UsersServiceParamHistory(object):
    users_service_history = models.ForeignKey(UsersServiceHistory)
    service_param = models.ForeignKey(ServiceParam)
    service_param_value = models.ForeignKey(ServiceParamValue)
    price = models.FloatField()

    class Meta:
        db_table = 'usersserviceparamhistory'


class UsersServiceChoosenParam(models.Model):
    users_services = models.ForeignKey(UsersService)
    service_param = models.ForeignKey(ServiceParam)
    service_param_value = models.ForeignKey(ServiceParamValue)
    price = models.FloatField()

    class Meta:
        db_table = 'usersservicechoosenparam'



