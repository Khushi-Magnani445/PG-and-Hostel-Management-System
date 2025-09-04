from django.shortcuts import render,get_object_or_404,redirect
from .models import PG,Tenant,Review
from django.contrib import messages
from django.db.models import Q
from datetime import date
from scrap_images import download_image
import os
import pickle
import numpy as np
import pandas as pd
import json
import ast
from textblob import TextBlob
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from functools import wraps
from sklearn.linear_model import LinearRegression
from django.urls import reverse



# Authentication guard must be defined before use
def require_login(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this feature.')
            return redirect(f"{reverse('login')}?next={request.get_full_path()}")
        return view_func(request, *args, **kwargs)
    return _wrapped


MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'ml_models','rent_model.pkl')

with open(MODEL_PATH, 'rb') as f:
    rent_model = pickle.load(f)
    
COMPLAINT_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models', 'complaint_model.pkl')
with open(COMPLAINT_MODEL_PATH, 'rb') as f:
    complaint_model = pickle.load(f)    

#from django.shortcuts import render 

def home(request):
    # Support search from home while preserving auth gating
    keyword = request.GET.get('keyword', '').strip()
    max_price = request.GET.get('max_price')

    pgs = []
    if keyword or max_price:
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to search listings.')
            return redirect(f"{reverse('login')}?next={request.get_full_path()}")

        qs = PG.objects.all()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(city__icontains=keyword))
        if max_price:
            try:
                qs = qs.filter(min_rent__lte=int(max_price))
            except (TypeError, ValueError):
                pass
        pgs = list(qs[:52])

    return render(request, 'main_app/home.html', { 'pgs': pgs })


def _update_occupancy_and_forecast(event_date: date):
    """Increment current month occupancy and regenerate forecast CSV.
    Creates CSVs if missing. Safe no-op on errors (logs via messages only when available).
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)

        hist_path = os.path.join(data_dir, 'occupancy_data.csv')
        forecast_path = os.path.join(data_dir, 'occupancy_forecast.csv')

        # Load or initialize historical data
        if os.path.exists(hist_path):
            hist = pd.read_csv(hist_path)
        else:
            hist = pd.DataFrame(columns=['month', 'beds_booked'])

        month_str = event_date.strftime('%Y-%m')

        if not hist.empty and month_str in hist['month'].astype(str).values:
            hist.loc[hist['month'] == month_str, 'beds_booked'] = hist.loc[hist['month'] == month_str, 'beds_booked'].astype(int) + 1
        else:
            hist = pd.concat([hist, pd.DataFrame([{'month': month_str, 'beds_booked': 1}])], ignore_index=True)

        # Sort by month chronological
        try:
            hist['month'] = pd.PeriodIndex(hist['month'].astype(str), freq='M').astype(str)
            hist = hist.sort_values('month')
        except Exception:
            pass

        hist.to_csv(hist_path, index=False)

        # Re-train simple linear model and save forecast next 3 months
        df = hist.copy()
        # Guard: require at least 2 points to fit; else flat forecast of current value
        df['period'] = pd.PeriodIndex(df['month'].astype(str), freq='M')
        df['month_num'] = df['period'].apply(lambda x: x.year * 12 + x.month)
        X = df[['month_num']]
        y = df['beds_booked'].astype(int)

        if len(df) >= 2:
            model = LinearRegression()
            model.fit(X, y)
            last_month_num = int(df['month_num'].max())
            future_idx = np.array(range(last_month_num + 1, last_month_num + 4)).reshape(-1, 1)
            forecast_vals = model.predict(future_idx)
            forecast_vals = np.clip(np.rint(forecast_vals).astype(int), 0, None)
        else:
            # With <2 points, just repeat current value
            last_month_num = int(df['month_num'].max()) if len(df) else (event_date.year * 12 + event_date.month)
            last_val = int(y.iloc[-1]) if len(y) else 1
            future_idx = np.array(range(last_month_num + 1, last_month_num + 4)).reshape(-1, 1)
            forecast_vals = np.array([last_val] * 3, dtype=int)

        forecast_df = pd.DataFrame({
            'month_num': future_idx.flatten().tolist(),
            'beds_predicted': forecast_vals.tolist(),
        })
        forecast_df.to_csv(forecast_path, index=False)
    except Exception:
        # Silently ignore in non-critical path; dashboard may fallback to old data
        pass


def _append_booking_log(tenant_name: str, pg_title: str, event_date: date):
    """Append a booking event to data/tenants_log.csv (date, tenant, pg).
    Safe no-op on errors.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        log_path = os.path.join(data_dir, 'tenants_log.csv')

        row = pd.DataFrame([{
            'date': event_date.strftime('%Y-%m-%d'),
            'tenant': tenant_name or 'Guest',
            'pg': pg_title,
        }])
        if os.path.exists(log_path):
            row.to_csv(log_path, mode='a', index=False, header=False)
        else:
            row.to_csv(log_path, index=False)
    except Exception:
        pass

