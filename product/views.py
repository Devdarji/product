import pandas as pd
from io import BytesIO

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from product import renderers as product_render
from product import serializers as product_serializer
from product import models as product_models
from product import tasks as product_tasks

from django.http import HttpResponse


class CreateProductView(APIView):
    """Handle product creation and listing"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        """Create a new product"""
        serializer_instance = product_serializer.CreateProductSerializer(
            data=request.data
        )

        if not serializer_instance.is_valid():
            return Response(
                f"Please Enter Valid Data {str(serializer_instance.errors)}", status=400
            )

        # Validate category exists
        category_instance = product_models.Category.objects.filter(
            name=serializer_instance.validated_data.get("category")
        ).last()

        if not category_instance:
            return Response("Category is not available", status=404)

        # Replace category name with category instance
        serializer_instance.validated_data.pop("category")
        serializer_instance.validated_data.update({"category_id": category_instance})

        product_instance = product_models.Product.objects.create(
            **serializer_instance.validated_data
        )

        return Response(data=product_instance.get_details(), status=200)

    @staticmethod
    def get(request):
        """Get all products with category details"""
        product_instances = product_models.Product.objects.select_related(
            "category_id"
        ).all()

        return Response(
            data=[product.get_details() for product in product_instances], status=200
        )


class UpdateProductView(APIView):
    """Handle product updates, deletion, and individual product retrieval"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [product_render.CustomAesRenderer]

    @staticmethod
    def put(request, id):
        """Update product details"""
        product_instance = product_models.Product.objects.filter(id=id).last()

        if not product_instance:
            return Response("Product is not available", status=404)

        serializer_instance = product_serializer.UpdateProductSerializer(
            data=request.data
        )

        if not serializer_instance.is_valid():
            return Response(
                f"Please Enter Valid Data {str(serializer_instance.errors)}", status=400
            )

        # Update category if provided
        if serializer_instance.validated_data.get("category"):
            category_instance = product_models.Category.objects.filter(
                name=serializer_instance.validated_data.get("category")
            ).last()

            if not category_instance:
                return Response("Category is not available", status=404)

            product_instance.category_id = category_instance

        # Update other fields if provided
        if serializer_instance.validated_data.get("title"):
            product_instance.title = serializer_instance.validated_data.get("title")

        if serializer_instance.validated_data.get("description"):
            product_instance.description = serializer_instance.validated_data.get(
                "description"
            )

        if serializer_instance.validated_data.get("price"):
            product_instance.price = serializer_instance.validated_data.get("price")

        prev_status = product_instance.status

        if serializer_instance.validated_data.get("status") != prev_status:
            product_instance.status = serializer_instance.validated_data.get("status")

        product_instance.save(
            update_fields=[
                "category_id",
                "title",
                "description",
                "price",
                "status",
            ]
        )

        return Response(data=product_instance.get_details(), status=200)

    @staticmethod
    def delete(request, id):
        """Soft delete product by setting status to False"""
        product_instance = product_models.Product.objects.filter(id=id).last()

        if not product_instance:
            return Response("Product is not available", status=404)

        product_instance.status = False
        product_instance.save(update_fields=["status"])

        return Response(data="Product Deleted successfully!!", status=200)

    @staticmethod
    def get(request, id):
        """Get single product details"""
        product_instance = product_models.Product.objects.filter(id=id).last()

        if not product_instance:
            return Response("Product is not available", status=404)

        return Response(data=product_instance.get_details(), status=200)


class CreateCategoryView(APIView):
    """Handle category creation"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        """Create new category or return existing one"""
        serializer_instance = product_serializer.CreateCategorySerializer(
            data=request.data
        )

        if not serializer_instance.is_valid():
            return Response(
                f"Please Enter Valid Data {str(serializer_instance.errors)}", status=400
            )
        
        # Check if category already exists
        category_instance = product_models.Category.objects.filter(
            name =serializer_instance.validated_data.get("name")
        ).last()

        if category_instance:
            return Response(data=category_instance.get_details(), status=200)

        # Create new category
        category_instance = product_models.Category.objects.create(
            **serializer_instance.validated_data
        )

        return Response(data=category_instance.get_details(), status=200)


class BulkCreateView(APIView):
    """Handle bulk product creation using Celery tasks"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @staticmethod
    def post(request):
        """Trigger async bulk product creation"""
        serializer_instance = product_serializer.BulkCreateSerializer(data=request.data)

        if not serializer_instance.is_valid():
            return Response(
                f"Please Enter Valid Data {str(serializer_instance.errors)}", status=400
            )
        
        # Queue bulk creation task
        product_tasks.bulk_create_product.delay(number=serializer_instance.validated_data.get("number"))
        
        return Response(
            data="We will inform you when data has created",
            status=200
        )
    

class ExportProductDetailsView(APIView):
    """Export product data to Excel file"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @staticmethod
    def get(request):
        """Generate and download Excel file with all product data"""
        product_instances = product_models.Product.objects.all()
        
        # Convert to DataFrame
        df = pd.DataFrame([product.get_details() for product in product_instances])
        
        # Remove timezone info for Excel compatibility
        df['created_at'] = df['created_at'].dt.tz_localize(None)
        df['updated_at'] = df['updated_at'].dt.tz_localize(None)

        # Generate Excel file in memory
        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            
            # Prepare HTTP response with Excel file
            filename = 'Rapport'
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(b.getvalue(), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
            return response