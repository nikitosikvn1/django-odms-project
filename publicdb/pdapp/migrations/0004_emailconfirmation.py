# Generated by Django 4.2 on 2023-06-11 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pdapp.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pdapp', '0003_alter_datasetfile_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('confirmation_key', models.UUIDField(default=uuid.uuid4)),
                ('expiration_date', models.DateTimeField(default=pdapp.models.get_expiration_date)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]