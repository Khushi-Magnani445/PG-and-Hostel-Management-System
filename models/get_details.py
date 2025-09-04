import pandas as pd
from main_app.models import PG
from datetime import datetime

df = pd.read_csv('data/PG.csv')

for index, row in df.iterrows():
    try:
        PG.objects.create(
            title=row.get('title', f"PG {index}"),
            address=row.get('address', 'Not provided'),
            city=row.get('city', 'Unknown'),
            description=row.get('description', 'No description available'),

            established_year=int(row.get('establishedYear', 0)) if not pd.isna(row.get('establishedYear')) else None,
            house_type=row.get('houseType', 'Unknown'),
            bhk_type=row.get('bhkType', '1 BHK'),

            shared=(row.get('shared', 'No') == 'Yes'),
            bed_available=int(row.get('bedAvailable', 0)),
            room_available=int(row.get('roomAvailable', 0)),
            available_for=row.get('availableFor', 'Any'),
            booking_type=row.get('bookingType', 'General'),

            area_sqft=int(row.get('area(sq-fit)', 0)) if not pd.isna(row.get('area(sq-fit)')) else 0,
            bathroom_count=int(row.get('bathroomCount', 1)),
            furnishing_type=row.get('furnishingType', 'Semi-Furnished'),

            facilities=row.get('facilities', 'Basic Facilities'),

            min_rent=int(row.get('minRent(Rs)', 0)),
            min_room_rent=int(row.get('minRoomRent(Rs)', 0)),
            min_room_advance=int(row.get('minRoomAdvance(Rs)', 0)),

            latitude=float(row.get('lat')) if not pd.isna(row.get('lat')) else None,
            longitude=float(row.get('long')) if not pd.isna(row.get('long')) else None,

            available_from=datetime.strptime(row.get('available_from'), "%Y-%m-%d").date() if not pd.isna(row.get('available_from')) else None,

            is_available=True if int(row.get('roomAvailable', 0)) > 0 else False
        )

    except Exception as e:
        print(f"❌ Error at row {index}: {e}")
