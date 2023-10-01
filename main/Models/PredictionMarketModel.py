from django.db import models
from django.utils import timezone

from main.MarketMakers.shares import Share

# Models from same module
from .ReservePoolModel import ReservePool, PoolArgumentTranslator
from .MarketMakerModel import MarketMaker
from .SnapshotModel import Snapshot

# Market settings
from main.PredictionMarkets.settings import MarketSettings 

    

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

        # make snapshot for this market
        Snapshot.objects.create(market_type = settings.market_maker_type)

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
        # take snapshot of the initial state of the market
        prediction_market.take_snapshot()

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
    title = models.CharField(default = 'Untitled Prediction Market', max_length = 500)
    description = models.TextField(default = 'No description')
    start_date = models.DateTimeField()

    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    is_active = models.IntegerField(default = 1)

    reserve_pool = models.ForeignKey(ReservePool, on_delete=models.CASCADE)
    market_maker = models.ForeignKey(MarketMaker, on_delete=models.CASCADE)

    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, blank=True, null=True)

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
    
    def take_snapshot(self):
        """
        Takes a snapshot of the current state of the market
        """
        snapshot = self.snapshot
        market_type = self.market_maker.market_maker_type

        assert(snapshot is not None)

        snapshot_arguments = PoolArgumentTranslator.translate(reserve_pool=self.reserve_pool, market_type=market_type)
        
        snapshot.record_snapshot(**snapshot_arguments)
        return snapshot
    
    def _buy_positive(self, fund: float) -> Share:

        assert(self.is_active == 1)

        pool_state = self.market_maker.simulate_positive_buy(fund)
        pool_positive_shares, pool_negative_shares, return_shares = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_shares']
        
        assert(return_shares().share_type == 'positive')

        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)
        reserve_pool.increase_market_size(fund, 'positive')

        # take snapshot of the current state of the market
        self.take_snapshot()

        return return_shares
    
    def _buy_negative(self, fund: float) -> Share:

        assert(self.is_active == 1)

        pool_state = self.market_maker.simulate_negative_buy(fund)
        pool_positive_shares, pool_negative_shares, return_shares = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_shares']
        
        assert(return_shares().share_type == 'negative')

        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)
        reserve_pool.increase_market_size(fund, 'negative')

        # take snapshot of the current state of the market
        self.take_snapshot()

        return return_shares
    

    def _sell(self, shares: Share) -> float:

        assert(self.is_active == 1)

        pool_state = self.market_maker.simulate_sell(shares)

        pool_positive_shares, pool_negative_shares, return_fund = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_fund']

        assert(return_fund > 0)
        
        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)
        reserve_pool.decrease_market_size(return_fund, shares.share_type)

        # take snapshot of the current state of the market
        self.take_snapshot()

        return return_fund
    
    def _get_estimated_price_for_single_share(self) -> dict:
        """
        Calculates an estimated price for one share at the given reserve pool state
        This value relies on the ratio of shares in the reserve pool
        """
        return self.market_maker.get_estimated_price_per_share()
    
    def _get_exact_price_for_single_share(self) -> dict:
        """
        Calculates the exact price for one share at the given reserve pool state
        """
        return self.market_maker.get_exact_price_per_share()
    
    def _get_exact_share_prices(self, shares: Share) -> float:
        
        # Check if shares is a valid share object
        assert(issubclass(type(shares), Share))

        return self.market_maker.simulate_sell(shares)
    
