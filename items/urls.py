
from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', UploadFileView.as_view(), name='upload-file'),
    path('csv/', UploadItemCSVFileView.as_view(), name='upload-csv'),
    path('list-create', ListCreateItemView.as_view(), name='create_suppliers')
]
