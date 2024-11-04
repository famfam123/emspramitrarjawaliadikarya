# admin_app/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a 'CustomUser' with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)  # Normalisasi email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Set password yang di-hash
        user.save(using=self._db)  # Simpan ke database
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with 'is_staff' and 'is_superuser' set to True.
        """
        extra_fields.setdefault('is_staff', True)  # Superuser harus bisa mengakses admin
        extra_fields.setdefault('is_superuser', True)  # Superuser memiliki hak istimewa penuh

        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin Aplikasi'),
        ('petugas', 'Petugas Kasir'),
    )
    
    email = models.EmailField(unique=True)  # Email harus unik
    full_name = models.CharField(max_length=255)  # Nama lengkap pengguna
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # Peran pengguna
    is_active = models.BooleanField(default=True)  # Status aktif pengguna
    is_staff = models.BooleanField(default=False)  # Untuk akses admin Django
    is_admin_aplikasi = models.BooleanField(default=False)  # Menandakan admin aplikasi

    objects = CustomUserManager()  # Menggunakan custom user manager

    USERNAME_FIELD = 'email'  # Field yang digunakan untuk login
    REQUIRED_FIELDS = ['full_name', 'role']  # Field tambahan yang diperlukan saat membuat user

    def __str__(self):
        return self.email  # Representasi string dari objek pengguna
