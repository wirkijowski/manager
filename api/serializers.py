from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.forms import widgets
from rest_framework import serializers
from rest_framework.reverse import reverse
from api.models import Services
from api.models import ServiceParams
from api.models import TaxClass
from api.models import ParamUnits
from api.models import UsersServices
from api.models import UsersServicesParams
from api.models import UsersServiceDomains
import math


class UserListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'url')
        lookup_field = 'username'


class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class ServicesListSerializerGET(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Services
        fields = ( 'service_name', 'url', )
        lookup_field = 'service_name'

class ServicesListSerializerPOST(serializers.HyperlinkedModelSerializer):
    tax_class = serializers.HyperlinkedRelatedField(view_name='taxclass-detail',
            lookup_field='title')
    class Meta:
        model = Services
        fields = ( 'service_name', 'url', 'description',  'available_to',
        'base_price', 'tax_class',)
        lookup_field = 'service_name'


class ServiceDetailSerializer(serializers.HyperlinkedModelSerializer):
    params_list = serializers.SerializerMethodField('get_param_list_url')
    tax_class = serializers.HyperlinkedRelatedField(view_name='taxclass-detail',
            lookup_field='title')
    class Meta:
        model = Services
        fields = ('service_name', 'description', 'available_to', 'base_price',
        'tax_class', 'params_list')

    def get_param_list_url(self, obj):
        kwargs = {'service_name': obj.service_name}
        return reverse('params-list', kwargs=kwargs,
                request=self.context['request'])


class ServiceParamsListSerializerGET(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_param_url')
    class Meta:
        model = ServiceParams
        fields = ('param_name', 'url')

    def get_param_url(self, obj):
        service_name = (
                self.context['request'].parser_context['view']
                .kwargs['service_name'] )
        kwargs = {'service_name': service_name, 'param_name': obj}

        return reverse('param-detail', kwargs=kwargs, request=self.context['request'])


class ServiceParamsListSerializerPOST(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_param_url')
    unit = serializers.HyperlinkedRelatedField(view_name='units-detail',
                                               lookup_field='unit')
    class Meta:
        model = ServiceParams
        fields = ('param_name', 'description', 'min_value', 'max_value',  'step_value',
                  'unit', 'unit_price', 'available_to', 'sort_order' )

    def get_param_url(self, obj):
        service_name = (
                self.context['request'].parser_context['view']
                .kwargs['service_name'] )
        kwargs = {'service_name': service_name, 'param_name': obj}

        return reverse('param-detail', kwargs=kwargs, request=self.context['request'])

class ServiceParamsDetailSerializer(serializers.ModelSerializer):
    unit = serializers.HyperlinkedRelatedField(view_name='units-detail',
                                               lookup_field='unit')
    class Meta:
        model = ServiceParams
        fields = ('param_name', 'description', 'min_value', 'max_value',  'step_value',
                  'unit', 'unit_price', 'available_to', 'sort_order' )


class TaxClassDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxClass


class ParamUnitsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParamUnits


class ParamUnitsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParamUnits


####################################################################

class ParamsSerializer(serializers.Serializer):
    name = serializers.CharField(source='services_param')
    value = serializers.FloatField()
    price = serializers.FloatField(read_only=True, required=False)
    value_units = serializers.SerializerMethodField('get_units')

    def get_units(self, obj):
        return obj.services_param.unit.unit

    def validate_value(self, attrs, value):
        if attrs['services_param'] is None:
            raise serializers.ValidationError( "Param's name is required")
        
        try:
            serviceparam = ServiceParams.objects.get(param_name=attrs['services_param'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError( "Param " +
                    attrs['services_param'] + " does not exist." )
        except: 
            raise serializers.ValidationError( "Something went wrong d41d8c" )

        modulo = ( math.fmod(( attrs['value'] - serviceparam.min_value),
                serviceparam.step_value) )
        
        if modulo == 0.0:
            return attrs
        elif value < serviceparam.min_value or value > serviceparam.max_value:
            raise serializers.ValidationError( "Value for " +
                    attrs['services_param'] + 
            "is out of allowed range: " + serviceparam.min_value + ":" +
            serviceparam.max_value)
        
        elif modulo != 0.0:
            raise serializers.ValidationError( "Value " + value + 
            " is not multiplication of " + serviceparam.setp_value + ".")
        else:
            raise serializers.ValidationError( "Wrong value " + value )

    

class DomainSerializer(serializers.Serializer):
    fqdn = serializers.URLField()

    def restore_object(self, attrs, instance=None):
#        if instance is not None:
#            instance.users_service =  attrs.get('users_service',
#                    instance.users_service)
#            instance.fqdn = attrs.get('fqdn', instance.fqdn)
#            return instance
#
#        domain = UsersServiceDomains()
#        domain.fqdn = attrs['fqdn']
#        return domain
        return attrs    

    def validate(self, attrs):
        # TODO: add some challenge-response to prove that domain belongs to
        # user
        method = self.context['request'].method
        usersService = UsersServices.objects.get(
            user = User.objects.get(
                username = ( self.context['request']
                    .parser_context['view'].request.user )
                ),
            name = ( self.context['request'].parser_context['view']
                .kwargs['appname'] ),
            )
      
        
        try:
            domains = UsersServiceDomains.objects.get(fqdn=attrs['fqdn'])
            print domains
        except MultipleObjectsReturned:
            # Fix to catch proper exception
            raise serializers.ValidationError( "Can\'t assign domain: " +
                    attrs['fqdn'] + ".")

        except ObjectDoesNotExist:
            return attrs
        else:
            if ( (method == 'PUT' or method == 'PATCH')  and
                domains.users_service == usersService ):
                return attrs
            else:
                raise serializers.ValidationError( "Domain " + attrs['fqdn'] + " already used.")
    
       

class AppsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=60)
    description = serializers.CharField(widget=widgets.Textarea,
                                             max_length=255)
    uri = serializers.SerializerMethodField('get_app_uri')
    domains = DomainSerializer(source='user_domains', many=True, allow_add_remove=True)
    params = ParamsSerializer(source='user_services_params', many=True)
    power = serializers.SerializerMethodField('get_power_handler')

    # some magic if selected fields are to be presented
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(AppsSerializer, self).__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


    def get_app_uri(self, obj):
        return reverse('apps-detail', kwargs={'appname': obj}, request=self.context['request'] )

    def get_power_handler(self, obj):
        return reverse('apps-power', kwargs={'appname': obj},
                request=self.context['request'])

    def validate_name(self, attrs, name):

        #TODO:
        #   - validate chars (ex no white space)

        #Validate if name is uniq for particular user's services
        #when creating new resource or changing name
        method = self.context['request'].method
        user = ( self.context['request'].parser_context['view']
                    .request.user )
        # check what is submited (attrs not kwargs - part of URI)
        us = UsersServices.objects.filter(user=user,name=attrs['name']).count()

        attr = attrs['name']


        if method == 'POST' and us !=0:
            raise serializers.ValidationError( "Application " + attrs['name'] + "  exists.")
        #when resource whth submited name exists
        elif (method == 'PUT' or method == 'PATCH') and us!=0 and attr != (
            self.context['request'].parser_context['view'].kwargs['appname'] ):

            raise serializers.ValidationError( "Application " + attrs['name'] + "  exists.")

        else:
            return attrs

    def validate(self, attrs):
        application = Services.objects.get(service_name='application')
        availableParams = ServiceParams.objects.filter(service=application)
      
        if len(availableParams) > len(attrs['user_services_params']):
            raise serializers.ValidationError(
            "Missing params. Please set all available params")
        elif len(availableParams) < len(attrs['user_services_params']):
            raise serializers.ValidationError(
            "To many params.")
        else:
            app_params = []
            for param in availableParams:
                app_params.append(param.param_name)

            for param in attrs['user_services_params']:
                if param['services_param'] in app_params:
                    app_params.remove(param['services_param'])
                else:
                    raise serializers.ValidationError("Param " +
                             param['services_param'] + 
                             " is invalid or redundant.")

            if len(app_params) != 0:
                raise serializers.ValidationError("Missing params")
            else:
                return attrs


    def restore_object(self, attrs, instance=None):

        try:
            usersService = UsersServices.objects.get(
                    user = User.objects.get(
                        username = ( self.context['request']
                            .parser_context['view'].request.user )
                        ),
                    name = ( self.context['request'].parser_context['view']
                        .kwargs['appname'] ),
                    )
                    
        except ObjectDoesNotExist:
            usersService = UsersServices()
            usersService.user = User.objects.get(username=self.context['request'].parser_context['view'].request.user )

            usersService.service = Services.objects.get(service_name='application')
        
        usersService.name = attrs['name']
        usersService.description = attrs['description']
        usersService.save()
        userDomains = usersService.user_domains

        # Delete domain if not in request. Remove domain from request 
        # if already in db then insert into db what left in request.
        if usersService.user_domains.count() > 0:
            for domain in usersService.user_domains.all():
                if domain not in attrs['user_domains']:
                    domain.delete()
           #     else:
           #         atrrs['user_domains'].remove(domain)
        if len(attrs['user_domains']) > 0:
            for domain in attrs['user_domains']:
                newDomain = UsersServiceDomains() 
                newDomain.fqdn = domain['fqdn']
                usersService.user_domains.add(newDomain)

      
        # Assign or update user's params
        #
        # If not assigned
        if usersService.user_services_params.count() == 0:
            userParams = []
            for param in attrs['user_services_params']:
                serviceParam = ServiceParams.objects.get(
                    param_name=param['services_param'])
                usersParam.append( UsersServicesParams(
                        services_param = serviceParam,
                        value = param['value'],
                        price = serviceParam.unit_price * param['value'],
                        ) )
               
            usersService.user_services_params = userParams 
        # update assigned
        else:
            for param in attrs['user_services_params']:
                userparam = usersService.user_services_params.get(
                        services_param=ServiceParams.objects.get(
                            param_name=param['services_param']
                            )
                        )
                userparam.value = param['value']
                userparam.save()

        usersService.save()
        return usersService

    def save(self, **kwargs):
        return self.object

class ServiceOptionsSerializer(serializers.Serializer):

    name = serializers.SerializerMethodField('get_name')
    description = serializers.SerializerMethodField('get_description')
    params = serializers.SerializerMethodField('get_params')
    domains =  serializers.SerializerMethodField('get_domains')
    _base_price = serializers.SerializerMethodField('get_base_price')

    
    def get_name(self, obj):
        return "<application name>"
    
    def get_description(self, obj):
        return "<app description>"

    def get_params(self, obj):
        params = []
        for param in obj.params.all():
            tmp = {
                    'name': param.param_name,
                    'value': "<({0}, {1}, {2})>".format(param.min_value,
                        param.max_value, param.step_value),
                    '_unit': param.unit,
                    '_unit_price': param.unit_price,
                    }
            params.append(tmp)
        return params

    def get_domains(self, obj):
        domains = { 
                'fqdn': "<fqdn>",
                }
        return [domains,]

    def get_base_price(self, obj):
        return obj.base_price
