import pandas as pd
import django, os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pg_project.settings')  # update with your project settings
django.setup()

from main_app.models import Tenant

def generate_occupancy_csv():
    tenants = Tenant.objects.values('joined_on')
    df = pd.DataFrame(list(tenants))
    df['joined_on'] = pd.to_datetime(df['joined_on'])
    
    # Group by month
    df['month'] = df['joined_on'].dt.to_period('M')
    monthly = df.groupby('month').size().reset_index(name='beds_booked')

    os.makedirs('data', exist_ok=True)
    monthly.to_csv('data/occupancy_data.csv', index=False)
    print(" Occupancy CSV saved to data/occupancy_data.csv")
    print(monthly.head())

if __name__ == '__main__':
    generate_occupancy_csv()
