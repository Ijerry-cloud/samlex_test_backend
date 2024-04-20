from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import StoreConfig
from .serializers import UserSerializer, CreateUserSerializer, GetAllUsersSerializer, StoreConfigSerializer, UserLoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from accounts.authentication import BearerTokenAuthentication
from accounts.permissions import *


User = get_user_model()

PARAM_QUERY_BY_EMPLOYEE_USERNAME = "username"
PARAM_QUERY_PAGE_NUMBER = "page"
COMPANY_NAME = "chuksdigitals"

# Create your views here.
class LoginView(generics.CreateAPIView):
    
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        
        # TODO:
        # add validation to ensure email and password are provided
        # in the post body
        
        print('response is -------------')
        #dict(response._headers.items())
        print(request.headers)
        user = get_object_or_404(User, email=request.data.get('email'))

        


        # if the user is not active throw error
        if not user.is_active:    
            return response.Response({'detail': 'authentication failed'}, status=status.HTTP_400_BAD_REQUEST)    
        
        # if password does not match 
        if not user.check_password(request.data.get('password')):
            #print(request.data.get('password'))
            return response.Response({'detail': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)    
        
        # delete all previous tokens
        Token.objects.filter(user=user).delete()
        
        # create a new token for that user
        token = Token.objects.create(user=user)
        
        data = dict()
        data['user'] = UserLoginSerializer(user).data
        data['token'] = token.key

        #print(data['user'])
        
        return response.Response(data, status=status.HTTP_200_OK)
    

class LogoutView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        tokens = Token.objects.filter(user=request.user)
        # delete all tokens affiliated with this user
        tokens.delete()
        return response.Response({'detail': 'Logout Successful'}, status=status.HTTP_200_OK)


class ChangePasswordView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        # validate that the user sends the old password and new password
        if request.user.check_password(request.data.get('old_password')):
            request.user.set_password(request.data.get('new_password'))
            return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)    
        return response.Response({'detail': 'incorrect password provided'}, status=status.HTTP_400_BAD_REQUEST)
   
    
class ResetPasswordView(generics.CreateAPIView):
    
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        user = get_object_or_404(User, id=request.data.get("id"))
        
        user.set_password(request.data.get("password"))
        
        return response.Response({
            'detail': 'success'
        },
        status=status.HTTP_200_OK)
    
    
