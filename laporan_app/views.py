from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from transaksi_app.models import Transaksi, TransaksiItem

from .serializers import RevenueSummarySerializer, DailySalesChartSerializer
from admin_app.permissions import IsAdminAplikasi  # Import custom permission
import matplotlib.pyplot as plt
import io

from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter


class RevenueSummaryView(APIView):
    permission_classes = [IsAdminAplikasi]

    def get(self, request):
        start_date = timezone.now() - timedelta(days=7)
        try:
            revenue_summary = (
                Transaksi.objects
                .filter(tanggal__gte=start_date)
                .values('tanggal__date')
                .annotate(total_harga=Sum('total_harga'))
                .order_by('tanggal__date')
            )
            print(revenue_summary)  # Debugging: Lihat output di terminal

            serializer = RevenueSummarySerializer(revenue_summary, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error: {e}")  # Tangkap dan cetak kesalahan
            return Response({"error": str(e)}, status=500)
class DailySalesChartView(APIView):
    permission_classes = [IsAdminAplikasi]  # Hanya admin yang bisa akses

    def get(self, request):
        period = request.query_params.get('period', 'daily')  # 'daily', 'weekly', 'monthly', 'yearly'
        days = int(request.query_params.get('days', 30))  # Default 30 hari
        start_date = timezone.now() - timedelta(days=days)

        if period == 'daily':
            daily_sales = self.get_daily_sales(start_date)
        elif period == 'weekly':
            daily_sales = self.get_weekly_sales(start_date)
        elif period == 'monthly':
            daily_sales = self.get_monthly_sales(start_date)
        elif period == 'yearly':
            daily_sales = self.get_yearly_sales(start_date)
        else:
            return Response({"error": "Invalid period"}, status=400)

        serializer = DailySalesChartSerializer(daily_sales, many=True)
        return Response(serializer.data)

    def get_daily_sales(self, start_date):
        return (
            Transaksi.objects
            .filter(tanggal__gte=start_date)
            .extra(select={'tanggal': "DATE(tanggal)"})
            .values('tanggal')
            .annotate(
                total_penjualan=Sum('total_harga'),
                total_transaksi=Count('id')
            )
            .order_by('tanggal')
        )

    def get_weekly_sales(self, start_date):
        return (
            Transaksi.objects
            .filter(tanggal__gte=start_date)
            .extra(select={'week': "WEEK(tanggal, 1)"}).values('week')
            .annotate(
                total_penjualan=Sum('total_harga'),
                total_transaksi=Count('id')
            )
            .order_by('week')
        )

    def get_monthly_sales(self, start_date):
        return (
            Transaksi.objects
            .filter(tanggal__gte=start_date)
            .extra(select={'bulan': "DATE_FORMAT(tanggal, '%Y-%m')"}).values('bulan')
            .annotate(
                total_penjualan=Sum('total_harga'),
                total_transaksi=Count('id')
            )
            .order_by('bulan')
        )

    def get_yearly_sales(self, start_date):
        return (
            Transaksi.objects
            .filter(tanggal__gte=start_date)
            .extra(select={'tahun': "YEAR(tanggal)"}).values('tahun')
            .annotate(
                total_penjualan=Sum('total_harga'),
                total_transaksi=Count('id')
            )
            .order_by('tahun')
        )


