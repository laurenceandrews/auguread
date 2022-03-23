# Generated by Django 3.2.10 on 2022-03-21 23:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0024_auto_20220321_1427'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Book_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='clubs.book')),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]