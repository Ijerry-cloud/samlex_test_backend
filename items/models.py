

from django.db import models
from people.models import Supplier



class File(models.Model):
    id = models.CharField(primary_key=True, max_length=6)
    staff_name = models.CharField(max_length=100)
    position = models.CharField(max_length=200)
    age = models.IntegerField()
    year_joined = models.CharField(max_length=4)

    def __str__(self):
        return self.staff_name
    
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ("name",)

class Item(models.Model):
    barcode = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name="items", blank=True, null=True, on_delete=models.SET_NULL)
    supplier = models.ForeignKey(Supplier, related_name="items", blank=True, null=True, on_delete=models.SET_NULL)
    cost_price = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax1_name = models.CharField(max_length=10, blank=True, null=True)
    tax1_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    tax2_name = models.CharField(max_length=10, blank=True, null=True)
    tax2_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    quantity = models.IntegerField(blank=True, null=True, default=0)
    reorder_level = models.IntegerField(blank=True, null=True, default=0)
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    allow_alt = models.BooleanField(null=True)
    has_serial_no = models.BooleanField(null=True)
    edit_history = models.JSONField(default=list, editable=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ("name",)
    


