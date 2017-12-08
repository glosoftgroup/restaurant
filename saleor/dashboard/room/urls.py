from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # paymentoption urls
    url(r'^$', permission_required('room.view_room', login_url='account_login')
        (views.list), name='room-list'),
    url(r'^add/$', permission_required('room.add_room', login_url='account_login')
        (views.add), name='room-add'),
    url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('room.delete_room', login_url='account_login')
        (views.delete), name='room-delete'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='room-detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.edit, name='room-edit'),
    url(r'^search/$', views.searchs, name='room-search'),
    url(r'^paginate/', views.paginate, name='room_paginate'),
    url(r'fetch/amenities/$', views.fetch_amenities, name="fetch-amenities"),
    url(r'add/amenities/$', views.add_amenities, name="add-amenities"),

    ]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)