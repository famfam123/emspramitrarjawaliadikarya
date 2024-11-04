from rest_framework import status, generics  # Import generics here
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from .serializers import LoginSerializer, CustomUserSerializer, UserCreateSerializer, ResetPasswordSerializer,SetNewPasswordSerializer
from .models import CustomUser
from rest_framework.permissions import IsAdminUser 
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .permissions import IsAdminAplikasi  # Import izin kustom 
from rest_framework.permissions import IsAuthenticated


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Autentikasi pengguna
        user = authenticate(request=request, email=email, password=password)

        if user is None:
            return Response({'detail': 'Kredensial tidak valid.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Pastikan pengguna aktif
        if not user.is_active:
            return Response({'detail': 'Akun ini tidak aktif.'}, status=status.HTTP_403_FORBIDDEN)

        # Cek role pengguna sesuai dengan endpoint
        if request.path == '/api/login/admin/':
            if user.role.lower() != 'admin' or not user.is_admin_aplikasi:
                return Response({'detail': 'Hanya Admin Aplikasi yang dapat login di sini.'}, status=status.HTTP_403_FORBIDDEN)

        elif request.path == '/api/login/petugas/':
            if user.role.lower() != 'petugas' or not user.is_staff:
                return Response({'detail': 'Hanya Petugas yang dapat login di sini.'}, status=status.HTTP_403_FORBIDDEN)

        # Jika login berhasil, buat token JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)



class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsAdminAplikasi]  # Gunakan izin khusus

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer  
    permission_classes = [IsAuthenticated, IsAdminAplikasi]  # Gunakan izin khusus

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Menyimpan pengguna baru
            return Response({'detail': 'Pengguna baru berhasil dibuat.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserToggleActiveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminAplikasi]  # Gunakan izin khusus

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save()
        serializer = CustomUserSerializer(user)
        return Response({'detail': 'Status pengguna diperbarui.', 'user': serializer.data}, status=status.HTTP_200_OK)

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminAplikasi]  # Gunakan izin khusus

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response({'detail': 'Pengguna berhasil dihapus.'}, status=status.HTTP_204_NO_CONTENT)

class UserResetPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdminAplikasi]  # Gunakan izin khusus

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({'detail': 'Pengguna tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

            send_mail(
                subject='Reset Password',
                message=f'Klik link ini untuk mereset password: {link}',
                from_email='skripsipenting07@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({'detail': 'Link reset password telah dikirim.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None:
            token = request.data.get('token')
            new_password = request.data.get('new_password')
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Password telah berhasil diperbarui.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Token tidak valid atau telah kedaluwarsa.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Pengguna tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)



