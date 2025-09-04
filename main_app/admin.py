from django.contrib import admin
from .models import PG, Tenant, Complaint,Complaints,Review

admin.site.register(PG)
admin.site.register(Tenant)
admin.site.register(Complaint)
admin.site.register(Complaints)
admin.site.register(Review)
