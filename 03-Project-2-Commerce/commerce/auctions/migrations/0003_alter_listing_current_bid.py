# Generated by Django 5.1.1 on 2024-10-29 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_listing_current_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='current_bid',
            field=models.DecimalField(decimal_places=2, default=models.DecimalField(decimal_places=2, max_digits=10), max_digits=10),
        ),
    ]
