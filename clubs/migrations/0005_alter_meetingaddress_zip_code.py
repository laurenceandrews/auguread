# Generated by Django 3.2.10 on 2022-03-02 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0004_auto_20220301_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetingaddress',
            name='zip_code',
            field=models.CharField(blank=True, max_length=12, verbose_name='ZIP / Postal code'),
        ),
    ]