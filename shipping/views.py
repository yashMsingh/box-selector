from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Box, Product
from .selector import OrderPayload, ProductDimensions, select_box
from .serializers import (
    BoxSerializer,
    ProductSerializer,
    RecommendBoxRequestSerializer,
)


class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all().order_by('name')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=200)


class BoxListView(APIView):
    def get(self, request):
        boxes = Box.objects.all().order_by('cost')
        serializer = BoxSerializer(boxes, many=True)
        return Response(serializer.data, status=200)


class RecommendBoxView(APIView):
    def post(self, request):
        # Step 1 — Validate request body
        serializer = RecommendBoxRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data

        # Step 2 — Build list of (ProductDimensions, quantity) tuples
        items_list = []
        for item in validated_data['items']:
            product = Product.objects.get(pk=item['product_id'])
            dims = ProductDimensions(
                length_cm=product.length_cm,
                width_cm=product.width_cm,
                height_cm=product.height_cm,
                weight_kg=product.weight_kg,
            )
            items_list.append((dims, item['quantity']))

        # Step 3 — Build payload
        payload = OrderPayload(items=items_list)

        # Step 4 — Run selector engine
        result = select_box(payload)

        # Step 5 — Build response dict
        response_dict = {
            'order_reference': validated_data.get('order_reference', ''),
            'recommended_box': (
                BoxSerializer(result.recommended_box).data
                if result.recommended_box else None
            ),
            'fits': result.fits,
            'reason': result.reason,
            'total_weight_kg': str(result.total_weight_kg),
            'total_volume_cm3': str(result.total_volume_cm3),
            'box_volume_cm3': result.box_volume_cm3,
        }

        # Step 6 — Always 200; fits=False is a business response, not an error
        return Response(response_dict, status=200)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'service': 'box-selector-api'}, status=200)
