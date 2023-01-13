from django.contrib import admin
from .models import Category, Dataset, DatasetFile

# Register your models here.

# Inline configs
class DatasetInline(admin.TabularInline):
    model = Dataset
    can_delete = False
    extra = 0

class DatasetFileInline(admin.TabularInline):
    model = DatasetFile
    can_delete = False
    extra = 0

# Basic configs
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

    inlines = [
        DatasetInline,
    ]

class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "category",)
    list_filter = ("category",)
    search_fields = ("name",)

    inlines = [
        DatasetFileInline,
    ]

class DatasetFileAdmin(admin.ModelAdmin):
    list_display = ("name", "dataset", "provider", "created_by",)
    list_filter = ("dataset", "created_by", "confirmed",)
    search_fields = ("name", "description", "provider",)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetFile, DatasetFileAdmin)