@require_login
def pg_listings(request):
    keyword = request.GET.get('keyword', '').strip()

    if keyword:
        pgs = PG.objects.filter(
            Q(title__icontains=keyword) | Q(city__icontains=keyword)
        )[:50]
    else:
        pgs = PG.objects.all()[:52]

    return render(request, 'main_app/pg_list.html', {'pgs': pgs})

def pg_detail(request, pk):
    pg = get_object_or_404(PG, pk=pk)
    
    # Handle review submission
    if request.method == 'POST' and 'review_submit' in request.POST:
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to submit a review.')
            return redirect(f"{reverse('login')}?next={request.get_full_path()}")
        name = request.POST.get('reviewer_name')
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment')
        sentiment = 'positive' if TextBlob(comment).sentiment.polarity >= 0 else 'negative'
        Review.objects.create(pg=pg, name=name, rating=rating, comment=comment, sentiment=sentiment)
        messages.success(request, "Review submitted!")
        return redirect('pg_detail', pk=pk)

    # Fetch all reviews
    reviews = Review.objects.filter(pg=pg).order_by('-created_at')
    total_reviews = reviews.count()
    positive_reviews = reviews.filter(sentiment="positive").count()
    sentiment_percent = round((positive_reviews / total_reviews) * 100, 1) if total_reviews > 0 else 0

    # Sentiment trend over time
    sentiment_data = (
        Review.objects.filter(pg=pg)
        .annotate(month=TruncMonth('created_at'))
        .values('month', 'sentiment')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Organize for Chart.js
    from collections import defaultdict
    month_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0})
    for entry in sentiment_data:
        month = entry['month'].strftime('%Y-%m')
        month_sentiment[month][entry['sentiment']] = entry['count']

    labels = list(month_sentiment.keys())
    pos_values = [month_sentiment[m]['positive'] for m in labels]
    neg_values = [month_sentiment[m]['negative'] for m in labels]

    return render(request, 'main_app/pg_details.html', {
        'pg': pg,
        'reviews': reviews,
        'sentiment_percent': sentiment_percent,
        'total_reviews': total_reviews,
        'labels': json.dumps(labels),
        'pos_values': json.dumps(pos_values),
        'neg_values': json.dumps(neg_values),
    })

