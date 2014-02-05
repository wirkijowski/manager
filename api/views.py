from api.serializers import UserListSerializer, UserDetailSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from api.serializers import ServicesListSerializerGET
from api.serializers import ServicesListSerializerPOST
from api.serializers import ServiceDetailSerializer
from api.serializers import ServiceParamsListSerializerGET
from api.serializers import ServiceParamsListSerializerPOST
from api.serializers import ServiceParamsDetailSerializer
from api.serializers import TaxClassDetailSerializer
from api.serializers import ParamUnitsListSerializer
from api.serializers import ParamUnitsDetailSerializer
from api.serializers import AppsSerializer
from api.models import Services
from api.models import ServiceParams
from api.models import TaxClass
from api.models import ParamUnits
from api.models import UsersServices
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework import serializers

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
    permission_classes = ( IsAdminUser, )

    queryset = User.objects.all()
    serializer_class = UserListSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = ( IsAdminUser, )

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'username'

class ServicesList(generics.ListCreateAPIView):
    permission_classes = ( IsAdminUser, )
    queryset = Services.objects.all()


    def get_serializer_class(self):
        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return ServicesListSerializerGET
        return ServicesListSerializerPOST

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = ( IsAdminUser, )

    queryset = Services.objects.all()
    serializer_class = ServiceDetailSerializer
    lookup_field = 'service_name'


class ServiceParamsList(generics.ListCreateAPIView):
    permission_classes = ( IsAdminUser, )
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

        self.check_object_permissions(self.request, obj)
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
    permission_classes = ( IsAdminUser, )
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

        self.check_object_permissions(self.request, obj)
        return obj

class TaxClassList(generics.ListCreateAPIView):
    permission_classes = ( IsAdminUser, )
    queryset = TaxClass.objects.all()
    serializer_class = TaxClassDetailSerializer

class TaxClassDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = ( IsAdminUser, )

    queryset = TaxClass.objects.all()
    serializer_class = TaxClassDetailSerializer

class ParamUnitsList(generics.ListCreateAPIView):
    permission_classes = ( IsAdminUser, )

    queryset = ParamUnits.objects.all()
    serializer_class = ParamUnitsListSerializer

class ParamUnitsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = ( IsAdminUser, )
    
    queryset = ParamUnits.objects.all()
    serializer_class = ParamUnitsDetailSerializer


class AppsList(generics.ListCreateAPIView):
#    serializer_class = AppsListSerializer
    serializer_class = AppsSerializer
    def get_queryset(self):

        username = self.request.user
        return UsersServices.objects.filter(user=username,deleted=False)

    
    def pre_save(self, obj):
        obj.user = self.request.user
    #    obj.service = Services.objects.get(service_name='application')

    def post(self, request, format=None):
        serializer = AppsSerializer(data=request.DATA, context={'request':
            request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppsDetail(generics.RetrieveUpdateDestroyAPIView):
    #do przepisania na get_queryset
    queryset = UsersServices.objects.all()
    serializer_class = AppsSerializer

    def get_object(self):
        #appname = 'druga aplikacja'
        appname = self.kwargs['appname']
        user = self.request.user
        service =  Services.objects.get(service_name='application')

   #     userservice = UsersServices.objects.get(name=appname, user=user, service=service)

        try:
            return UsersServices.objects.get(name=appname, user=user, service=service, deleted=False)
        except UsersServices.DoesNotExist:
            raise Http404

  #      if userservice.deleted:
  #          return Response( { appname: "Not found"}, status=status.HTTP_404_NOT_FOUND)
  #     else:
  #          return userservice

        #return get_object_or_404(UsersServices.objects.get(name=appname, user=user, service=service, deleted=False))

    def delete(self, request, *args, **kwargs):
        userservice = self.get_object()
        userservice.deleted = True
        userservice.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
