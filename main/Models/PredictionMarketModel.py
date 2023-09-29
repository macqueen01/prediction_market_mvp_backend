from django.db import models

class PredictionMarket(models.Model):
    title = models.CharField(default = 'Untitled Prediction Market')
    description = models.TextField(default = 'No description')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField()
    is_active = models.IntegerField(default = 1)

    