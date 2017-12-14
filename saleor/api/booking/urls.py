from django.conf.urls import url

from .views import (
                    PaymentListAPIView,
                    BookingListAPIView,
                    )


urlpatterns = [
    url(r'^$', BookingListAPIView.as_view(),
        name='api-booking-list'),
    url(r'^customer/(?P<pk>[0-9]+)/$', BookingListAPIView.as_view(),
        name='api-customer-booking-list'),
    url(r'^payments/(?P<pk>[0-9]+)/$', PaymentListAPIView.as_view(),
        name='api-booking-payment-list'),
]

