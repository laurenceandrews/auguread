# Generated by Django 3.2.10 on 2022-03-03 14:14

import uuid

import clubs.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist of @ followed by at least three alphanumericals', regex='^@\\w{3,}$')])),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('age', models.PositiveIntegerField(default=18, validators=[django.core.validators.MaxValueValidator(105), django.core.validators.MinValueValidator(5)])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('bio', models.CharField(blank=True, max_length=520)),
                ('city', models.CharField(max_length=50)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
            },
            managers=[
                ('objects', clubs.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ApplicantMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISBN', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=250)),
                ('author', models.CharField(max_length=300)),
                ('publisher', models.CharField(max_length=300)),
                ('publication_year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('location', models.CharField(max_length=500)),
                ('description', models.CharField(max_length=520)),
                ('avg_reading_speed', models.IntegerField(default=200, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(500)])),
                ('applicants', models.ManyToManyField(blank=True, related_name='applicant', through='clubs.ApplicantMembership', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MyUUIDModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='User_Books',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='clubs.book')),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=280)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OwnerMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Club_Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_num', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)])),
                ('club', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Club_Books',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='clubs.book')),
                ('club', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
        ),
        migrations.AddField(
            model_name='club',
            name='books',
            field=models.ManyToManyField(blank=True, related_name='book', through='clubs.Club_Books', to='clubs.Book'),
        ),
        migrations.AddField(
            model_name='club',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='member', through='clubs.Club_Users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='club',
            name='owner',
            field=models.ForeignKey(blank=b'I00\n', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='club',
            name='owners',
            field=models.ManyToManyField(blank=True, related_name='owner', through='clubs.OwnerMembership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='applicantmembership',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club'),
        ),
        migrations.AddField(
            model_name='applicantmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
