from django.urls import path
from .views import (
    LoginView,
    UserCreateView,
    UserToggleActiveView,
    UserDeleteView,
    UserResetPasswordView,
    PasswordResetConfirmView,
    UserListView
)

urlpatterns = [
    # Endpoint untuk login
    path('login/admin/', LoginView.as_view(), name='login_admin'),
    path('login/petugas/', LoginView.as_view(), name='login_petugas'),

    # Endpoint untuk manajemen pengguna
    path('users/', UserListView.as_view(), name='user_list'),  # Untuk melihat daftar pengguna
    path('users/create/', UserCreateView.as_view(), name='user_create'),  # Untuk menambah pengguna baru
    path('users/<int:pk>/toggle-active/', UserToggleActiveView.as_view(), name='user_toggle_active'),  # Untuk mengubah status aktif pengguna
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),  
    path('users/reset-password/', UserResetPasswordView.as_view(), name='user_reset_password'),  # Untuk meminta reset password
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Endpoint diperbarui
]
