# Generated by Django 4.1.3 on 2022-12-17 19:46

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pdapp.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('hex_code', models.CharField(max_length=7)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=2000)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='datasets', to='pdapp.category')),
            ],
            options={
                'verbose_name_plural': 'Datasets',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='DatasetFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=2000)),
                ('file_csv', models.FileField(max_length=200, upload_to='csv/', validators=[pdapp.validators.validate_csv_file])),
                ('provider', models.CharField(max_length=200)),
                ('date_creation', models.DateTimeField(default=datetime.datetime(2022, 12, 17, 19, 46, 40, 873946, tzinfo=datetime.timezone.utc))),
                ('confirmed', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='createdfiles', to=settings.AUTH_USER_MODEL)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasetfiles', to='pdapp.dataset')),
            ],
        ),
    ]
