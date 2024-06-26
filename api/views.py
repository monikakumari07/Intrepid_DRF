from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from  django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from .custom_authentication import OTPAuthenticationBackend
from rest_framework.response import Response
from rest_framework import status
import random
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .serializer import *
from django.db.models import Count, Sum
from .models import *
from rest_framework import permissions

class GenrateOtpMobileAPIView(APIView):
    # permission_classes = (AllowAny)
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        try:
            user = CustomUser.objects.get(username=mobile_number)
            otp = str(random.randint(1000, 9999))
            Otp.objects.create(otp=otp, mobile_number=mobile_number)
            return Response({"otp": otp}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            
            new_user = CustomUser(username=mobile_number, is_active=False)
            new_user.save()
            
            otp = str(random.randint(1000, 9999))
            Otp.objects.create(otp=otp, mobile_number=mobile_number)
            
            return Response({"otp": otp, "message": "New mobile number saved and OTP sent."}, status=status.HTTP_200_OK)
        
class VerifyOTP(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        otp = request.data.get('otp')
        try:
            otp_obj = Otp.objects.get(otp=otp)
            otp_obj.delete()
        except Otp.DoesNotExist:
            return Response({"error": "Invalid OTP or Mobile Number"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
    
    
    

class UserDetailAPI(APIView):
    def get(self, request, format=None):
        users_detials = UserProfile.objects.all()
        serializer = UserProfileSerializer(users_detials, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def post(Self, request):
        name = request.data.get('name')
        mobile_number = request.data.get('mobile_number')
        email = request.data.get('email')
        profile_image = request.FILES.get('profile_image')
       
        if CustomUser.objects.filter(username=mobile_number).exists():
            return Response({"message": "Already Register. Please use a different mobile number."}, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.create_user(
            username=mobile_number, email=email)
        user_detail = UserProfile.objects.create(
            user=user,
            name=name,
            profile_image=profile_image

        )
        user.is_user = True
        user.save()
        serializer = UserProfileSerializer(user_detail)
        response = {
            "success": "true",
            "message": "successfully registered",
            "result": serializer.data,


        }

        return Response(response)
    
# USER LOGIN API


class UserLoginAPIView(APIView):
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        try:
            user = CustomUser.objects.get(username=mobile_number)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found or not registered"}, status=status.HTTP_404_NOT_FOUND)
        new_otp = str(random.randint(1000, 9999))
        user.otp = new_otp
        user.save()

        return Response({"otp": new_otp}, status=status.HTTP_200_OK)

class OTPLoginVerifyAPIView(APIView):
    def post(self,request):
        otp= request.data.get('otp')
         
        user_obj = CustomUser.objects.filter(otp=otp).exists()
        if user_obj:
            user = OTPAuthenticationBackend.authenticate(self,request,otp=otp)
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message" : 'Success',
                "token": str(token.key),
            })
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class HotelApi(APIView):
    def get(self, request, format=None):
        hotel_detials = Hotel.objects.all()
        serializer = UserProfileSerializer(hotel_detials, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        name = request.data.get('name')
        image = request.FILES.get('image')
        address = request.data.get('address')
        available_rooms = request.data.get('available_rooms')
        booking_hotel = request.data.get('booking_hotel')
        room_count = request.data.get('room_count')
        hotel = Hotel.objects.create(name=name, address=address, available_rooms=available_rooms, room_count=room_count,  image=image, booking_hotel=booking_hotel)
        serializer = HotelSerializer(hotel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#UPDATE Hotel
class HotelUpdateApi(APIView):
    def put(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=pk)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found."},
                            status=status.HTTP_404_NOT_FOUND)       
        serializer = HotelSerializer(hotel, data=request.data, partial=True)# Use the update serializer for updating the actor
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Successfully updated", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PackageDetailView(APIView):
    # permission_classes =[IsAuthenticated]
    def get(self, request):
        package_get_all = Package.objects.all()
        serializer = PackageSerializer(package_get_all, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        name = request.data.get('name')
        overview = request.data.get('overview')
        cost = request.data.get('cost')
        reviews = request.data.getlist('reviews')
        
        hotels = request.data.getlist('hotels', [])
        hotels_instances = []

        users_id = request.data.get('user')
        reviews_data = request.POST.getlist('reviews')
        package_status = request.data.get('package_status')
        
        try:
            user = CustomUser.objects.get(id=users_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "CustomUser Id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
        package = Package.objects.create(
            user=user,
            name=name,
            overview=overview,
            cost=cost,
            package_status=package_status

        )

        for hotel_id in hotels:
            try:
                hotel = Hotel.objects.get(id=hotel_id)
                package.hotels.add(hotel)
            except Hotel.DoesNotExist:
                return Response({"error": f"Hotel with ID {hotel_id} does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        for img in request.FILES.getlist('images'):
            PackageImage.objects.create(package=package, image=img)

        package.save()

        serializer = PackageSerializer(package)
        return JsonResponse(serializer.data, status=201)

class PackageDetailUpdateDelete(APIView):
    def put(self,request,pk):
        try:
            package = Package.objects.get(id=pk)
        except package.DoesNotExist:
            return Response({"message":"package does not found"},status=status.HTTP_404_NOT_FOUND)
        
        obj_package_name = Package.objects.filter(name=request.data.get('name')).exists()
        if obj_package_name:
            return Response({"message": "package name  already exist, please enter another name."}, status=status.HTTP_404_NOT_FOUND)
        
        package.name = request.data.get("name", package.name)
        package.overview = request.data.get("overview", package.overview)
        package.cost = request.data.get("cost", package.cost)
        package.package_status = request.data.get("package_status", package.package_status)
        
        if 'images' in request.FILES:
            package.packageimage_set.all().delete()
            for img in request.FILES.getlist('images'):
                PackageImage.objects.create(package=package, image=img)

        hotel_ids = request.POST.getlist('hotels')
        if hotel_ids:
            package.hotels.clear()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, pk=hotel_id)
                package.hotels.add(hotel)

        package.save()
       
        return Response({"message":"updated sucessfully", "status": status.HTTP_200_OK})
    

    #delete 
    def delete(self, request, pk):
        try:
            package = Package.objects.get(id=pk)
        except Package.DoesNotExist:
            return Response({"message": "Package Id not found"}, status=status.HTTP_404_NOT_FOUND)
        package.delete()
        return Response({"message": "Package Id deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    #GET BY ID
    def get(self, request,pk):
        if pk:
            package_get_id = Package.objects.get(id=pk)
            serializer = PackageSerializer(package_get_id)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


class PackageBookingCreate(APIView):
    # permission_classes =[IsAuthenticated,IsSuperAdmin]
    def get(self, request):
        try:
            packages = Package.objects.all()
            package_stats = []

            for package in packages:
                package_bookings = PackageBooking.objects.filter(package=package)

                confirmed_count = package_bookings.filter(booking_status='confirmed').count()
                pending_count = package_bookings.filter(booking_status='pending').count()
                cancelled_count = package_bookings.filter(booking_status='cancelled').count()
                total_cost = package_bookings.aggregate(Sum('package__cost'))['package__cost__sum']

                # Calculate total number of days booked
                total_days_booked = package_bookings.aggregate(Sum('no_of_days'))['no_of_days__sum']

                # Construct package statistics
                package_stat = {
                    'package_id': package.id,
                    'package_name': package.name,
                    'total_bookings': package_bookings.count(),
                    'confirmed_bookings': confirmed_count,
                    'pending_bookings': pending_count,
                    'cancelled_bookings': cancelled_count,
                    'total_cost': total_cost if total_cost else 0,
                    'total_days_booked': total_days_booked if total_days_booked else 0,
                }
                package_stats.append(package_stat)

            return Response(package_stats, status=status.HTTP_200_OK)

        except Package.DoesNotExist:
            return Response({"message": "Packages not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):            
        booking_status = request.data.get('booking_status', None)
        if booking_status is None or booking_status == '':       
            request.data['booking_status'] = 'pending'      
        serializer =PackageBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking_status = request.data.get('booking_status', None)
            if booking_status and booking_status in ['confirmed', 'pending','cancelled']:              
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Invalid booking status value. Use 'confirmed', 'pending', 'cancelled'."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)














