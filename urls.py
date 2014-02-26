from django.conf.urls import patterns, include, url
from api.views import *
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include
from django.contrib import admin


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()
#router = routers.DefaultRouter()
#router.register(r'users', UserViewSet)


urlpatterns = format_suffix_patterns(patterns('api.views',
    # Examples:
    url(r'^$', 'api_root'),
    url(r'^admin/$', 'admin_api',
        name='admin-resources'),
    url(r'^admin/users/$',
        UserList.as_view(), 
        name='user-list'),
    url(r'^admin/users/(?P<username>[\w-]+)/$',
        UserDetail.as_view(), 
        name='user-detail'),
    url(r'^admin/services/$',
        ServicesList.as_view(), 
        name='services-list'),
    url(r'^admin/services/(?P<service_name>[\w-]+)/$',
        ServiceDetail.as_view(),
        name='services-detail'),
    url(r'^admin/services/(?P<service_name>[\w-]+)/params/$',
        ServiceParamsList.as_view(), 
        name='params-list'),
    url(r'^admin/services/(?P<service_name>[\w-]+)/params/(?P<param_name>[\s\w-]+)/$',
        ServiceParamsDetail.as_view(), 
        name='param-detail'),
    url(r'^admin/tax/$', TaxClassList.as_view(),
        name='taxclass-list'),
    url(r'^admin/tax/(?P<title>[\w-]+)/$', TaxClassDetail.as_view(),
        name='taxclass-detail'),
    url(r'^admin/units/$', ParamUnitsList.as_view(),
        name='units-list'),
    url(r'^admin/units/(?P<unit>[\w]+)/$', ParamUnitsDetail.as_view(),
        name='units-detail'),


    url(r'apps/$', AppsList.as_view(),
        name='apps-list'),
    url(r'apps/(?P<appname>[\w]+)/$', AppsDetail.as_view(),
        name='apps-detail'),
    url(r'apps/(?P<appname>[\w]+)/power/$', AppsPower.as_view(),
        name='apps-power'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^djangoadmin/', include(admin.site.urls)),
))

#urlpatterns =
urlpatterns += patterns('',
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)
