from django.db import models

# Internal model import
from Models.BankModel import Bank

class ReservePoolManager(models.Manager):
    def initialize_pool(self, initial_positive, initial_negative):
        """
        reserved_pool_size is an initialy allocated amount of asset to the reserve pool
        """

        reserve_pool = self.create(
            _positive = initial_positive,
            _negative = initial_negative,
            _total = initial_positive + initial_negative,
        )

        return reserve_pool
        

class ReservePool(models.Model):
    _positive = models.FloatField(default = 0)
    _negative = models.FloatField(default = 0)
    _total = models.FloatField(default = 0)

    def get_positive(self):
        return self._positive
    
    def get_negative(self):
        return self._negative
    
    def get_total(self):
        return self._total
    
    objects = ReservePoolManager()
    
    class Meta:
        db_table = 'reserve_pool'
        fields = ['_yes', '_no', '_total', '_constant']

    
