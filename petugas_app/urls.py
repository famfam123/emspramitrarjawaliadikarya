from django.urls import path
from .views import (
    DashboardSummaryView,
    UserDetailView,
    ServerTimeView,
    LogoutView,
    NotificationViewSet,
)

urlpatterns = [
    path('dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('user-detail/', UserDetailView.as_view(), name='user-detail'),  # Menampilkan info pengguna
    path('server-time/', ServerTimeView.as_view(), name='server-time'),  # Menampilkan waktu server
    path('logout/', LogoutView.as_view(), name='logout'),

    # Tambahkan endpoint untuk notifikasi
    path('notifications/', NotificationViewSet.as_view({'get': 'list'}), name='notification-list'),  # Mendapatkan semua notifikasi
    path('notifications/<int:pk>/', NotificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='notification-detail'),  # Mendapatkan, memperbarui, atau menghapus notifikasi berdasarkan ID
    path('notifications/create/', NotificationViewSet.as_view({'post': 'create'}), name='notification-create'),  # Membuat notifikasi baru
]
