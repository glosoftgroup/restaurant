from django.conf.urls import url

from .views import (PaymentListAPIView)


urlpatterns = [
    url(r'^payments/(?P<pk>[0-9]+)/$', PaymentListAPIView.as_view(),
        name='api-booking-payment-list'),
]

