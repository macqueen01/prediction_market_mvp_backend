from django.utils import timezone
from django.db import models

from main.MarketMakers.shares import SHARE_TYPE_BY_MARKET_TYPE, Share
from main.Models.AccountModel import Account
from main.Models.PredictionMarketModel import PredictionMarket

class OrderManager(models.Manager):
    def _create_order(self, 
                     market: PredictionMarket, 
                     ordering_account: Account, 
                     order_type: int, 
                     share_option: int):
        order = self.create(
            market = market,
            ordering_account = ordering_account,
            order_type = order_type,
            share_option = share_option
        )
        order.save()
        return order
    
    def create_buy_order(self, 
                         market: PredictionMarket, 
                         ordering_account: Account, 
                         share_option: int, 
                         fund: float):
        order = self._create_order(
            market = market,
            ordering_account = ordering_account,
            order_type = 0,
            share_option = share_option
        )
        order.fund = fund
        order.save()
        return order
    
    def create_sell_order(self, 
                          market: PredictionMarket, 
                          ordering_account: Account, 
                          share_option: int, 
                          num_shares: float):
        order = self._create_order(
            market = market,
            ordering_account = ordering_account,
            order_type = 1,
            share_option = share_option
        )
        order.num_shares = num_shares
        order.save()
        return order
class Order(models.Model):
    market = models.ForeignKey(PredictionMarket, on_delete=models.CASCADE)
    ordering_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    # buy (order_type == 0) or sell (order_type == 1)
    order_type = models.IntegerField(default = 0)
    share_option = models.IntegerField(default = 0)

    num_shares = models.FloatField(default = 0)
    fund = models.FloatField(default = 0)

    created_at = models.DateTimeField(auto_now_add = True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    is_rejected = models.IntegerField(default = 0)

    objects = OrderManager()

    def is_waiting(self) -> bool:
        if self.resolved_at is None and self.is_rejected == 0:
            return True
        return False
    
    def is_resolved(self) -> bool:
        if self.resolved_at is not None and self.is_rejected == 0:
            return True
        return False
    
    def is_buy(self) -> bool:
        if self.order_type == 0:
            return True
        return False
    
    def is_sell(self) -> bool:
        if self.order_type == 1:
            return True
        return False
    
    def reject(self) -> None:
        self.is_rejected = 1
        self.save()

    def resolve_order(self, exchanged_asset: Share | float) -> None:
        # transfer of shares and funds to & from the account
        # should be called after the share pool has been updated (after the market order execution)
        if type(exchanged_asset) == float:
            assert(self.is_sell())
            # fund transfer and portfolio update (decrease shares, increase funds)
            self.ordering_account.get_fund(fund = exchanged_asset)
            self.ordering_account.remove_share_from_portfolio(market = self.market, 
                                                              share = self.order_content()['shares'],
                                                              fund_received=exchanged_asset)
            
        else:
            assert(self.is_buy())
            # fund transfer and portfolio update (decrease funds, increase shares)
            self.ordering_account.withdraw_fund(fund = self.fund)
            self.ordering_account.add_share_to_portfolio(market = self.market,
                                                         share = exchanged_asset,
                                                         fund_spent = self.fund)
        self.resolved_at = timezone.now()
        self.save()

    def order_content(self) -> dict:
        if (self.is_buy()):
            return {
                'market': self.market,
                'order_type': 'buy',
                'share_option': self.share_option,
                'fund': self.fund
            }
        else:
            return {
                'market': self.market,
                'order_type': 'sell',
                'shares': SHARE_TYPE_BY_MARKET_TYPE.get(
                    self.market.market_maker.market_maker_type)(
                        share_type = self.share_option,
                        share_amount = self.num_shares
                    )
            }



