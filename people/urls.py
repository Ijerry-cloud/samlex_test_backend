from django.urls import path
from .views import *

urlpatterns = [
    path('suppliers/', ListCreateSupplierView.as_view(), name='create_suppliers' ),
]