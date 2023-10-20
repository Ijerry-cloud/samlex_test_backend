from django.urls import path
from .views import *

urlpatterns = [
    path('suppliers/', ListCreateSupplierView.as_view(), name='create_suppliers' ),
    path('suppliers/update/', UpdateSupplierView.as_view(), name='update_suppliers'),
    path('suppliers/delete/', DeleteSupplierView.as_view(), name='delete_suppliers'),
    path('customers/', ListCreateCustomerView.as_view(), name='create_customers'),
    path('customers/update/', UpdateCustomerView.as_view(), name='update_customer'),
    path('customers/delete/', DeleteCustomerView.as_view(), name='delete_customer')
]