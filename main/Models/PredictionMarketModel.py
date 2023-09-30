from django.db import models
from django.utils import timezone

from main.MarketMakers.shares import Share

# Models from same module
from .ReservePoolModel import ReservePool
from .MarketMakerModel import MarketMaker

# Market settings
from main.PredictionMarkets import MarketSettings 

    

class PredictionMarketManager(models.Manager):
    def create_market(self, title, description, start_date, end_date, settings: MarketSettings):

        # make market maker for this market with specified settings
        market_maker = MarketMaker.objects.create_market_maker(settings)
        shares = market_maker.get_num_shares()
        # make reserve pool for this market with the shares from market maker
        reserve_pool = ReservePool.objects.initialize_pool(
            initial_positive = shares['positive_shares'],
            initial_negative = shares['negative_shares']
        )

        prediction_market = self.create(
            title = title,
            description = description,
            start_date = start_date,
            end_date = end_date,
            created_at = timezone.now(),
            is_active = 0,
            reserve_pool = reserve_pool,
            market_maker = market_maker
        )
        prediction_market.save()

        return prediction_market
    
    def get_active_markets(self):
        return self.filter(is_active = 1)
    
    def get_inactive_markets(self):
        return self.filter(is_active = 0)
    
    def get_market_by_id(self, id):
        return self.get(id = id)
    
    def get_market_by_title(self, title):
        return self.get(title = title)


class PredictionMarket(models.Model):
    title = models.CharField(default = 'Untitled Prediction Market')
    description = models.TextField(default = 'No description')
    start_date = models.DateTimeField()

    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    is_active = models.IntegerField(default = 1)

    reserve_pool = models.ForeignKey(ReservePool, on_delete=models.CASCADE)
    market_maker = models.ForeignKey(MarketMaker, on_delete=models.CASCADE)

    # related markets are coupled ones that any one of the market predicted results depends on the others
    related_markets = models.ManyToManyField('self', symmetrical=False)

    objects = PredictionMarketManager()

    def activate(self):
        self.is_active = 1
        self.save()

    def deactivate(self):
        self.is_active = 0
        self.save()

    def get_current_shares(self):
        return self.reserve_pool.get_current_shares()
    
    def _buy_positive(self, fund: float) -> Share:

        pool_state = self.market_maker.simulate_positive_buy(fund)
        pool_positive_shares, pool_negative_shares, return_shares = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_shares']
        
        assert(return_shares().share_type == 'positive')

        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)

        return return_shares
    
    def _buy_negative(self, fund: float) -> Share:

        pool_state = self.market_maker.simulate_negative_buy(fund)
        pool_positive_shares, pool_negative_shares, return_shares = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_shares']
        
        assert(return_shares().share_type == 'negative')

        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)

        return return_shares
    

    def _sell(self, shares: Share) -> float:

        pool_state = self.market_maker.simulate_sell(shares)

        pool_positive_shares, pool_negative_shares, return_fund = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_fund']

        assert(return_fund > 0)
        
        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)

        return return_fund
    
    def _get_estimated_price_per_share(self, shares: Share) -> float:
        # Check if shares is a valid share object
        assert(issubclass(type(shares), Share))

        return self.market_maker.get_estimated_price_per_share(shares)
    
    # def _get_exact_price_per_
    