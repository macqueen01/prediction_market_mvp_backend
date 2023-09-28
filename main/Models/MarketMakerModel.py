from django.db import models
from main.MarketMakers import ConstantProductMarketMaker


MARKET_MAKER_TYPE = {
    'binary_constant_product': ConstantProductMarketMaker,
}

class MarketMakerManager(models.Manager):
    def create_market_maker(self, marker_maker_type, initial_fund, cap_price, initial_positive_probability, initial_negative_probability):
        market_maker = self.create(
            market_maker_type = marker_maker_type,
            initial_fund = initial_fund,
            cap_price = cap_price,
            initial_positive_probability = initial_positive_probability,
            initial_negative_probability = initial_negative_probability
        )
        return market_maker

class MarketMaker(models.Model):
    market_maker_type = models.CharField(max_length = 120, default = 'binary_constant_product')
    initial_fund = models.FloatField(default = 0)
    cap_price = models.FloatField(default = 0)
    initial_positive_probability = models.FloatField(default = 0.5)
    initial_negative_probability = models.FloatField(default = 0.5)
    
    objects = MarketMakerManager()

    def _get_market_maker_interactor(self):
        market_maker = MARKET_MAKER_TYPE.get(self.market_maker_type)
        market_maker = market_maker()

