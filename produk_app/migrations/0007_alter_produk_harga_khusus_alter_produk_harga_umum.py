# Generated by Django 5.1.1 on 2024-10-03 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produk_app', '0006_alter_produk_harga_khusus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produk',
            name='harga_khusus',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='produk',
            name='harga_umum',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]
