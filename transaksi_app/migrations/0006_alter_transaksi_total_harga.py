# Generated by Django 5.1.1 on 2024-10-27 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaksi_app', '0005_alter_transaksi_total_harga'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaksi',
            name='total_harga',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=15),
        ),
    ]
