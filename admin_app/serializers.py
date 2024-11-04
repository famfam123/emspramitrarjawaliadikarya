from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator 


User = get_user_model()
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Memastikan email dan password diisi
        if not email or not password:
            raise serializers.ValidationError(_('Must include "email" and "password"'), code='authorization')

        # Autentikasi pengguna
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if user is None:
            raise serializers.ValidationError(_('Invalid login credentials'), code='authorization')

        # Memastikan pengguna aktif
        if not user.is_active:
            raise serializers.ValidationError(_('User is not active.'), code='authorization')

        # Memastikan hanya admin aplikasi yang dapat login
        if user.role == 'admin' and not user.is_admin_aplikasi:
            raise serializers.ValidationError(_('Only application admins can login here.'), code='authorization')

        # Memastikan hanya petugas kasir yang dapat login
        if user.role == 'petugas' and not user.is_staff:
            raise serializers.ValidationError(_('Only kasir staff can login here.'), code='authorization')

        # Menyimpan pengguna ke dalam data
        data['user'] = user
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role', 'is_active']

class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'role', 'password']

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])  # Meng-hash password
        user.save()
        return user

class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'role', 'is_active']  # Hanya field yang bisa diupdate


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'role', 'password']

    def create(self, validated_data):
        # Validasi untuk memastikan admin tidak bisa menambahkan pengguna dengan role admin
        if validated_data['role'] == 'admin':
            raise serializers.ValidationError("Admin tidak dapat ditambahkan sebagai pengguna baru.")
        
        # Validasi password
        validate_password(password=validated_data['password'])
        
        user = CustomUser(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
            is_active=True  # Secara default, pengguna baru diaktifkan
        )
        user.set_password(validated_data['password'])  # Meng-hash password
        user.save()  # Menyimpan pengguna ke database
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Verifies that the email exists in the database.
        """
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Email tidak terdaftar.")
        return value



class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = force_text(urlsafe_base64_decode(attrs['uidb64']))  # Decode uidb64
        try:
            user = CustomUser.objects.get(pk=uid)  # Get user from database
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Pengguna tidak ditemukan.")

        # Validate the token
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Token tidak valid atau telah kedaluwarsa.")

        attrs['user'] = user  # Add user to validated data
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        new_password = validated_data['new_password']
        user.set_password(new_password)  # Set the new password
        user.save()  # Save the user
        return user