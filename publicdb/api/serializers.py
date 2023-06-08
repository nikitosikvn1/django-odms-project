from rest_framework import serializers
import csv

from pdapp.models import Category, Dataset, DatasetFile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'hex_code',)


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ('id', 'name', 'description', 'category',)


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


class DatasetFileToJsonSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()

    class Meta:
        model = DatasetFile
        fields = ('id', 'name', 'description', 'provider', 'labels', 'values',)

    def get_labels(self, obj):
        return self._get_row_from_csv(obj.file_csv, 0)

    def get_values(self, obj):
        return self._get_row_from_csv(obj.file_csv, 1)

    def _get_row_from_csv(self, file, row_index):
        file.open(mode='r')
        reader = csv.reader(file)
        try:
            row = next(row for idx, row in enumerate(reader) if idx == row_index)
        except StopIteration:
            row = []
        file.close()
        return row