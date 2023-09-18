from rest_framework import permissions

class CustomerAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.customer_perm)
    
class ItemsAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.items_perm)
    
class ItemkitsAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.item_kits_perm)
    
class SuppliersAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.suppliers_perm)
    
class ReportsAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.reports_perm)
    
class ReceivingsAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.receivings_perm)
    
class SalesAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.sales_perm)
    
class EmployeesAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        return bool(request.user.employees_perm)