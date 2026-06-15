from django.contrib import admin
from django.urls import path, include

from shipping import views

urlpatterns = [
    path('', include('shipping.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('shipping.urls')),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]
