from django.urls import path
from .views import (
    ProdukListView,
    ProdukDetailView,
    StockLogListView,
    StockLogDetailView,
)

urlpatterns = [
    # URLs untuk manajemen produk
    path('produk/', ProdukListView.as_view(), name='produk-list'),  # List & Create Produk
    path('produk/<int:pk>/', ProdukDetailView.as_view(), name='produk-detail'),  # Retrieve, Update & Destroy Produk

    # URLs untuk log stok
    path('stok-log/', StockLogListView.as_view(), name='stock-log-list'),  # List & Create StockLog
    path('stok-log/<int:pk>/', StockLogDetailView.as_view(), name='stock-log-detail'),  # Retrieve, Update & Destroy StockLog
]
