# Generated by Django 5.1.1 on 2024-10-01 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produk_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='produk',
            old_name='harga_beli',
            new_name='harga_khusus',
        ),
        migrations.RenameField(
            model_name='produk',
            old_name='harga_jual',
            new_name='harga_umum',
        ),
    ]