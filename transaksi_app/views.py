from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import CartItem, Transaksi, TransaksiItem
from .serializers import CartItemSerializer, TransaksiSerializer
from produk_app.models import Produk
from django.http import JsonResponse
from django.views import View
from .models import Invoice  
from .serializers import InvoiceSerializer  #
import logging
from django.utils import timezone
from django.db import IntegrityError
logger = logging.getLogger(__name__)
from rest_framework import serializers

class TransaksiListCreateView(generics.ListCreateAPIView):
    serializer_class = TransaksiSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Mengambil daftar transaksi sesuai dengan role user.
        - Jika 'petugas', hanya transaksi yang dibuat oleh user tersebut.
        - Jika 'admin', semua transaksi ditampilkan.
        """
        user = self.request.user
        if user.role == 'petugas':
            return Transaksi.objects.filter(user=user)  
        return Transaksi.objects.all()  

    def get(self, request, *args, **kwargs):
        """
        Mengambil daftar transaksi.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Membuat transaksi baru.
        """
        # Hanya 'petugas' yang dapat membuat transaksi
        if request.user.role != 'petugas':
            return Response({'detail': 'Anda tidak memiliki izin untuk membuat transaksi.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # Menetapkan user yang membuat transaksi
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        petugas = request.user
        kode_produk = request.data.get('kode_produk')
        jumlah = request.data.get('jumlah', 1)
        tipe_harga = request.data.get('tipe_harga')

        try:
            produk = Produk.objects.get(kode=kode_produk)
        except Produk.DoesNotExist:
            logger.error(f"User {petugas} mencoba menambahkan produk dengan kode {kode_produk} yang tidak ditemukan.")
            return Response({"error": "Produk tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

        harga = produk.harga_khusus if tipe_harga == 'khusus' else produk.harga_umum

        cart_item, created = CartItem.objects.get_or_create(
            petugas=petugas,
            produk=produk,
            defaults={'jumlah': jumlah, 'tipe_harga': tipe_harga}
        )

        if not created:
            cart_item.jumlah += jumlah
            cart_item.save()
            logger.info(f"User {petugas} menambahkan produk {produk.nama} ke keranjang. Jumlah baru: {cart_item.jumlah}.")
        else:
            logger.info(f"User {petugas} membuat item baru di keranjang: {produk.nama} dengan jumlah {jumlah}.")

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        petugas = request.user
        cart_items = CartItem.objects.filter(petugas=petugas)
        serializer = CartItemSerializer(cart_items, many=True)
        total_harga = sum(item.subtotal() for item in cart_items)

        # Cek ketersediaan stok
        unavailable_items = []
        for item in cart_items:
            if item.jumlah > item.produk.stok:
                unavailable_items.append(item.produk.nama)

        return Response({
            'items': serializer.data,
            'total_harga': total_harga,
            'unavailable_items': unavailable_items  # Daftar item yang tidak tersedia
        })


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        petugas = request.user
        cart_items = CartItem.objects.filter(petugas=petugas)

        if not cart_items.exists():
            logger.warning(f"User {petugas} mencoba checkout dengan keranjang kosong.")
            return Response({"error": "Keranjang kosong."}, status=status.HTTP_400_BAD_REQUEST)

        pelanggan = request.data.get('pelanggan')
        if not pelanggan:
            logger.error(f"User {petugas} melakukan checkout tanpa nama pelanggan.")
            return Response({"error": "Nama pelanggan wajib diisi."}, status=status.HTTP_400_BAD_REQUEST)

        total_harga = sum(item.subtotal() for item in cart_items)

        try:
            # Cek ketersediaan stok
            for item in cart_items:
                if item.jumlah > item.produk.stok:
                    logger.error(f"Stok tidak cukup untuk produk {item.produk.nama}. Permintaan: {item.jumlah}, Stok: {item.produk.stok}")
                    return Response({"error": f"Stok tidak cukup untuk produk {item.produk.nama}."}, status=status.HTTP_400_BAD_REQUEST)

            # Buat transaksi
            transaksi = Transaksi.objects.create(user=petugas, total_harga=total_harga, pelanggan=pelanggan)

            items = []  # Untuk menyimpan data produk yang dibeli
            for item in cart_items:
                # Pastikan produk ada
                if not item.produk:
                    logger.error(f"Produk dengan ID {item.produk.id} tidak ditemukan saat checkout.")
                    return Response({"error": f"Produk dengan ID {item.produk.id} tidak ditemukan."}, status=status.HTTP_400_BAD_REQUEST)

                # Buat item transaksi
                TransaksiItem.objects.create(transaksi=transaksi, produk=item.produk, jumlah=item.jumlah, tipe_harga=item.tipe_harga)

                # Kurangi stok produk
                item.produk.stok -= item.jumlah
                item.produk.save()

                # Tambahkan item ke dalam list untuk response
                items.append({
                    "cart_item": item.id,
                    "jumlah": item.jumlah,
                })

            logger.info(f"User {petugas} berhasil melakukan checkout dengan ID transaksi {transaksi.id}.")

            # Hapus item keranjang
            cart_items.delete()

            # Serialize transaksi untuk dikembalikan dalam response
            transaksi_serializer = TransaksiSerializer(transaksi)

            return Response({
                "message": "Checkout berhasil",
                "transaksi": transaksi_serializer.data,
                "items": items  # Kembalikan daftar item yang dibeli
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Kesalahan database saat checkout oleh user {petugas}: {str(e)}")
            return Response({"error": "Terjadi kesalahan pada database. Silakan coba lagi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Kesalahan tidak terduga saat checkout oleh user {petugas}: {str(e)}")
            return Response({"error": "Terjadi kesalahan yang tidak terduga. Silakan coba lagi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LatestUserTransactionsView(generics.ListAPIView):
    serializer_class = TransaksiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter transaksi berdasarkan user yang sedang login, batasi ke 10 transaksi terbaru
        return Transaksi.objects.filter(user=self.request.user).order_by('-tanggal')[:10]


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        petugas = request.user
        CartItem.objects.filter(petugas=petugas).delete()
        
        # Logging pengosongan keranjang
        logger.info(f"User {petugas} telah mengosongkan keranjang.")
        return Response({"message": "Keranjang berhasil dikosongkan"}, status=status.HTTP_200_OK)
    
class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cart_item_id):
        petugas = request.user
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, petugas=petugas)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item tidak ditemukan di keranjang."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, cart_item_id):
        petugas = request.user
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, petugas=petugas)
            cart_item.delete()  # Menghapus item dari keranjang
            return Response({"message": "Item berhasil dihapus dari keranjang."}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Item tidak ditemukan di keranjang."}, status=status.HTTP_404_NOT_FOUND)
        

        
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, cart_item_id):
        petugas = request.user
        jumlah = request.data.get('jumlah')

        try:
            cart_item = CartItem.objects.get(id=cart_item_id, petugas=petugas)
            if jumlah <= 0:
                cart_item.delete()
                return Response({"message": "Item dihapus dari keranjang"}, status=status.HTTP_204_NO_CONTENT)
            
            cart_item.jumlah = jumlah
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item tidak ditemukan di keranjang."}, status=status.HTTP_404_NOT_FOUND)
        

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        """Menghapus item dari keranjang berdasarkan item_id."""
        try:
            item = CartItem.objects.get(id=item_id)
            item.delete()
            return Response({"detail": "Item berhasil dihapus dari keranjang"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Mengambil daftar invoice sesuai dengan role user.
        - Jika 'petugas', hanya invoice yang terkait dengan transaksi yang dibuat oleh user tersebut.
        - Jika 'admin', semua invoice ditampilkan.
        """
        user = self.request.user
        if user.role == 'petugas':
            return Invoice.objects.filter(transaksi__user=user)  # Hanya invoice dari transaksi petugas tersebut
        return Invoice.objects.all()  # Admin dapat melihat semua invoice

    def post(self, request, *args, **kwargs):
        """
        Membuat invoice baru.
        """
        # Hanya 'petugas' yang dapat membuat invoice
        if request.user.role != 'petugas':
            return Response({'detail': 'Anda tidak memiliki izin untuk membuat invoice.'}, status=status.HTTP_403_FORBIDDEN)

        # Memanggil serializer untuk memvalidasi dan menyimpan data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Menyimpan invoice yang valid
        invoice = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)