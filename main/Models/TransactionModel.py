from django.db import models 

TRANSACTION_TYPE = {
    'buy': None
}

class Transaction(models.Model):
    transaction_type = models.CharField(max_length = 120, default = 'buy')
    