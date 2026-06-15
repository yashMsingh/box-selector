from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    length_cm = models.DecimalField(max_digits=8, decimal_places=2)
    width_cm = models.DecimalField(max_digits=8, decimal_places=2)
    height_cm = models.DecimalField(max_digits=8, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}
        if self.length_cm is not None and self.length_cm <= Decimal('0'):
            errors['length_cm'] = 'Length must be greater than 0.'
        if self.width_cm is not None and self.width_cm <= Decimal('0'):
            errors['width_cm'] = 'Width must be greater than 0.'
        if self.height_cm is not None and self.height_cm <= Decimal('0'):
            errors['height_cm'] = 'Height must be greater than 0.'
        if self.weight_kg is not None and self.weight_kg <= Decimal('0'):
            errors['weight_kg'] = 'Weight must be greater than 0.'
        if errors:
            raise ValidationError(errors)


class Box(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    internal_length_cm = models.DecimalField(max_digits=8, decimal_places=2)
    internal_width_cm = models.DecimalField(max_digits=8, decimal_places=2)
    internal_height_cm = models.DecimalField(max_digits=8, decimal_places=2)
    max_weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['cost']

    def __str__(self):
        return self.name

    @property
    def internal_volume_cm3(self):
        return float(self.internal_length_cm * self.internal_width_cm * self.internal_height_cm)

    def clean(self):
        errors = {}
        if self.internal_length_cm is not None and self.internal_length_cm <= Decimal('0'):
            errors['internal_length_cm'] = 'Internal length must be greater than 0.'
        if self.internal_width_cm is not None and self.internal_width_cm <= Decimal('0'):
            errors['internal_width_cm'] = 'Internal width must be greater than 0.'
        if self.internal_height_cm is not None and self.internal_height_cm <= Decimal('0'):
            errors['internal_height_cm'] = 'Internal height must be greater than 0.'
        if self.max_weight_kg is not None and self.max_weight_kg <= Decimal('0'):
            errors['max_weight_kg'] = 'Max weight must be greater than 0.'
        if self.cost is not None and self.cost <= Decimal('0'):
            errors['cost'] = 'Cost must be greater than 0.'
        if errors:
            raise ValidationError(errors)


class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    id = models.AutoField(primary_key=True)
    reference = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    def __str__(self):
        return self.reference


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.order.reference}"

    def clean(self):
        if self.quantity is not None and self.quantity < 1:
            raise ValidationError({'quantity': 'Quantity must be at least 1.'})