@require_login
def register_tenant(request, pk=None):
    # Supports both routes:
    # - /register/ (POST with pg_id)
    # - /pg/<pk>/register/ (POST without pg_id; uses URL pk)
    if request.method == 'POST':
        pg_id = pk or request.POST.get('pg_id')
        name = request.POST.get('name')

        if not pg_id:
            messages.error(request, "No PG specified.")
            return redirect('home')


        

        pg = get_object_or_404(PG, id=pg_id)

        if pg.bed_available > 0:
            pg.bed_available -= 1
            pg.save()

            Tenant.objects.create(
                pg=pg,
                name=name or 'Guest',
                joined_on=date.today(),
                rent_paid=False
            )
            # Update occupancy history and forecast for dashboard
            _update_occupancy_and_forecast(date.today())
            # Append booking log with tenant and PG name
            _append_booking_log(name, pg.title, date.today())
            messages.success(request, f"{name or 'Tenant'} registered successfully to {pg.title}.")
        else:
            messages.error(request, "Sorry, no beds are available at this PG.")

        return redirect('pg_detail', pk=pg.id)

    # Non-POST access falls back to the PG detail
    if pk:
        return redirect('pg_detail', pk=pk)
    return redirect('home')

    
# def scrap_images(request):
#     image_urls = [
#         'https://example.com/image1.jpg',
#         'https://example.com/image2.jpg',
#         'https://example.com/image3.jpg',
#     ]

#     save_directory = 'static/images/pg_images'
#     os.makedirs(save_directory, exist_ok=True)

#     for i, url in enumerate(image_urls):
#         save_path = os.path.join(save_directory, f'image_{i+1}.jpg')
#         download_image(url, save_path)

#     return redirect('pg_listings')

# def download_image(request):
    image_url = request.GET.get('image_url')
    if not image_url:
        messages.error(request, "No image URL provided.")
        return redirect('pg_listings')

    save_directory = 'static/images/pg_images'
    os.makedirs(save_directory, exist_ok=True)
    save_path = os.path.join(save_directory, 'downloaded_image.jpg')

    download_image(image_url, save_path)
    messages.success(request, "Image downloaded successfully.")
    
    return redirect('pg_listings')


# def pg_detail(request, pk):
#     pg = get_object_or_404(PG, pk=pk)
#     reviews = pg.reviews.order_by('-created_at')
#     if request.method == 'POST' and 'review_submit' in request.POST:
#         name = request.POST.get('reviewer_name')
#         rating = int(request.POST.get('rating', 5))
#         comment = request.POST.get('comment')
#         Review.objects.create(pg=pg, name=name, rating=rating, comment=comment)
#         messages.success(request, "Review submitted!")
#         return redirect('pg_detail', pk=pk)
#     return render(request, 'main_app/pg_details.html', {'pg': pg, 'reviews': reviews})


@require_login
def predict_rent(request):
    predicted_rent = None

    if request.method == 'POST':
        area = float(request.POST['area'])
        beds = int(request.POST['beds'])
        rooms = int(request.POST['rooms'])
        baths = int(request.POST['baths'])
        shared = 1 if request.POST.get('shared') == 'yes' else 0
        furnishing = request.POST['furnishing_type'].lower()  # normalize

        # Your model was trained with drop_first=True
        # furnishing_type_Semi-Furnished and furnishing_type_Unfurnished
        furn_vector = [
            1 if furnishing == 'semi-furnished' else 0,
            1 if furnishing == 'unfurnished' else 0
        ]

        # Features in the exact order as training
        features = np.array([[area, baths, beds, rooms, shared] + furn_vector])

        predicted_rent = round(rent_model.predict(features)[0], 2)

    return render(request, 'main_app/predict_rent.html', {'predicted_rent': predicted_rent})


@require_login
def occupancy_dashboard(request):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    hist_path = os.path.join(base_dir, 'data', 'occupancy_data.csv')
    forecast_path = os.path.join(base_dir, 'data', 'occupancy_forecast.csv')

    hist = pd.read_csv(hist_path)
    forecast = pd.read_csv(forecast_path)

    labels = hist['month'].astype(str).tolist() + ['Forecast '+str(i+1) for i in range(len(forecast))]
    values = hist['beds_booked'].tolist() + forecast['beds_predicted'].tolist()

    return render(request, 'main_app/occupancy_dashboard.html', {
        'labels_json': json.dumps(labels),
        'values_json': json.dumps(values),
    })

