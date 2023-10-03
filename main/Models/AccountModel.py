from django.utils import timezone
from django.db import models
from main.MarketMakers.shares import BinaryShare, Share

from .WithdrawalQueueModel import WithdrawalQueue
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

class AccountManager(models.Manager):
    
    def create_account(self):
        account = self.create(
            fund = 0,
            is_active = 0,
            created_at = timezone.now()
        )
        account.save()
        return account
    
    def transfer_fund(self, from_account, to_account, fund):
        assert(from_account.is_active == 1)
        assert(to_account.is_active == 1)
        assert(from_account.fund >= fund)
        from_account.withdraw_fund(fund)
        to_account.get_fund(fund)
        return
    
    def withdraw_fund(self, account, fund: float, bank_account: str, bank_code: str):
        assert(account.is_active == 1)
        assert(account.fund >= fund)
        # adding the withdrawal request to the queue
        WithdrawalQueue.objects.create_withdrawal(
            amount = fund,
            bank_account = bank_account,
            bank_code = bank_code
        )
        account.withdraw_fund(fund)
        return
    
class Account(models.Model):
    fund = models.FloatField(default = 0)
    portfolios = models.ManyToManyField(Portfolio, blank = True, related_name='account')
    created_at = models.DateTimeField(auto_now_add = True)
    is_active = models.IntegerField(default = 1)

    objects = AccountManager()

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

    def get_portfolio_by_market_and_share_type(self, market: PredictionMarket, share_type: int) -> Portfolio:
        assert(self.is_active == 1)

        query_result = self.portfolios.filter(market = market, share_type = share_type)

        if query_result.exists():
            return query_result.get()
        
        portfolio = Portfolio.objects.create_portfolio(
            market = market, 
            position_index = share_type, 
            num_shares = 0.0, 
            buying_price = 0.0)
        self.portfolios.add(portfolio)
        self.save()
        return portfolio

    def add_share_to_portfolio(self, market: PredictionMarket, share: Share, fund_spent: float):
        share_info = SHARE_TRANSLATION_BY_SHARE_TYPE.get(type(share))(share)
        
        share_type = share_info['share_type']
        share_amount = share_info['share_amount']

        assert(self.is_active == 1)

        portfolio = self.get_portfolio_by_market_and_share_type(market, share_type)
        portfolio.add_shares(num_shares = share_amount, price_bought = fund_spent)

    def remove_share_from_portfolio(self, market: PredictionMarket, share: Share, fund_received: float):
        share_info = SHARE_TRANSLATION_BY_SHARE_TYPE.get(type(share))(share)
        
        share_type = share_info['share_type']
        share_amount = share_info['share_amount']

        assert(self.is_active == 1)

        portfolio = self.get_portfolio_by_market_and_share_type(market, share_type)
        portfolio.remove_shares(num_shares = share_amount, price_sold = fund_received)

    




