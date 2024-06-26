from django.urls import path
from . import views
from .views import *


app_name = "api"

urlpatterns = [
    
#USER API
    path('user-genrate-otp/',GenrateOtpMobileAPIView.as_view(),name='user-register'),
    path('verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('user_detail_register/', UserDetailAPI.as_view(), name='user_detail_register'),
    path('user-login/', UserLoginAPIView.as_view(), name='user-register'),
    path('otp-login-verify/', OTPLoginVerifyAPIView.as_view(), name='otp-login-verify'),
#HOTEL API

    path('hotel/', HotelApi.as_view(), name='hotel'),
    path('hotel-update/<int:pk>/', HotelUpdateApi.as_view(), name='actors-update'),
    
#PACKAGE
    path('package_detail/', PackageDetailView.as_view(), name='package_detail'),
    path('package_update_delete/<int:pk>/', PackageDetailUpdateDelete.as_view(), name='package_update_delete'),
    path('package-booking-status/',PackageBookingCreate.as_view(), name='package-booking-status'),
    
#REVIEW
path('review/',ReviewAPIView.as_view(), name='review'),

]