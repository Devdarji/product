
from django.urls import path
from product import views as product_views

urlpatterns = [
    path('create/p/', product_views.CreateProductView.as_view(), name='create-get-product'),
    path('update/p/<int:id>/', product_views.UpdateProductView.as_view(), name='update-delete-search-product'),
    path('create/c/', product_views.CreateCategoryView.as_view(), name='create-get-category'),
    path('bulk-create/', product_views.BulkCreateView.as_view(), name='bulk-create'),
    path('export/', product_views.ExportProductDetailsView.as_view(), name='export-product-details'),
]