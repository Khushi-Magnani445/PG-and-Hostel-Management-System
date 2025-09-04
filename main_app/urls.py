from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('listings/', views.pg_listings, name='pg_listings'),
    path('pg/<int:pk>/', views.pg_detail, name='pg_detail'),
    path('pg/add/', views.add_pg, name='add_pg'),
    path('register/', views.register_tenant, name='register_tenant'),
    # Add more routes as needed
    # path('scrap-images/', views.scrap_images, name='scrap_images'),
    # # Ensure that scrap_images is included in the urlpatterns
    # path('download-image/', views.download_image, name='download_image'),
    # This route is for downloading images, if needed
    #path('register-tenant/', views.register_tenant, name='register_tenant'),
    # This route is for registering tenants, if needed
    path('pg/<int:pk>/register/', views.register_tenant, name='pg_register_tenant'),
    # This route is for registering a tenant to a specific PG
    
    # This route is for viewing details of a specific PG
    path('predict-rent/', views.predict_rent, name='predict_rent'),
    path('dashboard/occupancy/', views.occupancy_dashboard, name='occupancy_dashboard'),
    path('recommend-pgs/', views.recommend_pgs, name='recommend_pgs'),
    path('predict-complaint/', views.predict_complaint_resolution, name='predict_complaint_resolution'),

    # Authentication routes
    path('accounts/login/', auth_views.LoginView.as_view(template_name='main_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),

]
