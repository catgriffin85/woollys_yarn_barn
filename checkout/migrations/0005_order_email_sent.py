# Generated by Django 4.2.5 on 2025-04-20 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0004_order_user_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
    ]
