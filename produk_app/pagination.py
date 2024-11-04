from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # Ukuran halaman default
    page_size_query_param = 'page_size'  # Mengizinkan klien untuk mengatur ukuran halaman menggunakan parameter query
    max_page_size = 100  # Batas maksimum ukuran halaman
