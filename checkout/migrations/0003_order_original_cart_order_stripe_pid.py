# Generated by Django 4.2.5 on 2025-04-10 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_alter_orderlineitem_stock_colour_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='original_cart',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='stripe_pid',
            field=models.CharField(default='', max_length=254),
        ),
    ]
