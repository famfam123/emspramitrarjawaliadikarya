from rest_framework import serializers
from transaksi_app.models import Transaksi, TransaksiItem  
from produk_app.models import Produk
from .models import Notification 

class TransaksiItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaksiItem
        fields = ['id', 'produk', 'jumlah', 'tipe_harga', 'subtotal']

    subtotal = serializers.SerializerMethodField()

    def get_subtotal(self, obj):
        """Menghitung subtotal untuk item ini."""
        return obj.subtotal()

class TransaksiSerializer(serializers.ModelSerializer):
    items = TransaksiItemSerializer(many=True)

    class Meta:
        model = Transaksi
        fields = ['id', 'user', 'tanggal', 'total_harga', 'metode_pembayaran', 'pelanggan', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        transaksi = Transaksi.objects.create(**validated_data)
        for item_data in items_data:
            TransaksiItem.objects.create(transaksi=transaksi, **item_data)
        transaksi.update_total_harga()  # Update total harga setelah menambahkan item
        return transaksi

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance.metode_pembayaran = validated_data.get('metode_pembayaran', instance.metode_pembayaran)
        instance.pelanggan = validated_data.get('pelanggan', instance.pelanggan)
        instance.save()

        # Mengupdate item transaksi
        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id:
                item = TransaksiItem.objects.get(id=item_id, transaksi=instance)
                item.jumlah = item_data.get('jumlah', item.jumlah)
                item.tipe_harga = item_data.get('tipe_harga', item.tipe_harga)
                item.save()
            else:
                TransaksiItem.objects.create(transaksi=instance, **item_data)

        instance.update_total_harga()  # Update total harga setelah mengubah item
        return instance





class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'recipient_username',  # Optional: to show the recipient's username
            'notification_type',
            'notification_type_display',  # Optional: to show readable notification type
            'message',
            'is_read',
            'created_at'
        ]
        read_only_fields = ['created_at', 'notification_type_display', 'recipient_username']

    def update(self, instance, validated_data):
        """Overrides the default update method to handle 'mark as read' functionality."""
        is_read = validated_data.get('is_read', None)
        if is_read is not None:
            instance.is_read = is_read
            instance.save(update_fields=['is_read'])
        return instance