from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Invoice(models.Model):
    invoice_no = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_sale = models.DateField(default=timezone.now, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')

    @property
    def balance(self):
        """Calculate the remaining balance (total - amount_paid)"""
        return (self.total or 0) - (self.amount_paid or 0)

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            today = timezone.now().strftime('%Y%m%d')
            prefix = f"INV-{today}-"
            last_invoice = Invoice.objects.filter(invoice_no__startswith=prefix).order_by('-invoice_no').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_no[-3:])
                next_number = f"{last_number+1:03d}"
            else:
                next_number = "001"
            self.invoice_no = f"{prefix}{next_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_no


class AdminLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

class Product(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    item = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.item} - {self.quantity} units"

class StockMovement(models.Model):
    """
    Track all stock movements for audit trail
    """
    MOVEMENT_TYPES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('RETURN', 'Return'),
        ('RESTOCK', 'Restock'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity_change = models.IntegerField()  # Positive for additions, negative for reductions
    stock_before = models.IntegerField()  # Stock level before this movement
    stock_after = models.IntegerField()   # Stock level after this movement
    reference = models.CharField(max_length=100, blank=True, null=True)  # Invoice number, etc.
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type}: {self.quantity_change}"