from django.db import models
from django.db.models import Sum


# Create your models here.
class PurchaserModel(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    total_credit_limit = models.PositiveIntegerField()
    outstanding_balance = models.PositiveIntegerField(default=0)  
    total_payments = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name
    
class PurchaseHistory(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('credit', 'Credit'),
        ('cash', 'Cash'),
    )
    
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    )

    purchaser = models.ForeignKey(PurchaserModel, on_delete=models.CASCADE, related_name='purchase_history')
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=100, null=True)
    weight = models.PositiveIntegerField(null=True)
    payment = models.PositiveIntegerField(default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    purchase_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"Purchase by {self.purchaser.name}"
    
class acounts_history(models.Model):
    date_day = models.DateTimeField(null=True)
    sale_day_cash = models.PositiveIntegerField(null=True)
    sale_day_credit = models.PositiveIntegerField(null=True)
    credit_day_payment = models.IntegerField(null=True)
    total_income = models.PositiveIntegerField(null=True)
    total_sale = models.PositiveIntegerField(null=True)






