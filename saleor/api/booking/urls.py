from django.conf.urls import url

from .views import (
                    PaymentListAPIView,
                    BookingListAPIView,
                    RoomBookingListAPIView,
                    )


urlpatterns = [
    url(r'^$', BookingListAPIView.as_view(),
        name='api-booking-list'),
    url(r'^customer/(?P<pk>[0-9]+)/$', BookingListAPIView.as_view(),
        name='api-customer-booking-list'),
    url(r'^room/(?P<pk>[0-9]+)/$', RoomBookingListAPIView.as_view(),
        name='api-room-booking-list'),
    url(r'^payments/(?P<pk>[0-9]+)/$', PaymentListAPIView.as_view(),
        name='api-booking-payment-list'),
]

