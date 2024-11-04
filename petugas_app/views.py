from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum
from transaksi_app.models import Transaksi
from admin_app.serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated 
from datetime import datetime
import pytz
from django.contrib.auth import logout
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Hanya bisa diakses jika pengguna sudah login

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class ServerTimeView(APIView):
    def get(self, request):
        timezone = pytz.timezone("Asia/Jakarta")  # Sesuaikan timezone jika perlu
        current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")  # Format waktu
        return Response({"server_time": current_time})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=200)



class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Menghitung transaksi hari ini
        jumlah_transaksi_hari_ini = Transaksi.objects.filter(user=user, tanggal__date=today).count()
        total_pendapatan_hari_ini = Transaksi.objects.filter(user=user, tanggal__date=today).aggregate(Sum('total_harga'))['total_harga__sum'] or 0

        # Menghitung transaksi hari sebelumnya
        kemarin = today - timezone.timedelta(days=1)
        jumlah_transaksi_kemarin = Transaksi.objects.filter(user=user, tanggal__date=kemarin).count()

        # Menghitung perubahan kinerja
        if jumlah_transaksi_kemarin > 0:
            perubahan_kinerja = ((jumlah_transaksi_hari_ini - jumlah_transaksi_kemarin) / jumlah_transaksi_kemarin) * 100
        else:
            perubahan_kinerja = float('inf')  # Jika tidak ada transaksi kemarin, bisa dianggap perubahan tidak terbatas

        summary_data = {
            'jumlah_transaksi': jumlah_transaksi_hari_ini,
            'total_pendapatan': total_pendapatan_hari_ini,
            'perubahan_kinerja': round(perubahan_kinerja, 2) if perubahan_kinerja != float('inf') else "N/A",
        }

        return Response(summary_data, status=status.HTTP_200_OK)




class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Menampilkan notifikasi milik pengguna yang sedang login.
        """
        user = self.request.user
        return Notification.objects.filter(recipient=user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Menandai notifikasi sebagai sudah dibaca.
        """
        try:
            notification = self.get_object()
            notification.mark_as_read()
            return Response({'status': 'Notifikasi ditandai sebagai sudah dibaca'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notifikasi tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Menandai semua notifikasi milik pengguna yang sedang login sebagai sudah dibaca.
        """
        user = self.request.user
        updated_count = Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
        return Response({'status': f'{updated_count} notifikasi ditandai sebagai sudah dibaca'}, status=status.HTTP_200_OK)
    
    def create_stock_low_notification(self, produk, recipient):
        """
        Membuat notifikasi stok hampir habis (fungsi yang bisa dipanggil dari luar view).
        """
        return Notification.create_stock_low_notification(produk, recipient)

    def create_transaction_success_notification(self, transaksi, recipient):
        """
        Membuat notifikasi transaksi berhasil (fungsi yang bisa dipanggil dari luar view).
        """
        return Notification.create_transaction_success_notification(transaksi, recipient)