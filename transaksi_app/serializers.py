from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from .models import Transaksi, TransaksiItem, CartItem
from produk_app.models import Produk
from admin_app.models import CustomUser
from .models import InvoiceItem, Invoice


class TransaksiItemSerializer(serializers.ModelSerializer):
    kode_produk = serializers.SerializerMethodField()
    jumlah = serializers.IntegerField()
    tipe_harga = serializers.ChoiceField(choices=[('harga_umum', 'Harga Umum'), ('harga_khusus', 'Harga Khusus')])
    nama_produk = serializers.SerializerMethodField()

    class Meta:
        model = TransaksiItem
        fields = ['kode_produk', 'jumlah', 'tipe_harga', 'nama_produk']

    def get_kode_produk(self, obj):
        """Retrieve kode from the related Produk model."""
        return obj.produk.kode

    def get_nama_produk(self, obj):
        return obj.produk.nama


class TransaksiSerializer(serializers.ModelSerializer):
    items = TransaksiItemSerializer(many=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Transaksi
        fields = ['id', 'user', 'total_harga', 'tanggal', 'items']
        read_only_fields = ['id', 'total_harga', 'tanggal']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        
        transaksi = Transaksi.objects.create(user=user, total_harga=0)

        total_harga = 0
        transaksi_items = []
        produk_list = []

        for item_data in items_data:
            produk = Produk.objects.get(id=item_data.get('produk').id)  
            jumlah = item_data.get('jumlah')
            tipe_harga = item_data.get('tipe_harga')

           
            if produk.stok < jumlah:
                raise serializers.ValidationError(f'Stok produk "{produk.nama}" tidak mencukupi. Stok saat ini: {produk.stok}')

            
            harga = produk.harga_khusus if tipe_harga == 'harga_khusus' else produk.harga_umum
            total_harga += harga * jumlah

            
            produk.stok = F('stok') - jumlah
            produk_list.append(produk)

            
            transaksi_item = TransaksiItem(
                transaksi=transaksi,
                produk=produk,
                jumlah=jumlah,
                tipe_harga=tipe_harga,
                harga=harga
            )
            transaksi_items.append(transaksi_item)

        Produk.objects.bulk_update(produk_list, ['stok'])

        
        TransaksiItem.objects.bulk_create(transaksi_items)

        
        transaksi.total_harga = total_harga
        transaksi.save()

        return transaksi


class CartItemSerializer(serializers.ModelSerializer):
    produk_detail = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    tipe_harga_keterangan = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'produk', 'produk_detail', 'jumlah', 'tipe_harga', 'subtotal', 'tipe_harga_keterangan']

    def get_produk_detail(self, obj):
        harga = obj.produk.harga_khusus if obj.tipe_harga == 'harga_khusus' else obj.produk.harga_umum
        return {
            'kode': obj.produk.kode,
            'nama': obj.produk.nama,
            'harga': harga
        }

    def get_subtotal(self, obj):
        return obj.subtotal()

    def get_tipe_harga_keterangan(self, obj):
        return "Harga Khusus" if obj.tipe_harga == 'harga_khusus' else "Harga Umum"


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['cart_item', 'jumlah', 'subtotal']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['nomor_invoice', 'tanggal_invoice', 'total_harga', 'pelanggan', 'status', 'items']
        read_only_fields = ['tanggal_invoice', 'total_harga']  # Total harga dan tanggal dibuat tidak bisa diubah

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Ambil data item dari validated_data
        invoice = Invoice.objects.create(**validated_data)  # Buat objek Invoice

        # Buat objek InvoiceItem berdasarkan data yang ada
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)  

        # Update field di Invoice
        instance.nomor_invoice = validated_data.get('nomor_invoice', instance.nomor_invoice)
        instance.pelanggan = validated_data.get('pelanggan', instance.pelanggan)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Jika ada data item, update atau buat item baru
        if items_data is not None:
            # Hapus semua item lama
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)

        return instance


