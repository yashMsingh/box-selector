from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('boxes/', views.BoxListView.as_view(), name='box-list'),
    path('recommend/', views.RecommendBoxView.as_view(), name='recommend-box'),
]
