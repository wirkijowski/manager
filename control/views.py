from control.serializers import UserListSerializer, UserDetailSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from control.serializers import ServicesListSerializerGET
from control.serializers import ServicesListSerializerPOST
from control.serializers import ServiceDetailSerializer
from control.serializers import ServiceParamsListSerializerGET
from control.serializers import ServiceParamsListSerializerPOST
from control.serializers import ServiceParamsDetailSerializer
from control.serializers import TaxClassDetailSerializer
from control.serializers import ParamUnitsListSerializer
from control.serializers import ParamUnitsDetailSerializer
from control.models import Services
from control.models import ServiceParams
from control.models import TaxClass
from control.models import ParamUnits
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser


class MultipleFieldLookupMixin(object):

    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)  # Lookup the object

@api_view(('GET',))
def api_root(request, format=None):
    admin_resources = {
        'admin': reverse('admin-resources', request=request, format=format)
    }
    resources = {
        'apps': reverse('apps-list', request=request, format=format),
        'account': 'details',
        'invoices': 'invoices',
    }
    if request.user.is_staff:
        return Response(
            dict(admin_resources.items() + resources.items())
        )
    return Response(
        resources
    )

@api_view(('GET',))
@permission_classes((IsAdminUser, ))
def admin_api(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'services': reverse('services-list', request=request, format=format),
        'tax': reverse('taxclass-list', request=request, format=format),
        'units': reverse('units-list', request=request, format=format),
        })

class UserList(generics.ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserListSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'username'

class ServicesList(generics.ListCreateAPIView):

    queryset = Services.objects.all()


    def get_serializer_class(self):
        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return ServicesListSerializerGET
        return ServicesListSerializerPOST

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceDetailSerializer
    lookup_field = 'service_name'


class ServiceParamsList(generics.ListCreateAPIView):

    def get_queryset(self):
        service=self.kwargs['service_name']
        queryset = ServiceParams.objects.filter(service=service)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        filter['service'] = self.kwargs['service_name']
        filter['param_name'] = self.kwargs['param_name']
        obj = get_object_or_404(queryset, **filter)

        return obj
    def get_serializer_class(self):
        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return ServiceParamsListSerializerGET
        return ServiceParamsListSerializerPOST
    
    # Service's param has one-to-many relation (service 1:* params)
    # When creating new param it has to be assigned to service
    def pre_save(self, obj):
        s = Services(service_name=self.kwargs['service_name'])
        obj.service = s


class ServiceParamsDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ServiceParamsDetailSerializer

    def get_queryset(self):
        service=self.kwargs['service_name']
        param_name=self.kwargs['param_name']
        queryset = ServiceParams.objects.filter(service=service,
                param_name=param_name)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)

        return obj

class TaxClassList(generics.ListCreateAPIView):
    queryset = TaxClass.objects.all()
    serializer_class = TaxClassDetailSerializer

class TaxClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaxClass.objects.all()
    serializer_class = TaxClassDetailSerializer

class ParamUnitsList(generics.ListCreateAPIView):
    queryset = ParamUnits.objects.all()
    serializer_class = ParamUnitsListSerializer

class ParamUnitsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParamUnits.objects.all()
    serializer_class = ParamUnitsDetailSerializer


class AppsList(generics.ListCreateAPIView):
    pass