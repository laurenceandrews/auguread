# Generated by Django 3.2.10 on 2022-03-21 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0022_auto_20220320_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club_users',
            name='role_num',
            field=models.IntegerField(choices=[('1', 'Applicant'), ('2', 'Member'), ('3', 'Officer'), ('4', 'Owner')], default=1),
        ),
    ]
