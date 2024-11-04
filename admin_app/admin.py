from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Menampilkan kolom-kolom penting di halaman daftar pengguna
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff', 'is_admin_aplikasi')
    list_filter = ('is_active', 'is_staff', 'role', 'is_admin_aplikasi')
    search_fields = ('email', 'full_name')
    ordering = ('email',)

    # Pengaturan tampilan detail pengguna
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_admin_aplikasi')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Pengaturan tampilan untuk menambah pengguna baru di admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_admin_aplikasi'),
        }),
    )

    # Pengaturan untuk menambahkan dan menyimpan pengguna dengan password terenkripsi
    def save_model(self, request, obj, form, change):
        if not change:  # jika pengguna baru dibuat
            obj.set_password(form.cleaned_data["password1"])
        super().save_model(request, obj, form, change)
