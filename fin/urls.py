"""fin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from my_dashboard import views

from first import views as first_views

from rest_framework import routers


class MyRouter(routers.DefaultRouter):
    include_root_view = True
    include_format_suffixes = False
    root_view_name = 'index'

    def get_api_root_view(self, api_urls=None):
        return first_views.APIRootView.as_view()


router = MyRouter()
router.register(r'records', first_views.RecordViewSet)
router.register(r'contragents', first_views.ContragentsViewSet)

urlpatterns = [
    path('', views.account_index, name='account_index'),
    path('dashboard', views.main, name='dashboard'),
    path('api/common_info', views.common_info, name='common_info'),     
    path('api/account_map', views.show_account_map, name='account_map'),
    path('api/contragent_map', views.show_contragent_map, name='account_map'),
    path('api/record-detail/<int:pk>', first_views.RecordDetail.as_view(), name='record-detail'),
    re_path("api/trans_q/(?P<q_id>[\w\d\-]+)$", views.trans_q, name="trans_q"),
    path('api/project/info', views.project_info, name='project_info'),     
    path('api/trans_context', views.trans_context, name='trans_context'),     
    path('api/trans', views.trans, name='trans'),
    path('logout',
         views.logout_context,
         name="logout"),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('our_accounts/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
]


