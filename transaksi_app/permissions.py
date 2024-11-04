from rest_framework import permissions

class IsPetugas(permissions.BasePermission):
    """
    Izin untuk memastikan pengguna adalah petugas kasir.
    """

    def has_permission(self, request, view):
        # Pastikan pengguna terautentikasi dan memiliki peran 'petugas'
        return request.user.is_authenticated and request.user.role == 'petugas'