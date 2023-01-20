from rest_framework import serializers

from pdapp.models import Category, Dataset, DatasetFile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'hex_code',
        )


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = (
            'id',
            'name',
            'description',
            'category',
        )


class DatasetFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetFile
        fields = (
            'id',
            'name',
            'description',
            'file_csv',
            'dataset',
            'created_by',
            'provider',
            'date_creation',
            'confirmed',
        )