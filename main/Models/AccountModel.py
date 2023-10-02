from django.db import models
from main.MarketMakers.shares import BinaryShare, Share

from .PortfolioModel import Portfolio, PortfolioManager
from .PredictionMarketModel import PredictionMarket

SHARE_TRANSLATION_BY_SHARE_TYPE = {
    BinaryShare: {
        lambda share: {
            'share_type': 0 if share.share_type == 'positive' else 1,
            'share_amount': share.share_amount
        }
    }
}
class Account(models.Model):
    fund = models.FloatField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    is_active = models.IntegerField(default = 1)

    def activate(self) -> None:
        self.is_active = 1
        self.save()

    def deactivate(self) -> None:
        self.is_active = 0
        self.save()

    def get_fund(self, fund: float) -> None:
        assert(self.is_active == 1)
        self.fund += fund
        self.save()

    def withdraw_fund(self, fund: float) -> None:
        assert(self.is_active == 1)
        assert(self.fund >= fund)
        self.fund -= fund
        self.save()

    def add_share_to_portfolio(self, market: PredictionMarket, share: Share, fund_spent: float):
        share_info = SHARE_TRANSLATION_BY_SHARE_TYPE.get(type(share))(share)
        
        share_type = share_info['share_type']
        share_amount = share_info['share_amount']

        assert(self.is_active == 1)

        portfolio = Portfolio.objects.get_or_create_portfolio(market, share_type, self)
        portfolio.add_shares(num_shares = share_amount, price_bought = fund_spent)

    def remove_share_from_portfolio(self, market: PredictionMarket, share: Share, fund_received: float):
        share_info = SHARE_TRANSLATION_BY_SHARE_TYPE.get(type(share))(share)
        
        share_type = share_info['share_type']
        share_amount = share_info['share_amount']

        assert(self.is_active == 1)

        portfolio = Portfolio.objects.get_or_create_portfolio(market, share_type, self)
        portfolio.remove_shares(num_shares = share_amount, price_sold = fund_received)





