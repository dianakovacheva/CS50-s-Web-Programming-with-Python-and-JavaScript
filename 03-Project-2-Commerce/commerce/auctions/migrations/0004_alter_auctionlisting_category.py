# Generated by Django 5.1.1 on 2024-10-10 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_remove_auctionlisting_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='category',
            field=models.ManyToManyField(help_text='Select a category', related_name='auction_categories', to='auctions.auctioncategory'),
        ),
    ]