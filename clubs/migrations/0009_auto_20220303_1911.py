# Generated by Django 3.2.10 on 2022-03-03 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0008_book_image_small'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='image_large',
            field=models.ImageField(default='', upload_to=''),
        ),
        migrations.AddField(
            model_name='book',
            name='image_medium',
            field=models.ImageField(default='', upload_to=''),
        ),
    ]
