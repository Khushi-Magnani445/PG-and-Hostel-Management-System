import csv
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pg_project.settings')
django.setup()

from main_app.models import PG

with open('data/PG.csv', newline='', encoding='utf-8') as csvFile:
    reader = csv.DictReader(csvFile)
    
    for row in reader:
        PG.objects.create(
            title=row['title'],
            city=row['city'],
            area_sqft=int(row['area(sq-fit)']),
            address=row['address'],
            available_for=row['availableFor'],
            available_from=datetime.strptime(row['available_from'], '%m/%d/%Y').date() if row['available_from'].strip() else None,
            bathroom_count=int(row['bathroomCount']),
            bed_available=int(row['bedAvailable']),
            bhk_type=row['bhkType'],
            booking_type=row['bookingType'],
            established_year = int(float(row['establishedYear'])) if row['establishedYear'].strip() else None,
            facilities=row['facilities'],
            furnishing_type=row['furnishingType'],
            house_type=row['houseType'],
            is_available=row['is_available'].lower() == 'true',
            latitude=float(row['lat']),
            longitude=float(row['long']),
            min_rent=int(row['minRent(Rs)']),
            min_room_advance=int(row['minRoomAdvance(Rs)']),
            min_room_rent=int(row['minRoomRent(Rs)']),
            room_available=int(row['roomAvailable']),
            shared=row['shared'].lower() == 'true'
        )

print("PG data loaded successfully!")
