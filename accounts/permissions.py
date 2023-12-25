from rest_framework import permissions

class CustomerAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)

        if request.user.customer_perm:
            return True
        else:
            return request.method in permissions.SAFE_METHODS
    
class ItemsAccessPermission(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)

        if request.user.items_perm:
            return True
        else:
            return request.method in permissions.SAFE_METHODS
        
    
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
    
class IsSamlexAdmin(permissions.BasePermission):
    message = 'You dont have access to this operation'

    def has_permission(self, request, view):
        #print(request.user.username)
        if request.user.dept == "admin":
            return True
        else:
            return False
