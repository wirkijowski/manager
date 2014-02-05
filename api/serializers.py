from django.contrib.auth.models import User
from django.forms import widgets
from rest_framework import serializers
from rest_framework.reverse import reverse
from api.models import Services
from api.models import ServiceParams
from api.models import TaxClass
from api.models import ParamUnits
from api.models import UsersServices
from api.models import UsersServicesParams

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

class AppsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=60)
    description = serializers.CharField(widget=widgets.Textarea,
                                             max_length=255)
#    params = 
    uri = serializers.SerializerMethodField('get_app_uri')

    def get_app_uri(self, obj):
        return reverse('apps-detail', kwargs={'appname': obj}, request=self.context['request'] )

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
            print attrs
            return attrs


    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.name =  attrs.get('name', instance.name)
            instance.description = attrs.get('name', instance.name)
            return instance

        newUsersService = UsersServices()
        newUsersService.user = User.objects.get(username=self.context['request'].parser_context['view'].request.user )

        newUsersService.service = Services.objects.get(service_name='application')
        newUsersService.name = attrs['name']
        newUsersService.description = attrs['description']

        return newUsersService


