from decimal import Decimal

from rest_framework import serializers

from .models import Box, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'length_cm', 'width_cm', 'height_cm', 'weight_kg']
        read_only_fields = ['id']


class BoxSerializer(serializers.ModelSerializer):
    internal_volume_cm3 = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Box
        fields = [
            'id',
            'name',
            'internal_length_cm',
            'internal_width_cm',
            'internal_height_cm',
            'max_weight_kg',
            'cost',
            'internal_volume_cm3',
        ]
        read_only_fields = ['id', 'internal_volume_cm3']

    def get_internal_volume_cm3(self, obj):
        return obj.internal_volume_cm3


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class RecommendBoxRequestSerializer(serializers.Serializer):
    order_reference = serializers.CharField(max_length=100, required=False, default='')
    items = serializers.ListField(
        child=OrderItemInputSerializer(),
        min_length=1,
    )

    def validate(self, data):
        items = data.get('items', [])
        for item in items:
            product_id = item.get('product_id')
            if not Product.objects.filter(pk=product_id).exists():
                raise serializers.ValidationError(
                    {'items': f'Product with id {product_id} does not exist.'}
                )
        return data


class RecommendBoxResponseSerializer(serializers.Serializer):
    order_reference = serializers.CharField()
    recommended_box = BoxSerializer(allow_null=True)
    fits = serializers.BooleanField()
    reason = serializers.CharField()
    total_weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_volume_cm3 = serializers.DecimalField(max_digits=12, decimal_places=2)
    box_volume_cm3 = serializers.FloatField(allow_null=True)
