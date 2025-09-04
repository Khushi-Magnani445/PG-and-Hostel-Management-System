import csv
import os
import django
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pg_project.settings')
django.setup()

from main_app.models import PG, Tenant

# Load the CSV
with open('data/members.csv', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    count = 0

    for row in reader:
        try:
            # Get PG using both title and city
            pg_instance = pg_instance = PG.objects.filter(title=row['pg_title'].strip(), city=row['pg_city'].strip()).first()


            # Parse joined date
            joined_date = datetime.strptime(row['joined_on'], '%Y-%m-%d').date()

            # Create Tenant
            Tenant.objects.create(
                pg=pg_instance,
                name=row['name'].strip(),
                joined_on=joined_date,
                rent_paid=row['rent_paid'].strip().lower() == 'true'
            )
            count += 1

        except PG.DoesNotExist:
            print(f"PG not found for: {row['pg_title']} in {row['pg_city']}")
        except Exception as e:
            print(f"Error on row: {row} => {e}")

print(f"Tenant loading complete. Total tenants added: {count}")
