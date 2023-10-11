from django.test import TestCase
from django.utils import timezone
from .models import PredictionMarket, MarketMaker, ReservePool, Snapshot, Share
from .PredictionMarkets.settings import MarketSettings

from main.CoreLogics.main import *

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

        self.user1, is_created = User.objects.get_or_create(username="test_user1")
        self.user2, is_created = User.objects.get_or_create(username="test_user2")

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
    
    def test_market_size_change(self):
        self.prediction_market.activate()
        self._sell()

    def test_user_fund_wire(self):
        user1_account = self.user1.account
        user2_account = self.user2.account

        # initial fund of user1 and user2 both be 0
        self.assertEqual(user1_account.fund, 0.0)
        self.assertEqual(user2_account.fund, 0.0)

        try:
            Account.objects.transfer_fund(user1_account, user2_account, 100.0)
        except AssertionError as e:
            print(e)

        # fund of user1 increased by 100
        
        self.user1.account.get_fund(100.0)
        self.assertEqual(user1_account.fund, 100.0)

        # wire fund from user1 to user2 (100)

        Account.objects.transfer_fund(user1_account, user2_account, 100.0)
        self.assertEqual(user1_account.fund, 0.0)
        self.assertEqual(user2_account.fund, 100.0)


    def test_user_fund_withdrawal(self):
        user1_account = self.user1.account
        user1_account.get_fund(100.0)

        bank_account = '3333159588157'
        bank_code = '3333'
        
        # make withdrawal request
        withdrawal_request = Account.objects.withdraw_fund(user1_account, 100, bank_account, bank_code)
        
        # check if the withdrawal request is in the queue
        self.assertIn(withdrawal_request, WithdrawalQueue.objects.all())

        # check if the fund of the user is decreased by 100
        self.assertEqual(user1_account.fund, 0.0)

        # check if the withdrawal request is processed
        self.assertEqual(withdrawal_request.is_processed, 0)
        # check if the withdrawal request is made on the bank_account and bank_code
        self.assertEqual(withdrawal_request.withdrawing_bank_account, bank_account)
        self.assertEqual(withdrawal_request.withdrawing_bank_code, bank_code)

        # check assertion error rises when the user has insufficient fund
        try:
            Account.objects.withdraw_fund(user1_account, 100, bank_account, bank_code)
        except AssertionError as e:
            print(e)
        
    def test_user_buy_share_through_order(self):
        self.prediction_market.activate()
        user1_account = self.user1.account
        user1_account.get_fund(100.0)
        
        new_order = make_buy_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            fund = 50.0
        )

        executed_result = execute_order(new_order)

        self.assertEqual(type(executed_result), BinaryShare)

        self.assertEqual(user1_account.fund, 50)

    
    def test_user_sell_share_through_order(self):
        self.prediction_market.activate()
        user1_account = self.user1.account
        user1_account.get_fund(100.0)

        new_order = make_buy_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            fund = 50.0
        )

        executed_result = execute_order(new_order)

        self.assertEqual(type(executed_result), BinaryShare)

        new_order = make_sell_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            num_shares = executed_result.share_amount
        )

        executed_result = execute_order(new_order)

        self.assertEqual(type(executed_result), float)
        self.assertEqual(round(user1_account.fund, 3), 100.0)

    def test_portfolio_browse(self):
        self.prediction_market.activate()

        user1_account = self.user1.account
        user1_account.get_fund(100.0)

        new_order = make_buy_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            fund = 50.0
        )

        executed_result = execute_order(new_order)

        self.assertEqual(round(user1_account.portfolios.all().first().average_buying_price, 3), 0.6)
    
    def test_get_entire_market_snapshots(self):

        self.prediction_market.activate()
        user1_account = self.user1.account
        user1_account.get_fund(100.0)

        new_order = make_buy_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            fund = 50.0
        )

        executed_result = execute_order(new_order)
        
        time.sleep(1)

        new_order = make_sell_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            num_shares = executed_result.share_amount
        )

        executed_result = execute_order(new_order)
        
        time.sleep(1)

        new_order = make_buy_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 1,
            fund = 20.0
        )

        executed_result = execute_order(new_order)

        time.sleep(1)

        new_order = make_buy_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 0,
            fund = 30.0
        )

        executed_result = execute_order(new_order)

        time.sleep(2)

        new_order = make_sell_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 1,
            num_shares = 20.0
        )

        executed_result = execute_order(new_order)

        time.sleep(2)

        new_order = make_sell_order(
            market = self.prediction_market,
            ordering_account = user1_account,
            share_option = 1,
            num_shares = 20.0
        )

        executed_result = execute_order(new_order)

        snapshots = view_entire_market_snapshot(self.prediction_market)

        print((snapshots['snapshots'][list(snapshots['snapshots'].keys())[0]]['timestamp']).timestamp())
        print(list(snapshots['snapshots'].keys())[0])
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