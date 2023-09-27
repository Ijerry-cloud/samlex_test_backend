from django.urls import path
from .views import *

urlpatterns = [
    path('suppliers/', ListCreateSupplierView.as_view(), name='create_suppliers' ),
    path('suppliers/update/', UpdateSupplierView.as_view(), name='update_suppliers'),
    path('suppliers/delete/', DeleteSupplierView.as_view(), name='delete_suppliers'),
]