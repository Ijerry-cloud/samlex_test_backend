from django.db import models



class File(models.Model):
    id = models.CharField(primary_key=True, max_length=6)
    staff_name = models.CharField(max_length=100)
    position = models.CharField(max_length=200)
    age = models.IntegerField()
    year_joined = models.CharField(max_length=4)
    def __str__(self):
        return self.staff_name

class Item(models.Model):
    barcode = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    supplier_ID = models.IntegerField(blank=True, null=True)
    cost_price = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.CharField(max_length=100, blank=True, null=True)
    tax1_name = models.CharField(max_length=10, blank=True, null=True)
    tax1_percent = models.IntegerField(blank=True, null=True)
    tax2_name = models.CharField(max_length=10, blank=True, null=True)
    tax2_percent = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField()
    reorder_level = models.CharField(max_length=10, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    allow_alt = models.BooleanField(null=True)
    has_serial_no = models.BooleanField(null=True)

    def __str__(self):
        return self.name  