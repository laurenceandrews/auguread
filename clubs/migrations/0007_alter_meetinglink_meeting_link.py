# Generated by Django 3.2.10 on 2022-03-02 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0006_alter_meetingaddress_address2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetinglink',
            name='meeting_link',
            field=models.URLField(),
        ),
    ]
