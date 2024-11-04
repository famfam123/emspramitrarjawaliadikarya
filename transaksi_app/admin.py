from django.contrib import admin
from .models import InvoiceItem

class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'cart_item', 'jumlah', 'subtotal')  # Ubah transaksi_item ke cart_item

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'  # Memberikan nama kolom di admin

admin.site.register(InvoiceItem, InvoiceItemAdmin)
