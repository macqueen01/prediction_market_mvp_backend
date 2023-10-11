from django.db import models

from main.MarketMakers.shares import POOL_STATE_TYPE

# Internal model import
from .BankModel import Bank

class ReservePoolManager(models.Manager):
    def initialize_pool(self, initial_positive, initial_negative, market_type: str):
        """
        reserved_pool_size is an initialy allocated amount of asset to the reserve pool
        """
        constant = initial_positive * initial_negative

        reserve_pool = self.create(
            _positive = initial_positive,
            _negative = initial_negative,
            _total = initial_positive + initial_negative,
            _constant = constant,
            market_maker_type = market_type
        )

        reserve_pool.save()
        return reserve_pool
        

class ReservePool(models.Model):
    _positive = models.FloatField(default = 0)
    _negative = models.FloatField(default = 0)
    _total = models.FloatField(default = 0)
    _constant = models.FloatField(default = 0)
    market_maker_type = models.CharField(max_length = 120, default = 'binary_constant_product')

    _positive_market_size = models.FloatField(default = 0)
    _negative_market_size = models.FloatField(default = 0)

    def get_positive(self):
        return self._positive
    
    def get_negative(self):
        return self._negative
    
    def get_total(self):
        return self._total
    
    def get_constant(self):
        return self._constant
    
    def set_shares(self, positive, negative):
        assert(round(positive * negative, 3) == self.get_constant())

        self._positive = round(positive, 3)
        self._negative = self._constant / self._positive
        self._total = positive + negative
        self.save()
        return self
    
    def increase_market_size(self, amount: float, share_type: str):
        if share_type == 'positive':
            self._positive_market_size += amount
        elif share_type == 'negative':
            self._negative_market_size += amount
        else:
            raise Exception('Invalid share type')
        self.save()
        return self
    
    def decrease_market_size(self, amount: float, share_type: str):
        if share_type == 'positive':
            self._positive_market_size -= amount
        elif share_type == 'negative':
            self._negative_market_size -= amount
        else:
            raise Exception('Invalid share type')
        self.save()
        return self
    
    def get_market_size(self, share_type: str):
        if share_type == 'positive':
            return self._positive_market_size
        elif share_type == 'negative':
            return self._negative_market_size
        else:
            raise Exception('Invalid share type')
        
    def get_total_market_size(self):
        return self._positive_market_size + self._negative_market_size
    
    def get_share_options(self):
        return ['positive', 'negative']
    
    def get_current_shares(self):
        return {
            'positive_shares': self.get_positive(),
            'negative_shares': self.get_negative(),
        }
    
    def get_probability_of_share_type(self, share_type: str) -> float:
        if share_type == 'positive':
            return self._negative / self._total
        elif share_type == 'negative':
            return self._positive / self._total
        else:
            raise Exception('Invalid share type')
    
    def get_pool_state(self):
        return POOL_STATE_TYPE.get(self.market_maker_type)(**self.get_current_shares())
    
    objects = ReservePoolManager()
    
    class Meta:
        pass

class PoolArgumentTranslator(object):
    # Pool Agrument Translator translates the pool arguments into a dictionary
    # that can be used to create a snapshot object

    def translate(self, reserve_pool: ReservePool, market_type: str) -> dict:
        if market_type == 'binary_constant_product':
            return self._translate_binary_constant_product(reserve_pool)
        raise NotImplementedError('Market type not supported')
    
    def _translate_binary_constant_product(self, reserve_pool: ReservePool) -> dict:
        return {
            'positive_shares': reserve_pool.get_positive(),
            'negative_shares': reserve_pool.get_negative(),
            'positive_market_size': reserve_pool.get_market_size('positive'),
            'negative_market_size': reserve_pool.get_market_size('negative'),
        }