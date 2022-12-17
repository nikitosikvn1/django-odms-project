from django.db import models
from django.contrib.auth.models import User
from .validators import validate_csv_file
from django.utils import timezone

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
    date_creation = models.DateTimeField(default=timezone.now())
    confirmed = models.BooleanField(default=False)