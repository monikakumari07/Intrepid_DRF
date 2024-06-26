from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class CustomUser(AbstractUser):
    otp = models.CharField(max_length=4,blank=True,null=True)
    is_user = models.BooleanField(default=False)
    

    def __str__(self):
        if self.username:
            return self.username
        elif self.email:
            return self.email
        else:
            return f"User {self.id}"
        
class Otp(models.Model):
    mobile_number = models.CharField(max_length=12)
    otp = models.CharField(max_length=4 )
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __str__(self):
        return str(self.otp)
    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='user_images/')
    email = models.EmailField(max_length=254)

    def __str__(self):
        return str(self.user.username) 
    
class Hotel(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    HOTEL_TYPE=(
        ('available','Available'),
        ('not available','Not Available'),
        ('cancelled','Cancelled'),
    )
    booking_hotel = models.CharField(max_length=50, choices=HOTEL_TYPE, default='not available')
    image = models.ImageField(upload_to='hotel_images/',  null=True,blank=True)
    room_count = models.IntegerField(default=0)  
    available_rooms = models.IntegerField(default=0)

    def __str__(self):
        return self.name  
   
class Package(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_package')
    name = models.CharField(max_length=100)
    overview = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    hotels = models.ManyToManyField('Hotel', blank=True)
    PACKAGE_TYPE=(
        ('confirmed','Confirmed'),
        ('pending','Pending'),
        ('cancelled','Cancelled'),
    )
    package_status = models.CharField(max_length=50, choices=PACKAGE_TYPE, default='pending')
    
    def __str__(self):
        return self.name
    
class PackageImage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='package_images/')

    def __str__(self):
        return f"Image for {self.package.name}"
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review')
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    

    def __str__(self):
        return f"Review for {self.package.name}"
    
  

class PackageBooking(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    no_of_days = models.PositiveIntegerField(editable=False)
    BOOKING_TYPE=(
        ('confirmed','Confirmed'),
        ('pending','Pending'),
        ('cancelled','Cancelled'),
    )
    booking_status = models.CharField(max_length=50, choices=BOOKING_TYPE, default='pending')
    date_booked = models.DateField(auto_now_add=True)
    

    def save(self, *args, **kwargs):
        self.no_of_days = (self.to_date - self.from_date).days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.package.name} by {self.user.email}"
    
