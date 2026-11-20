from django.db import models

class Payment(models.Model):
    STATUS = [("PENDING", "Pending"), ("SUCCESS", "Success"), ("FAILED", "Failed")]
    phone = models.CharField(max_length=12)
    amount = models.PositiveIntegerField()
    checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - {self.amount} - {self.status}"