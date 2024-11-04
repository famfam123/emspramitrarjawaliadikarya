from django.urls import path
from .views import (
    TransaksiListCreateView,
    AddToCartView,
    ViewCart,
    CheckoutView,
    ClearCartView,
    UpdateCartItemView,
    CartItemView,
    CartItemDetailView,
    InvoiceListCreateView,
    LatestUserTransactionsView,
    
)



urlpatterns = [
    path('transaksi/', TransaksiListCreateView.as_view(), name='transaksi-list-create'),  # Untuk daftar dan membuat transaksi
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),  # Untuk menambahkan item ke keranjang
    path('cart/', ViewCart.as_view(), name='view-cart'),  # Untuk melihat keranjang
    path('clear-cart/', ClearCartView.as_view(), name='clear-cart'), 
    path('checkout/', CheckoutView.as_view(), name='checkout'),  
    path('transactions/latest/', LatestUserTransactionsView.as_view(), name='latest-user-transactions'),  \
    path('cart/item/<int:cart_item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),  
    path('cart/update/<int:cart_item_id>/', UpdateCartItemView.as_view(), name='cart-update'),  
    path('cart/delete/<int:item_id>/', CartItemView.as_view(), name='delete_cart_item'),
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list-create'),
]
