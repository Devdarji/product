from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def get_details(self):
        return {
            "name": self.name
        }

class Product(models.Model):
    category_id = models.ForeignKey(
        Category,
        related_name='product_category',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def get_details(self):
        return {
            "category": self.category_id.name,
            "title": self.title,
            "price": self.price,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

