from django.db import models
from decimal import Decimal, ROUND_DOWN

# Helper untuk format harga menjadi Rupiah
def format_rupiah(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

class Kategori(models.Model):
    nama = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"
        ordering = ['nama']

class Produk(models.Model):
    kode = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    harga_khusus = models.DecimalField(max_digits=12, decimal_places=2)
    harga_umum = models.DecimalField(max_digits=12, decimal_places=2)
    stok = models.PositiveIntegerField(default=0)
    kategori = models.ForeignKey('Kategori', on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

    def is_low_stock(self, threshold=10):
        return self.stok <= threshold

    def update_stock(self, amount, deskripsi="Perubahan stok"):
        if self.stok + amount < 0:
            raise ValueError("Stok tidak dapat menjadi negatif.")

        # Update stok produk
        self.stok += amount
        self.save()

    def get_price(self, is_permanent_customer):
        return self.harga_khusus if is_permanent_customer else self.harga_umum

    def display_harga_khusus(self):
        return format_rupiah(self.harga_khusus)

    def display_harga_umum(self):
        return format_rupiah(self.harga_umum)

    display_harga_khusus.short_description = "Harga Khusus"
    display_harga_umum.short_description = "Harga Umum"



class StockLog(models.Model):
    produk = models.ForeignKey('Produk', on_delete=models.CASCADE)
    perubahan = models.IntegerField()
    deskripsi = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.perubahan} unit untuk {self.produk.nama} pada {self.created_at}"

    class Meta:
        verbose_name = "Log Perubahan Stok"
        verbose_name_plural = "Log Perubahan Stok"
        ordering = ['-created_at']