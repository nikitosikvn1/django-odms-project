import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .validators import validate_csv_file

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    hex_code = models.CharField(max_length=7)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Categories"
    
    def __str__(self) -> str:
        return f"{self.name}"


class Dataset(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(blank=True, max_length=2000)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="datasets")

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Datasets"
    
    def __str__(self) -> str:
        return f"{self.name} : {self.category}"


class DatasetFile(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(blank=True, max_length=2000)
    file_csv = models.FileField(upload_to="csv/", max_length=200, validators=[validate_csv_file])
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="datasetfiles")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="createdfiles")
    provider = models.CharField(max_length=200)
    date_creation = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_creation']
        verbose_name_plural = "DatasetFiles"
    
    def __str__(self) -> str:
        return f"{self.name} : {self.created_by}"


def get_expiration_date():
    return timezone.now() + timedelta(hours=1)

class EmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    confirmation_key = models.UUIDField(default=uuid.uuid4)
    expiration_date = models.DateTimeField(default=get_expiration_date)

    def send_confirmation_mail(self) -> None:
        confirm_url = reverse('confirm-email', args=[str(self.confirmation_key)])
        send_mail(
            'Please confirm your email address - ODMS',
            f'Please visit the following link to verify your email: {confirm_url}',
            'from@odmsmail.com',
            [self.email],
        )
    
    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expiration_date

    def generate_new_confirmation(self) -> None:
        if self.is_expired():
            self.confirmation_key = uuid.uuid4()
            self.expiration_date = get_expiration_date()
            self.save()
            self.send_confirmation_mail()
