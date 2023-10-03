from django.test import TestCase
from django.utils import timezone
from .models import PredictionMarket, MarketMaker, ReservePool, Snapshot, Share
from .PredictionMarkets.settings import MarketSettings

import time
import random


class PredictionMarketModelTestCase(TestCase):
    def setUp(self):
        settings = MarketSettings(
            100, 1, 0.5, 0.5, True, True
        )

        # Create a test PredictionMarket instance
        self.prediction_market = PredictionMarket.objects.create_market(
            title="Test Market",
            description="Test Description",
            start_date=timezone.now(),
            end_date  = timezone.now(),
            settings=settings
        ) 

        self.reserve_pool = self.prediction_market.reserve_pool

    def test_activate_market(self):
        self.prediction_market.activate()
        self.assertEqual(self.prediction_market.is_active, 1)

    def test_deactivate_market(self):
        self.prediction_market.deactivate()
        self.assertEqual(self.prediction_market.is_active, 0)

    def test_get_current_shares(self):
        self.prediction_market.activate()
        current_shares = self.prediction_market.get_current_shares()
        self.assertEqual(current_shares, {'positive_shares': 100, 'negative_shares': 100})

    def test_take_snapshot(self):
        self.prediction_market.activate()
        snapshot = self.prediction_market.take_snapshot()
        self.assertIsNotNone(snapshot)  # Ensure a snapshot object is created

    def test_buy_positive(self):
        self.prediction_market.activate()
        fund = 50.0
        returned_shares = self.prediction_market.buy_positive(fund)
        self.assertEqual(round(self.prediction_market._get_exact_share_prices(returned_shares)['returned_fund'], 2), 50.0)

    def test_buy_negative(self):
        self.prediction_market.activate()
        fund = 50.0
        returned_shares = self.prediction_market.buy_negative(fund)
        self.assertEqual(round(self.prediction_market._get_exact_share_prices(returned_shares)['returned_fund'], 2), 50.0)

    def test_sell(self):
        self.prediction_market.activate()
        initial_positive_shares = self.reserve_pool.get_current_shares()['positive_shares']
        # buy the shares first
        fund = 50.0
        returned_shares = self.prediction_market.buy_positive(fund)

        # sell the shares
        returned_fund = self.prediction_market.sell(returned_shares)
        new_positive_shares = self.reserve_pool.get_current_shares()['positive_shares']
        self.assertEqual(round(new_positive_shares, 2), round(initial_positive_shares, 2))
        self.assertEqual(round(returned_fund, 3), 50.0)

    def _sell(self):
        self.prediction_market.activate()
        shares = self.prediction_market.buy_positive(30.0)
        shares2 = self.prediction_market.buy_negative(20.0)
        shares3 = self.prediction_market.buy_positive(50.0)
        self.prediction_market.sell(shares)
        self.prediction_market.sell(shares2)
        self.prediction_market.sell(shares3)
        shares4 = self.prediction_market.buy_negative(30.0)
        print([round(x.get_positive_market_size() + x.get_negative_market_size(), 3) for x in self.prediction_market.snapshot.get_snapshots()])
        print([round(x.get_positive_market_size() , 3) for x in self.prediction_market.snapshot.get_snapshots()])
        print([round( x.get_negative_market_size(), 3) for x in self.prediction_market.snapshot.get_snapshots()])
    def test_market_size_change(self):
        self.prediction_market.activate()
        self._sell()
    """

    def test_get_estimated_price_for_single_share(self):
        estimated_price = self.prediction_market._get_estimated_price_for_single_share()
        self.assertIsInstance(estimated_price, dict)
        self.assertIn('positive', estimated_price)
        self.assertIn('negative', estimated_price)

    def test_get_exact_price_for_single_share(self):
        exact_price = self.prediction_market._get_exact_price_for_single_share()
        self.assertIsInstance(exact_price, dict)
        self.assertIn('positive', exact_price)
        self.assertIn('negative', exact_price)

    def test_get_exact_share_prices(self):
        shares = Share(share_type='positive', quantity=10)
        exact_share_prices = self.prediction_market._get_exact_share_prices(shares)
        self.assertIsInstance(exact_share_prices, float)

    def test_related_markets(self):
        # Create a related market
        related_market = PredictionMarket.objects.create(
            title="Related Market",
            description="Related Description",
            start_date=timezone.now(),
            created_at=timezone.now(),
            is_active=1,
            reserve_pool=self.reserve_pool,
            market_maker=self.market_maker,
            snapshot=self.snapshot
        )

        # Add the related market to the current market's related markets
        self.prediction_market.related_markets.add(related_market)

        # Check if the related market is in the current market's related markets
        self.assertIn(related_market, self.prediction_market.related_markets.all())
    """