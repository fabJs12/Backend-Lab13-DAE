from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, CartView, AddToCartView, UpdateCartItemView, RemoveCartItemView

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('carrito/', CartView.as_view(), name='cart-detail'),              # GET /api/carrito/
    path('carrito/agregar/', AddToCartView.as_view(), name='cart-add'),           # POST /api/carrito/agregar/
    path('carrito/actualizar/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-update'), # PUT
    path('carrito/eliminar/<int:item_id>/', RemoveCartItemView.as_view(), name='cart-remove'),   # DELETE
]