# Generated by Django 5.1.1 on 2024-10-10 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_rename_auctioncategories_auctioncategory_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuctionCategory',
            new_name='Category',
        ),
        migrations.RenameModel(
            old_name='AuctionListing',
            new_name='Listing',
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
    ]
