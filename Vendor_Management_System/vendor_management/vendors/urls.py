# vendors/urls.py

from django.urls import path
from .views import (
    create_vendor, list_vendors, retrieve_vendor, update_vendor, delete_vendor,
    create_purchase_order, list_purchase_orders, retrieve_purchase_order, update_purchase_order, delete_purchase_order,
    vendor_performance
)

urlpatterns = [
    path('vendors/', create_vendor, name='create_vendor'),
    path('vendors/', list_vendors, name='list_vendors'),
    path('vendors/<int:vendor_id>/', retrieve_vendor, name='retrieve_vendor'),
    path('vendors/<int:vendor_id>/', update_vendor, name='update_vendor'),
    path('vendors/<int:vendor_id>/', delete_vendor, name='delete_vendor'),
    path('purchase_orders/', create_purchase_order, name='create_purchase_order'),
    path('purchase_orders/', list_purchase_orders, name='list_purchase_orders'),
    path('purchase_orders/<int:po_id>/', retrieve_purchase_order, name='retrieve_purchase_order'),
    path('purchase_orders/<int:po_id>/', update_purchase_order, name='update_purchase_order'),
    path('purchase_orders/<int:po_id>/', delete_purchase_order, name='delete_purchase_order'),
    path('vendors/<int:vendor_id>/performance/', vendor_performance, name='vendor_performance'),
]
