from rest_framework import serializers


class CreateProductSerializer(serializers.Serializer):
    category = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    status = serializers.BooleanField(default=True)

class UpdateProductSerializer(serializers.Serializer):
    category = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    status = serializers.BooleanField(default=False)


class CreateCategorySerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    

class BulkCreateSerializer(serializers.Serializer):
    number = serializers.IntegerField()