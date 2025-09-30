from django.contrib import admin
from product import models as product_models


# Register your models here.
@admin.register(product_models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title","description", "price", "status", "created_at", "updated_at"]
    search_fields = ["title","description"]


@admin.register(product_models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]