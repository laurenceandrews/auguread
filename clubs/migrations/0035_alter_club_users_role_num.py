# Generated by Django 3.2.10 on 2022-04-03 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0034_userbookrecommendation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club_users',
            name='role_num',
            field=models.CharField(choices=[('1', 'Applicant'), ('2', 'Member'), ('4', 'Owner')], default=1, max_length=1),
        ),
    ]