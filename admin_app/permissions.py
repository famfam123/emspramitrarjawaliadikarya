from rest_framework.permissions import BasePermission

class IsAdminAplikasi(BasePermission):
    """
    Hanya izinkan akses untuk pengguna dengan is_admin_aplikasi=True.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_aplikasi
