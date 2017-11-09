from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.list, name='employees'),
	url(r'^add/$', views.add, name='add_employee'),
	# url(r'^add/process/$', views.add_process, name='add_expense_process'),
	# url(r'^delete/(?P<pk>[0-9]+)/$', views.delete, name='expense-delete'),
	# url(r'^expenses/paginate/', views.expenses_paginate, name='expenses_paginate'),
	# url( r'^expenses/search/$', views.expenses_search, name = 'expenses_search' ),
	# url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='pexpense-detail'),
]
