# produk_app/admin.py
from django.contrib import admin
from .models import Kategori, Produk

# Mendaftarkan model Kategori
@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('nama',)  # Menampilkan kolom nama di daftar
    search_fields = ('nama',)  # Mencari berdasarkan nama kategori

# Mendaftarkan model Produk
@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'harga_umum', 'harga_khusus', 'stok', 'kategori')  # Menampilkan kolom yang relevan di daftar
    search_fields = ('kode', 'nama')  # Mencari berdasarkan kode dan nama produk
    list_filter = ('kategori',)  # Memfilter produk berdasarkan kategori

