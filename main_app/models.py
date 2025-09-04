from django.db import models
from textblob import TextBlob
class PG(models.Model):
    title = models.CharField(max_length=150)                      # From 'title'
    address = models.TextField()                                  # From 'address'
    city = models.CharField(max_length=100)                       # From 'city'
    description = models.TextField()                              # From 'description'
    
    established_year = models.IntegerField(null=True, blank=True) # From 'establishedYear'
    house_type = models.CharField(max_length=50)                  # From 'houseType'
    bhk_type = models.CharField(max_length=20)                    # From 'bhkType'
    
    shared = models.BooleanField(default=False)                   # From 'shared'
    bed_available = models.IntegerField()                         # From 'bedAvailable'
    room_available = models.IntegerField()                        # From 'roomAvailable'
    available_for = models.CharField(max_length=50)               # From 'availableFor'
    booking_type = models.CharField(max_length=50)                # From 'bookingType'
    
    area_sqft = models.IntegerField()                             # From 'area(sq-fit)'
    bathroom_count = models.IntegerField()                        # From 'bathroomCount'
    furnishing_type = models.CharField(max_length=50)             # From 'furnishingType'
    
    facilities = models.TextField()                               # From 'facilities' (comma-separated string)
    
    min_rent = models.IntegerField()                              # From 'minRent(Rs)'
    min_room_rent = models.IntegerField()                         # From 'minRoomRent(Rs)'
    min_room_advance = models.IntegerField()                      # From 'minRoomAdvance(Rs)'
    
    latitude = models.FloatField(null=True, blank=True)           # From 'lat'
    longitude = models.FloatField(null=True, blank=True)          # From 'long'
    
    available_from = models.DateField(null=True, blank=True)      # From 'available_from'
    
    is_available = models.BooleanField(default=True) 
    image_url = models.URLField(null=True, blank=True)
    image_file = models.ImageField(upload_to='pg_images/', null=True, blank=True)

    # Logic-driven field (e.g., based on room availability)

    def __str__(self):
        return f"{self.title} - {self.city}"

    

class Tenant(models.Model):
    pg = models.ForeignKey(PG, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    joined_on = models.DateField()
    rent_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} in {self.pg.title}"

class Complaint(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    message = models.TextField()
    is_urgent = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint by {self.tenant.name}"
    
    
class Review(models.Model):
    pg = models.ForeignKey(PG, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)  # Or link to a User model
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    sentiment = models.CharField(max_length=20, default="neutral")
    created_at = models.DateTimeField(auto_now_add=True)    
    def __str__(self):
        return f"{self.name} - {self.pg.title}"

class Complaints(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    complaint_type = models.CharField(max_length=100)  # e.g., plumbing, electrical
    message = models.TextField()
    is_urgent = models.BooleanField(default=False)
    date_raised = models.DateField(auto_now_add=True)
    date_resolved = models.DateField(null=True, blank=True)

    def resolution_time(self):
        if self.date_resolved:
            return (self.date_resolved - self.date_raised).days
        return None

    def __str__(self):
        return f"{self.complaint_type} - {self.tenant.name}"