@require_login
def recommend_pgs(request):
    recommended_pgs = []

    if request.method == 'POST':
        city = request.POST['city']
        budget = int(request.POST['budget'])
        # Multiple checkboxes; normalize to lowercase for consistent matching
        selected_facilities = [f.strip().lower() for f in request.POST.getlist('facilities')]

        # Query PGs from database matching city and budget
        pgs = PG.objects.filter(city__icontains=city, min_rent__lte=budget)

        def parse_facilities(value):
            """Return a list of facilities from DB field in a robust way.
            Supports: list, JSON/Python-like list strings, or comma-separated strings.
            """
            if not value:
                return []
            if isinstance(value, list):
                return [str(x).strip().lower() for x in value if str(x).strip()]
            if isinstance(value, str):
                s = value.strip()
                # Try safe eval first (handles '["wifi","parking"]' or "['wifi','parking']")
                try:
                    parsed = ast.literal_eval(s)
                    if isinstance(parsed, list):
                        return [str(x).strip().lower() for x in parsed if str(x).strip()]
                except Exception:
                    pass
                # Fallback: treat as comma-separated
                return [part.strip().strip('"\'').lower() for part in s.split(',') if part.strip()]
            # Fallback for unexpected types
            return []

        results = []
        for pg in pgs:
            facilities_list = parse_facilities(pg.facilities)
            # Check if all selected facilities are present
            if all(f in facilities_list for f in selected_facilities):
                results.append(pg)

        recommended_pgs = results

    return render(request, 'main_app/recommend_pg.html', {
        'recommended_pgs': recommended_pgs
    }) 
    
    
@require_login
def predict_complaint_resolution(request):
    predicted_days = None

    if request.method == 'POST':
        complaint_type = request.POST['complaint_type']
        is_urgent = int(request.POST.get('is_urgent', 0))

        # Manual one-hot encoding
        complaint_types = ['cleaning','electrical', 'internet', 'plumbing']  # match training
        type_vector = [1 if complaint_type == t else 0 for t in complaint_types[1:]]  # drop first for dummy

        features = np.array([[is_urgent] + type_vector])
        predicted_days = round(complaint_model.predict(features)[0], 1)

    return render(request, 'main_app/predict_complaint.html', {
        'predicted_days': predicted_days
    })       


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main_app/register.html', {'form': form})


@require_login
def add_pg(request):
    # Staff only: create a new PG via ModelForm with optional image upload
    if not request.user.is_staff:
        messages.error(request, 'Only staff can add PG listings.')
        return redirect('home')

    if request.method == 'POST':
        try:
            data = request.POST
            image = request.FILES.get('image_file')

            pg = PG(
                title=data.get('title') or '',
                address=data.get('address') or '',
                city=data.get('city') or '',
                description=data.get('description') or '',
                established_year=(int(data['established_year']) if data.get('established_year') else None),
                house_type=data.get('house_type') or '',
                bhk_type=data.get('bhk_type') or '',
                shared=bool(data.get('shared')),
                bed_available=int(data.get('bed_available') or 0),
                room_available=int(data.get('room_available') or 0),
                available_for=data.get('available_for') or '',
                booking_type=data.get('booking_type') or '',
                area_sqft=int(data.get('area_sqft') or 0),
                bathroom_count=int(data.get('bathroom_count') or 0),
                furnishing_type=data.get('furnishing_type') or '',
                facilities=data.get('facilities') or '',
                min_rent=int(data.get('min_rent') or 0),
                min_room_rent=int(data.get('min_room_rent') or 0),
                min_room_advance=int(data.get('min_room_advance') or 0),
                is_available=bool(data.get('is_available', True)),
            )
            pg.save()
            if image:
                # Save after instance exists
                pg.image_file.save(image.name, image, save=True)

            messages.success(request, 'PG created successfully!')
            return redirect('pg_detail', pk=pg.pk)
        except Exception as e:
            messages.error(request, f'Failed to create PG: {e}')

    return render(request, 'main_app/add_pg.html')