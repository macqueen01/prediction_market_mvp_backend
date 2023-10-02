from datetime import timezone
from django.db import models

from main.MarketMakers.shares import SHARE_TYPE_BY_MARKET_TYPE, Share
from main.Models.AccountModel import Account
from main.Models.PredictionMarketModel import PredictionMarket


class Order(models.Model):
    market = models.ForeignKey(PredictionMarket, on_delete=models.CASCADE)
    ordering_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    order_type = models.IntegerField(default = 0)
    share_option = models.IntegerField(default = 0)

    num_shares = models.FloatField(default = 0)
    fund = models.FloatField(default = 0)

    created_at = models.DateTimeField(auto_now_add = True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    is_rejected = models.IntegerField(default = 0)

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
                                                              share = self.order_content['shares'],
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

def execute_order(order: Order) -> Share | float:
    """
    Executes the order and updates the state of the market
    """
    assert(order.market.is_active == 1)

    exchanged_asset: Share | float = None

    if order.is_buy():
        if order.share_option == 0:
            exchanged_asset = order.market.buy_positive(order.fund)
        elif order.share_option == 1:
            exchanged_asset = order.market.buy_negative(order.fund)
        else:
            order.reject()
            raise ValueError('Invalid share option')
    elif order.is_sell():
        exchanged_asset = order.market.sell(order.order_content['shares'])
    else:
        order.reject()
        raise ValueError('Invalid order type')

    order.resolve_order(exchanged_asset)
    return exchanged_asset
    


