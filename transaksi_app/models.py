from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from admin_app.models import CustomUser  # Import custom user
from produk_app.models import Produk
from django.core.exceptions import ValidationError

class Transaksi(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Petugas kasir yang melakukan transaksi
    tanggal = models.DateTimeField(auto_now_add=True)  # Tanggal transaksi
    total_harga = models.DecimalField(max_digits=15, decimal_places=2, editable=False, default=0)  # Total harga transaksi
    metode_pembayaran = models.CharField(max_length=50)  # Metode pembayaran (misal: tunai, transfer, dll.)
    pelanggan = models.CharField(max_length=255, blank=True, null=True)  # Nama pelanggan

    def __str__(self):
        return f"Transaksi #{self.id} oleh {self.user.full_name}"

    def update_total_harga(self):
        """Menghitung dan memperbarui total harga transaksi dari semua item."""
        total = self.items.aggregate(total=Sum(F('harga') * F('jumlah')))['total'] or 0
        self.total_harga = total
        self.save(update_fields=['total_harga'])  # Update hanya field total_harga

    def save(self, *args, **kwargs):
        """Override save untuk menghitung total_harga jika baru."""
        is_new = self._state.adding  # Check if it's a new instance
        super().save(*args, **kwargs)
        if is_new:
            self.update_total_harga()  # Only update total_harga if instance is newly created

    def buat_invoice(self):
        """Membuat invoice dari transaksi ini."""
        if hasattr(self, 'invoice'):
            raise ValueError("Invoice sudah dibuat untuk transaksi ini.")
        
        # Buat nomor invoice unik (misalnya, bisa menggunakan ID transaksi)
        nomor_invoice = f"INV-{self.id}-{timezone.now().strftime('%Y%m%d')}"

        # Buat invoice
        invoice = Invoice.objects.create(
            transaksi=self,
            nomor_invoice=nomor_invoice,
            total_harga=self.total_harga,
            pelanggan=self.pelanggan
        )

        # Buat item invoice dari item transaksi
        for item in self.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                transaksi_item=item,
                jumlah=item.jumlah
            )

        return invoice

    @classmethod
    def get_today_summary(cls, user):
        """Mengambil ringkasan transaksi untuk user pada hari ini."""
        today = timezone.now().date()

        # Filter transaksi yang dilakukan oleh user pada hari ini
        transaksi_hari_ini = cls.objects.filter(user=user, tanggal__date=today)

        # Hitung jumlah transaksi dan total pendapatan
        jumlah_transaksi = transaksi_hari_ini.count()
        total_pendapatan = transaksi_hari_ini.aggregate(Sum('total_harga'))['total_harga__sum'] or 0

        return jumlah_transaksi, total_pendapatan


class TransaksiItem(models.Model):
    transaksi = models.ForeignKey(Transaksi, related_name='items', on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah = models.PositiveIntegerField()

    TIPE_HARGA_CHOICES = [
        ('harga_khusus', 'Harga Khusus'),
        ('harga_umum', 'Harga Umum'),
    ]
    
    tipe_harga = models.CharField(max_length=20, choices=TIPE_HARGA_CHOICES, default='harga_umum')
    harga = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def get_harga(self):
        """Mengambil harga produk berdasarkan tipe_harga."""
        return self.produk.harga_khusus if self.tipe_harga == 'harga_khusus' else self.produk.harga_umum

    def subtotal(self):
        """Menghitung subtotal untuk item ini."""
        return self.jumlah * self.get_harga()

    def __str__(self):
        return f"{self.jumlah} x {self.produk.nama} ({self.get_harga()})"

    def save(self, *args, **kwargs):
        """Simpan item transaksi dan update harga."""
        self.harga = self.get_harga()
        super().save(*args, **kwargs)
        self.transaksi.update_total_harga()  # Update total_harga di transaksi


class CartItem(models.Model):
    petugas = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah = models.PositiveIntegerField(default=1)
    tipe_harga = models.CharField(max_length=20, choices=[
        ('harga_umum', 'Harga Umum'),
        ('harga_khusus', 'Harga Khusus')
    ])

    def subtotal(self):
        """Menghitung subtotal berdasarkan tipe_harga."""
        harga = self.produk.harga_khusus if self.tipe_harga == 'harga_khusus' else self.produk.harga_umum
        return harga * self.jumlah

    def __str__(self):
        return f"{self.jumlah} x {self.produk.nama}"


class Invoice(models.Model):
    transaksi = models.OneToOneField('Transaksi', on_delete=models.CASCADE, related_name='invoice')
    nomor_invoice = models.CharField(max_length=50, unique=True)
    tanggal_invoice = models.DateTimeField(auto_now_add=True)
    total_harga = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Set default ke 0
    pelanggan = models.CharField(max_length=255)
    
    # Pilihan untuk status pembayaran
    STATUS_CHOICES = [
        ('Belum Dibayar', 'Belum Dibayar'),
        ('Sudah Dibayar', 'Sudah Dibayar'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Belum Dibayar')

    def __str__(self):
        return f"Invoice #{self.nomor_invoice} untuk {self.pelanggan}"

    def total_invoice(self):
        """Menghitung total dari semua item dalam invoice."""
        return sum(item.subtotal() for item in self.items.all())

class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', related_name='items', on_delete=models.CASCADE)
    cart_item = models.ForeignKey('CartItem', on_delete=models.CASCADE, default=1)
    jumlah = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item Invoice'
        verbose_name_plural = 'Item Invoice'

    def subtotal(self):
        """Menghitung subtotal berdasarkan jumlah dan harga per item di CartItem."""
        harga = self.cart_item.produk.harga_khusus if self.cart_item.tipe_harga == 'harga_khusus' else self.cart_item.produk.harga_umum
        return self.jumlah * harga

    def clean(self):
        """Validasi untuk memastikan jumlah lebih besar dari nol."""
        if self.jumlah <= 0:
            raise ValidationError('Jumlah harus lebih besar dari nol.')

    def __str__(self):
        return f"{self.jumlah} x {self.cart_item.produk.nama} - Invoice #{self.invoice.nomor_invoice}"
