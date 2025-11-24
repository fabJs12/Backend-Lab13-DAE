from rest_framework import serializers
from .models import Categoria, Producto, CartItem

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    productos = ProductoSerializer(many=True, read_only=True)
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'productos']

class CartItemSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source='producto.id', read_only=True)
    producto_nombre = serializers.SerializerMethodField()
    producto_precio = serializers.SerializerMethodField()
    producto_imagen = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'producto_id', 'producto', 'producto_nombre', 'producto_precio', 'producto_imagen', 'cantidad', 'subtotal']
        read_only_fields = ['id', 'producto_id', 'producto_nombre', 'producto_precio', 'producto_imagen', 'subtotal']

    def get_producto_nombre(self, obj):
        return getattr(obj.producto, 'nombre', None) or getattr(obj.producto, 'name', '')

    def get_producto_precio(self, obj):
        return getattr(obj.producto, 'precio', None) or getattr(obj.producto, 'price', 0)

    def get_producto_imagen(self, obj):
        return getattr(obj.producto, 'imagen_url', None) or getattr(obj.producto, 'image', '')

    def get_subtotal(self, obj):
        return self.get_producto_precio(obj) * obj.cantidad