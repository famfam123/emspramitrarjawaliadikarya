from django.db import models
from django.utils import timezone
from admin_app.models import CustomUser
from produk_app.models import Produk
from transaksi_app.models import Transaksi, TransaksiItem  
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('STOCK_LOW', 'Stok Hampir Habis'),
        ('TRANSACTION_SUCCESS', 'Transaksi Berhasil'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Penerima notifikasi
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)  # Tipe notifikasi
    message = models.TextField()  # Pesan notifikasi
    is_read = models.BooleanField(default=False)  # Status baca
    created_at = models.DateTimeField(auto_now_add=True)  # Tanggal dan waktu notifikasi dibuat

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.message[:20]}"

    class Meta:
        verbose_name = "Notifikasi"
        verbose_name_plural = "Notifikasi"
        ordering = ['-created_at']

    def mark_as_read(self):
        """Menandai notifikasi sebagai sudah dibaca."""
        self.is_read = True
        self.save(update_fields=['is_read'])

    @classmethod
    def create_stock_low_notification(cls, produk, recipient):
        """Membuat notifikasi stok hampir habis."""
        message = f"Stok untuk produk {produk.nama} hampir habis. Sisa stok: {produk.stok}"
        notification = cls.objects.create(
            recipient=recipient,
            notification_type='STOCK_LOW',
            message=message
        )
        return notification

    @classmethod
    def create_transaction_success_notification(cls, transaksi, recipient):
        """Membuat notifikasi transaksi berhasil."""
        message = f"Transaksi berhasil dengan ID {transaksi.id}. Total: Rp {transaksi.total_harga:,.0f}"
        notification = cls.objects.create(
            recipient=recipient,
            notification_type='TRANSACTION_SUCCESS',
            message=message
        )
        return notification
