# Generated by Django 5.1.1 on 2024-10-03 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produk_app', '0004_stocklog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produk',
            name='harga_khusus',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
