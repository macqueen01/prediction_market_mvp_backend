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

        reserve_pool.save()
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
    
    def get_constant(self):
        return self._positive * self._negative
    
    def set_shares(self, positive, negative):
        assert(positive * negative == self.get_constant())

        self._positive = positive
        self._negative = negative
        self._total = positive + negative
        self.save()
        return self
    
    def get_current_shares(self):
        return {
            'positive_shares': self.get_positive(),
            'negative_shares': self.get_negative(),
        }
    
    objects = ReservePoolManager()
    
    class Meta:
        fields = ['_positive', '_negative', '_total']

    
