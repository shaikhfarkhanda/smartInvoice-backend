from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank = True)

    def __str__(self):
        return self.name
    
class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=50)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} for {self.client.name}"
    def total_amount(self):
        return sum(item.total() for item in self.items.all())
    
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return self.quantity * self.rate
    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.rate}"