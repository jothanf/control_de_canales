from django.db import models


# Create your models here.
class ProviderModel(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=20, null=True, blank=True)
    credit_balance = models.PositiveIntegerField(null=True, blank=True)
    pending_balance = models.PositiveIntegerField(null=True, blank=True)
    total_paid = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class AnimalModel(models.Model):
    STATE_CHOICES = (
        ('alive', 'Alive'),
        ('processed', 'Processed'),
    )
    
    PAYMENT_STATE_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    )

    ANIMAL_TYPE_CHOICES = (
        ('vacuno', 'Vacuno'),
        ('porcino', 'Porcino'),
    )

    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='alive')
    payment_state = models.CharField(max_length=10, choices=PAYMENT_STATE_CHOICES, default='pending')
    animal_type = models.CharField(max_length=10, choices=ANIMAL_TYPE_CHOICES, null=True)
    identification = models.CharField(max_length=50, null=True, blank=True)
    live_price = models.PositiveIntegerField(null=True, blank=True)
    live_weight = models.PositiveIntegerField(null=True, blank=True)
    purchase_dates = models.DateField(null=True, blank=True)
    payment_terms = models.PositiveIntegerField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    slaughter_dates = models.DateField(null=True, blank=True)
    canal_price = models.PositiveIntegerField(null=True, blank=True)
    canal_weight = models.PositiveIntegerField(null=True, blank=True)
    other_expenses = models.TextField(null=True, blank=True)
    total_price_purchase = models.PositiveIntegerField(null=True, blank=True)
    provider = models.ForeignKey(ProviderModel, on_delete=models.CASCADE, null=True, blank=True)
    payments = models.PositiveIntegerField(default=0)
    balance_due = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.identification


    
class OtherExpensesModel(models.Model):
    description = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    animal = models.ForeignKey(AnimalModel, on_delete=models.CASCADE, related_name='expenses')
