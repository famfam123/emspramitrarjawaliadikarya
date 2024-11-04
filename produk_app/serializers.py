from rest_framework import serializers
from .models import Produk, Kategori, StockLog
from decimal import Decimal

# Serializer untuk Kategori
class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = ['id', 'nama']

# Serializer untuk Produk
class ProdukSerializer(serializers.ModelSerializer):
    harga_khusus_rupiah = serializers.SerializerMethodField()
    harga_umum_rupiah = serializers.SerializerMethodField()

    class Meta:
        model = Produk
        fields = [
            'id',
            'kode',
            'nama',
            'deskripsi',
            'stok',
            'kategori',
            'barcode',
            'created_at',
            'updated_at',
            'harga_khusus',
            'harga_umum',
            'harga_khusus_rupiah',
            'harga_umum_rupiah',
        ]

    def get_harga_khusus_rupiah(self, obj):
        """Format harga khusus menjadi Rupiah."""
        return f"Rp{obj.harga_khusus:,.0f}".replace(",", ".") if obj.harga_khusus else "Rp0"

    def get_harga_umum_rupiah(self, obj):
        """Format harga umum menjadi Rupiah."""
        return f"Rp{obj.harga_umum:,.0f}".replace(",", ".") if obj.harga_umum else "Rp0"

    def clean_currency_value(self, value):
        """Bersihkan string input yang berupa Rupiah dan ubah menjadi Decimal."""
        if isinstance(value, str):
            value = value.replace("Rp", "").replace(",", "").strip()
            try:
                return Decimal(value)
            except ValueError:
                raise serializers.ValidationError(f"Nilai tidak valid: {value}")
        return value

    def validate_stok(self, value):
        """Validasi untuk memastikan stok tidak negatif."""
        if value < 0:
            raise serializers.ValidationError("Stok tidak boleh negatif.")
        return value

    def validate(self, data):
        """Validasi keseluruhan, misalnya memastikan harga khusus tidak lebih tinggi dari harga umum."""
        harga_khusus = self.clean_currency_value(data.get('harga_khusus', Decimal(0)))
        harga_umum = self.clean_currency_value(data.get('harga_umum', Decimal(0)))

        if harga_khusus > harga_umum:
            raise serializers.ValidationError("Harga khusus tidak boleh lebih tinggi dari harga umum.")
        
        data['harga_khusus'] = harga_khusus
        data['harga_umum'] = harga_umum
        return data

class StockLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLog
        fields = ['id', 'produk', 'perubahan', 'deskripsi', 'created_at']
        read_only_fields = ['created_at']
