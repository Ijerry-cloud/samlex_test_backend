from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('users/', ListCreateUserView.as_view(), name='create_user'),
    path('users/update/', UpdateUserView.as_view(), name='update_user'),
    path('deactivate_user/', DeactivateUserView.as_view(), name='deactivate_user'),
    path('activate_user/', ActivateUserView.as_view(), name='activate_user'),
    path('delete_user/', DeleteUserView.as_view(), name='delete_user'),
    path('users/delete_one_user/', DeleteOneUserView.as_view(), name='delete_one_user'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', ProfileView.as_view(), name='profile'),
]