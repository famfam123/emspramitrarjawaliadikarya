# Generated by Django 5.1.1 on 2024-10-03 21:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produk_app', '0007_alter_produk_harga_khusus_alter_produk_harga_umum'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kategori',
            options={'ordering': ['nama'], 'verbose_name': 'Kategori', 'verbose_name_plural': 'Kategori'},
        ),
    ]
