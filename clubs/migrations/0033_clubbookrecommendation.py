# Generated by Django 3.2.10 on 2022-03-31 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0032_alter_postcomment_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubBookRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.book')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
            options={
                'verbose_name': 'Club Book Recommendation',
                'verbose_name_plural': 'Club Book Recommendations',
            },
        ),
    ]
