from django.db import models
from main.MarketMakers.interface import MarketMakerInterface
from main.MarketMakers.shares import Share
from main.PredictionMarkets.settings import MarketSettings

class MarketMakerManager(models.Manager):

    def create_market_maker(self, settings: MarketSettings):
        """
        settings is MarketSettings object
        """
        market_maker_type = settings.market_maker_type
        initial_fund = settings.initial_fund
        cap_price = settings.cap_price
        initial_positive_probability = settings.initial_positive_probability
        initial_negative_probability = settings.initial_negative_probability
        
        return self._create_market_maker(
            market_maker_type,
            initial_fund,
            cap_price,
            initial_positive_probability,
            initial_negative_probability
        )
    
    def _create_market_maker(self, 
                            marker_maker_type, 
                            initial_fund, 
                            cap_price, 
                            initial_positive_probability, 
                            initial_negative_probability):
        
        market_maker = self.create(
            market_maker_type = marker_maker_type,
            initial_fund = initial_fund,
            cap_price = cap_price,
            initial_positive_probability = initial_positive_probability,
            initial_negative_probability = initial_negative_probability
        )
        market_maker.save()
        return market_maker

class MarketMaker(models.Model):
    market_maker_type = models.CharField(max_length = 120, default = 'binary_constant_product')
    initial_fund = models.FloatField(default = 0)
    cap_price = models.FloatField(default = 0)
    initial_positive_probability = models.FloatField(default = 0.5)
    initial_negative_probability = models.FloatField(default = 0.5)
    
    objects = MarketMakerManager()
    
    def _get_market_maker_interactor(self) -> MarketMakerInterface:
        """
        Returns the market maker interactor under current share circumstances
        """
        market_maker = self._get_market_maker_interactor()
        market_maker.set_num_shares(self.num_positive, self.num_negative)
        return market_maker
    
    def get_num_shares(self) -> dict:
        market_maker = self._get_market_maker_interactor()
        return market_maker.get_num_shares()
    
    def simulate_positive_buy(self, fund) -> Share:
        market_maker = self._get_market_maker_interactor()
        return market_maker.add_fund_to_positive_then_calculate_shares(fund)
    
    def simulate_negative_buy(self, fund) -> Share:
        market_maker = self._get_market_maker_interactor()
        return market_maker.add_fund_to_negative_then_calculate_shares(fund)
    
    def simulate_sell(self, shares: Share) -> float:
        # Check if shares is a valid share object
        assert(issubclass(type(shares), Share))

        market_maker = self._get_market_maker_interactor()
        if (shares.share_type == 'positive'):
            return market_maker.remove_fund_from_positive_then_calculate_shares(shares)
        elif (shares.share_type == 'negative'):
            return market_maker.remove_fund_from_negative_then_calculate_shares(shares)
        raise ValueError('Invalid share type')
    
    def get_estimated_price_per_share(self) -> dict:

        market_maker = self._get_market_maker_interactor()
        return market_maker.estimated_price_for_single_share()
    
    def get_exact_price_per_share(self) -> dict:
        """
        Calculates the exact price for one share at the given reserve pool state
        """
        market_maker = self._get_market_maker_interactor()
        return market_maker.price_for_single_share()
    
    
    

        

