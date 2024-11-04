from django.db import models
from rest_framework import serializers
from datetime import datetime

class RevenueSummarySerializer(serializers.Serializer):
    tanggal = serializers.DateField(source='tanggal__date')
    total_harga = serializers.DecimalField(max_digits=15, decimal_places=2)

    def validate_total_harga(self, value):
        """Ensure total_harga is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Total harga cannot be negative.")
        return value

    def validate_tanggal__date(self, value):
        """Validate that the date is not in the future."""
        if value > datetime.today().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value

class DailySalesChartSerializer(serializers.Serializer):
    tahun = serializers.IntegerField(required=False)
    bulan = serializers.CharField(required=False)  
    minggu = serializers.IntegerField(required=False)  
    tanggal = serializers.DateField(required=False)  
    total_penjualan = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transaksi = serializers.IntegerField()

    def to_representation(self, instance):
        """Mengubah representasi data jika `tanggal` berupa datetime dan hanya mengambil komponen tanggal."""
        representation = super().to_representation(instance)
        
        if 'tanggal' in representation and isinstance(representation['tanggal'], str):
            representation['tanggal'] = representation['tanggal']
        elif 'tanggal' in representation:
            representation['tanggal'] = representation['tanggal'].isoformat() 
        
        return representation

class Produk(models.Model):
    nama_produk = models.CharField(max_length=255)
    jumlah_terjual = models.IntegerField()
    total_pendapatan = models.DecimalField(max_digits=15, decimal_places=2)


