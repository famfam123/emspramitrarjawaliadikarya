# Generated by Django 5.1.1 on 2024-10-01 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produk_app', '0002_rename_harga_beli_produk_harga_khusus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='produk',
            name='barcode',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
