from django.db import models

class Payment(models.Model):
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.order_id
