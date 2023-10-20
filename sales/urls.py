from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', ListCreateSalesView.as_view(), name='create_sales' )
]