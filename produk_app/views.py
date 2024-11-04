from rest_framework import generics, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import ProdukSerializer, StockLogSerializer
from .models import Produk, StockLog
from admin_app.permissions import IsAdminAplikasi  # Import custom permission
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# List & Create Produk
class ProdukListView(generics.ListCreateAPIView):
    queryset = Produk.objects.all()
    serializer_class = ProdukSerializer
    permission_classes = [IsAuthenticated]  # Allow any authenticated user

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['kategori']
    search_fields = ['nama', 'kode']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if self.is_produk_exists(serializer.validated_data['kode']):
                return Response({'detail': 'Kode produk sudah ada.'}, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def is_produk_exists(self, kode):
        return Produk.objects.filter(kode=kode).exists()

# Detail Produk (Retrieve, Update & Destroy)
class ProdukDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Produk.objects.all()
    serializer_class = ProdukSerializer
    permission_classes = [IsAuthenticated]  # Allow any authenticated user
    lookup_field = 'kode'  # Use 'kode' as lookup field

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.validate_stock_and_price(serializer)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def validate_stock_and_price(self, serializer):
        stok = serializer.validated_data.get('stok', 0)
        harga_khusus = serializer.validated_data.get('harga_khusus', 0)
        harga_umum = serializer.validated_data.get('harga_umum', 0)

        if stok < 0:
            raise serializers.ValidationError("Stok tidak boleh negatif.")
        if harga_khusus < 0:
            raise serializers.ValidationError("Harga khusus tidak boleh negatif.")
        if harga_umum < 0:
            raise serializers.ValidationError("Harga umum tidak boleh negatif.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Produk berhasil dihapus.'}, status=status.HTTP_200_OK)

# List & Create StockLog
class StockLogListView(generics.ListCreateAPIView):
    queryset = StockLog.objects.all()
    serializer_class = StockLogSerializer
    permission_classes = [IsAuthenticated]  # Allow any authenticated user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Detail StockLog (Retrieve, Update & Destroy)
class StockLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockLog.objects.all()
    serializer_class = StockLogSerializer
    permission_classes = [IsAuthenticated]  # Allow any authenticated user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            produk = instance.produk
            perubahan = serializer.validated_data.get('perubahan', instance.perubahan)
            new_stok = produk.stok + perubahan - instance.perubahan

            if new_stok < 0:
                return Response({'detail': 'Stok tidak dapat negatif setelah update.'}, status=status.HTTP_400_BAD_REQUEST)

            produk.stok = new_stok
            produk.save()
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print("Deleting StockLog with ID:", kwargs.get('pk'))  # Log ID being deleted
        self.perform_destroy(instance)
        return Response({'detail': 'StockLog berhasil dihapus.'}, status=status.HTTP_200_OK)

# Search Produk
class SearchProdukView(APIView):
    def get(self, request):
        kode_barang = request.query_params.get('kode_barang', None)
        barcode = request.query_params.get('barcode', None)

        # Validate input
        if not kode_barang and not barcode:
            return Response({"error": "Kode barang atau barcode harus disediakan."}, status=status.HTTP_400_BAD_REQUEST)
        if kode_barang and barcode:
            return Response({"error": "Hanya satu dari kode barang atau barcode yang dapat disediakan."}, status=status.HTTP_400_BAD_REQUEST)

        # Search by kode_barang
        if kode_barang:
            try:
                produk = Produk.objects.get(kode=kode_barang)
            except Produk.DoesNotExist:
                return Response({"error": "Produk tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        # Search by barcode
        elif barcode:
            try:
                produk = Produk.objects.get(barcode=barcode)
            except Produk.DoesNotExist:
                return Response({"error": "Produk tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProdukSerializer(produk)
        return Response(serializer.data, status=status.HTTP_200_OK)