class ListCreateUserView(generics.ListCreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, EmployeesAccessPermission]
    
    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by('username')

        if request.query_params.get(PARAM_QUERY_BY_EMPLOYEE_USERNAME):
            users = users.filter(username__icontains = request.query_params.get(PARAM_QUERY_BY_EMPLOYEE_USERNAME))

        if not request.query_params.get(PARAM_QUERY_PAGE_NUMBER):#dont paginate if "page" is not in query parameter
            user_serializer = GetAllUsersSerializer(users, many=True)
            return response.Response(
                user_serializer.data,
                status=status.HTTP_200_OK
            )

        print("i'm being queried")
        
        users = users.exclude(email="adminer@adminer.com") #this line is added to the dev code just so that users wouldn't be able to delete the provided test account. Should be removec from prod code

        
        if request.query_params.get("first_name"):
            users = users.filter(first_name__icontains=request.query_params.get("first_name"))
        if request.query_params.get("last_name"):
            users = users.filter(last_name__icontains=request.query_params.get("last_name"))
        if request.query_params.get("email"):
            users = users.filter(email__icontains=request.query_params.get("email"))
        if request.query_params.get("is_active"):
            value = True if request.query_params.get("is_active") == 'true' else False
            users = users.filter(is_active=value)
        
        
        user_serializer = UserLoginSerializer(self.paginate_queryset(users), many=True)
        
        return self.paginator.get_paginated_response(user_serializer.data)    
    
    def post(self, request, *args, **kwargs):
        
        data = dict()
        try:
            if User.objects.filter(email=request.data.get("email")):
                return response.Response({
                    "detail": "This email already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=request.data.get("username")):
                return response.Response({
                    "detail": "This username already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            #print(request.data.get("customer_perm"))
            #print(request.data)

            user = User.objects.create(
                is_lead=False,
                first_name=request.data.get('first_name'),
                last_name=request.data.get('last_name'),
                gender=request.data.get('gender'),
                dept=request.data.get('dept'),
                email=request.data.get('email'),
                username=request.data.get('username'),

                phone_no=request.data.get('phone_no'),
                address_1=request.data.get('address_1'),
                address_2=request.data.get('address_2'),
                city=request.data.get('city'),
                state=request.data.get('state'),
                zip=request.data.get('zip'),
                country=request.data.get('country'),

                customer_perm=request.data.get('customer_perm'),
                items_perm=request.data.get('items_perm'),
                item_kits_perm=request.data.get('item_kits_perm'),
                suppliers_perm=request.data.get('suppliers_perm'),
                reports_perm=request.data.get('reports_perm'),
                receivings_perm=request.data.get('receivings_perm'),
                sales_perm=request.data.get('sales_perm'),
                employees_perm=request.data.get('employees_perm'),
            )

            user.set_password(request.data.get("password"))
            user.save()
            user = CreateUserSerializer(user).data

            data['detail'] = user
            
            return response.Response(
                data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            #print(e)
            return response.Response(
                {
                    "detail": "Oops! something went wrong, please contact the admin",
                },
                status=status.HTTP_400_BAD_REQUEST
            )


    
class ActivateUserView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        # :TODO
        # validate to ensure that ids have been passed in the json payload
        
        users = User.objects.filter(id__in=request.data.get("ids"))
        for user in users:
            user.is_active = True
            user.save()
            
        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)
    

class UpdateUserView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, EmployeesAccessPermission]
    
    def post(self, request, *args, **kwargs):
        #print(request.user)
        user = get_object_or_404(User, username=request.data.get("user_data")['username'])
        #print(request.data.get("user_data")['username'])
        user_serializer = UserSerializer(user)

        serializer = UserLoginSerializer(user, data=request.data.get("user_data"), partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()

            #update password if password is contained in the request
            if request.data.get("user_password")['password']:
                #print('shouldnt get to here')
                user.set_password(request.data.get("user_password")['password'])
                user.save()

            return response.Response({
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        #print(serializer.errors)
        return response.Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeactivateUserView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        # :TODO
        # validate to ensure that ids have been passed in the json payload
        
        users = User.objects.filter(id__in=request.data.get("ids"))
        
        for user in users:
            user.is_active = False
            user.save()

        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)
    

class DeleteUserView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, EmployeesAccessPermission]
    
    def post(self, request, *args, **kwargs):
        
        # :TODO
        # validate to ensure that ids have been passed in the json payload
        
        users = User.objects.filter(id__in=request.data.get("ids"))
        users.delete()
        
        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)
    
class DeleteOneUserView(generics.CreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, EmployeesAccessPermission]
    
    def post(self, request, *args, **kwargs):
        #print(11111111111111111111111)
        
        user = get_object_or_404(User, username=request.data.get("username"))
        #print(22222222222222222222)
        user_id = user.id
        #print(33333333333333333333333)
        user.delete()
        #print(4444444444444444444444444)
        return response.Response({'detail': 'success', 'id': user_id}, status=status.HTTP_200_OK)

    
class ProfileView(generics.ListCreateAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user_department = request.user.dept
        same_dept = User.objects.all().filter(dept=user_department)
        
        data = dict()
        
        user = UserLoginSerializer(request.user).data
        same_dept_users = UserLoginSerializer(same_dept, many=True).data    
        return response.Response({'detail': user, 'others': same_dept_users}, status=status.HTTP_200_OK)
    
class GetSalesConfigView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, IsSamlexAdmin]

    def get(self, request, *args, **kwargs):

        config  = get_object_or_404(StoreConfig, name=COMPANY_NAME)
        config_serializer = StoreConfigSerializer(config).data

        data = dict()
        data = config_serializer

        return response.Response(data, status=status.HTTP_200_OK)
    
class UpdateSalesConfigView(generics.CreateAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, IsSamlexAdmin]

    def post(self, request, *args, **kwargs):
        config = get_object_or_404(StoreConfig, name=COMPANY_NAME)

        serializer = StoreConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()

            return response.Response({
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        return response.Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )





    
    