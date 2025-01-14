
from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', UploadFileView.as_view(), name='upload-file'),
    path('csv/', UploadItemCSVFileView.as_view(), name='upload-csv'),
    path('list-create/', ListCreateItemView.as_view(), name='create_item'),
    path('update/', UpdateItemView.as_view(), name='update_item'),
    path('group-update/', UpdateItemGroupView.as_view(), name='group_update'),
    path('delete/', DeleteItemView.as_view(), name='item_delete'),
    path('group-delete/', DeleteItemGroupView.as_view(), name='group_delete'),

    path('categories/list-create/', ListCreateCategoryView.as_view(), name='list_categories')
]
