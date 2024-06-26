from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from datetime import timedelta

from .models import *
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'profile_image', 'email', 'user']
        # fields = '__all__'
        
class HotelSerializer(serializers.ModelSerializer):
	class Meta:
		model = Hotel
		fields = ('id', 'name', 'address', 'booking_hotel', 'room_count','image', 'available_rooms')

  
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'comment')  

class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        fields = ('image',)

class PackageSerializer(serializers.ModelSerializer):
    images = PackageImageSerializer(many=True, source='packageimage_set')
    hotels = HotelSerializer(many=True)

    class Meta:
        model = Package
        fields = ('id', 'name', 'overview', 'cost', 'images','hotels', 'package_status')
        
class PackageBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageBooking
        fields = ('id', 'package', 'from_date', 'to_date', 'no_of_days', 'booking_status', 'date_booked')
    
    def calculate_no_of_days(self, from_date, to_date):
        if from_date and to_date:
            delta = to_date - from_date 
            return delta.days
        return None

    def create(self, validated_data):
        from_date = (validated_data.get('from_date', None))
        to_date = (validated_data.get('to_date', None))   
        no_of_days = self.calculate_no_of_days(from_date, to_date) 
        validated_data['no_of_days'] = no_of_days

        return super().create(validated_data)
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'user', 'package', 'rating', 'comment')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

