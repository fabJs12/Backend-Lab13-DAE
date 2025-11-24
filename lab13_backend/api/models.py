from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class CartItem(models.Model):
    session_key = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session_key', 'producto')
        ordering = ['-updated_at']

    def subtotal(self):
        precio = getattr(self.producto, 'precio', None) or getattr(self.producto, 'price', 0)
        return precio * self.cantidad

    def __str__(self):
        return f'{self.session_key} - {self.producto} x{self.cantidad}'