from django.contrib import admin

from .models import Box, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'length_cm', 'width_cm', 'height_cm', 'weight_kg']
    search_fields = ['name']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal_length_cm', 'internal_width_cm', 'internal_height_cm', 'max_weight_kg', 'cost']
    ordering = ['cost']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'status', 'created_at']
    list_filter = ['status']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    list_select_related = True
