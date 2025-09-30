import random

from simprosys.celery import app
from faker import Faker
from product import models as product_models

@app.task
def task_one():
    print(" task one called and worker is running good")
    return "success"

@app.task
def task_two(data, *args, **kwargs):
    print(f" task two called with the argument {data} and worker is running good")
    return "success"

@app.task
def bulk_create_product(number):
    fake = Faker()
    product_instances = []

    for _ in range(number):
        category_instance = product_models.Category.objects.create(
            name=fake.name()
        )

        product_instances.append(product_models.Product(
            category_id=category_instance,
            title=fake.address(),
            description=fake.paragraph(),
            price=random.uniform(100, 10000)
        ))

    product_models.Product.objects.bulk_create(
        product_instances
    )

    print("Product Instances created successfully")
    