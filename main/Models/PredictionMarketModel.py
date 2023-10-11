from datetime import datetime
from PIL import Image

from django.db import models
from django.utils import timezone

from prediction_market_mvp import settings

from main.MarketMakers.shares import SHARE_TYPE_BY_MARKET_TYPE, Share

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
        shares = settings.shares
        # make reserve pool for this market with the shares from market maker
        reserve_pool = ReservePool.objects.initialize_pool(
            initial_positive = shares['positive_shares'],
            initial_negative = shares['negative_shares'],
            market_type = settings.market_maker_type
        )

        # make snapshot for this market
        snapshot = Snapshot.objects.create(market_type = settings.market_maker_type)

        prediction_market = self.create(
            title = title,
            description = description,
            start_date = start_date,
            end_date = end_date,
            created_at = timezone.now(),
            is_active = 0,
            reserve_pool = reserve_pool,
            market_maker = market_maker,
            snapshot = snapshot
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
    thumbnail = models.ImageField(storage = settings.s3_storage, upload_to = 'profile_image', blank = True, null = True, default=None)
    start_date = models.DateTimeField()

    end_date = models.DateTimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField()
    is_active = models.IntegerField(default = 1)
    resolved_index = models.IntegerField(blank=True, null=True, default=None)

    reserve_pool = models.ForeignKey(ReservePool, on_delete=models.CASCADE)
    market_maker = models.ForeignKey(MarketMaker, on_delete=models.CASCADE)

    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, blank=True, null=True)

    # related markets are coupled ones that any one of the market predicted results depends on the others
    related_markets = models.ManyToManyField('self', symmetrical=False)

    objects = PredictionMarketManager()

    def activate(self) -> None:
        self.is_active = 1
        self.save()

    def deactivate(self) -> None:
        self.is_active = 0
        self.save()

    def set_thumbnail(self, thumbnail: Image.Image):
        self.thumbnail = thumbnail
        self.save()

    def is_resolved(self) -> bool:
        return self.resolved_index is not None 

    def get_share_options(self) -> list:
        return self.reserve_pool.get_share_options()

    def get_current_shares(self) -> dict:
        return self.reserve_pool.get_pool_state()()
    
    def get_snapshot_a_day_ago(self) -> Snapshot:
        snapshots_of_one_day_ago = self.snapshot.get_snapshots().filter(_timestamp__lte=datetime.fromtimestamp(timezone.now().timestamp() - timezone.timedelta(days=1).total_seconds()))

        if (snapshots_of_one_day_ago.count() == 0):
            return None
        
        return snapshots_of_one_day_ago.order_by('-_timestamp')[0]
    
    
    def take_snapshot(self) -> Snapshot:
        """
        Takes a snapshot of the current state of the market
        """
        snapshot = self.snapshot
        market_type = self.market_maker.market_maker_type

        assert(snapshot is not None)

        snapshot_arguments = PoolArgumentTranslator().translate(reserve_pool=self.reserve_pool, market_type=market_type)
        
        snapshot.record_snapshot(**snapshot_arguments)
        return snapshot

    
    def buy_positive(self, fund: float) -> Share:

        assert(self.is_active == 1)

        # get current share state in the reserve pool
        pool_state = self.reserve_pool.get_pool_state()

        pool_state = self.market_maker.simulate_positive_buy(fund, pool_state)
        pool_positive_shares, pool_negative_shares, return_shares = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_shares']
        
        assert(return_shares.share_type == 'positive')

        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)
        reserve_pool.increase_market_size(fund, 'positive')

        # take snapshot of the current state of the market
        self.take_snapshot()

        return return_shares
    
    def buy_negative(self, fund: float) -> Share:

        assert(self.is_active == 1)

        # get current share state in the reserve pool
        pool_state = self.reserve_pool.get_pool_state()

        pool_state = self.market_maker.simulate_negative_buy(fund, pool_state)
        pool_positive_shares, pool_negative_shares, return_shares = pool_state['positive_shares'], pool_state['negative_shares'], pool_state['returned_shares']
        
        assert(return_shares.share_type == 'negative')

        reserve_pool = self.reserve_pool.set_shares(pool_positive_shares, pool_negative_shares)
        reserve_pool.increase_market_size(fund, 'negative')

        # take snapshot of the current state of the market
        self.take_snapshot()

        return return_shares
    

    def sell(self, shares: Share) -> float:

        assert(self.is_active == 1)

        # get current share state in the reserve pool
        pool_state = self.reserve_pool.get_pool_state()

        pool_state = self.market_maker.simulate_sell(shares, pool_state)

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
        
        # get current share state in the reserve pool
        pool_state = self.reserve_pool.get_pool_state()

        return self.market_maker.get_estimated_price_per_share(pool_state)
    
    def _get_exact_price_for_single_share(self) -> dict:
        """
        Calculates the exact price for one share at the given reserve pool state
        """

        # get current share state in the reserve pool
        pool_state = self.reserve_pool.get_pool_state(pool_state)

        return self.market_maker.get_exact_price_per_share()
    
    def _get_exact_share_prices(self, shares: Share) -> float:
        
        # Check if shares is a valid share object
        assert(issubclass(type(shares), Share))

        # get current share state in the reserve pool
        pool_state = self.reserve_pool.get_pool_state()

        return self.market_maker.simulate_sell(shares, pool_state)
    
