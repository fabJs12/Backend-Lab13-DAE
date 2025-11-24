from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.response import Response
from .models import Categoria, Producto, CartItem
from .serializers import CategoriaSerializer, ProductoSerializer, CartItemSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

def _get_session_key(request):
    key = request.session.session_key
    if not key:
        request.session.create()
        key = request.session.session_key
    return key

class CartView(APIView):
    """
    GET /api/carrito/  -> { items: [...], total: 0.0 }
    """
    def get(self, request):
        session_key = _get_session_key(request)
        items = CartItem.objects.filter(session_key=session_key).select_related('producto')
        serializer = CartItemSerializer(items, many=True)
        total = sum(item.subtotal() for item in items)
        return Response({'items': serializer.data, 'total': total})

class AddToCartView(APIView):
    """
    POST /api/carrito/agregar/  payload: { producto_id: X, cantidad: Y }
    """
    @transaction.atomic
    def post(self, request):
        session_key = _get_session_key(request)
        product_id = request.data.get('producto_id') or request.data.get('productId')
        cantidad = int(request.data.get('cantidad', 1) or 1)
        if cantidad < 1:
            return Response({'detail': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto = Producto.objects.get(pk=product_id)
        except Producto.DoesNotExist:
            return Response({'detail': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        stock = getattr(producto, 'stock', None)
        if stock is not None and cantidad > stock:
            return Response({'detail': 'Stock insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.get_or_create(session_key=session_key, producto=producto, defaults={'cantidad': cantidad})
        if not created:
            nueva = item.cantidad + cantidad
            if stock is not None and nueva > stock:
                return Response({'detail': 'Stock insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)
            item.cantidad = nueva
            item.save()

        serializer = CartItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateCartItemView(APIView):
    """
    PUT /api/carrito/actualizar/<item_id>/  payload: { cantidad: N }
    """
    @transaction.atomic
    def put(self, request, item_id):
        session_key = _get_session_key(request)
        cantidad = int(request.data.get('cantidad', 1) or 1)
        if cantidad < 1:
            return Response({'detail': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.select_related('producto').get(pk=item_id, session_key=session_key)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        stock = getattr(item.producto, 'stock', None)
        if stock is not None and cantidad > stock:
            return Response({'detail': 'Stock insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

        item.cantidad = cantidad
        item.save()
        return Response(CartItemSerializer(item).data)

class RemoveCartItemView(APIView):
    """
    DELETE /api/carrito/eliminar/<item_id>/
    """
    def delete(self, request, item_id):
        session_key = _get_session_key(request)
        try:
            item = CartItem.objects.get(pk=item_id, session_key=session_key)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
