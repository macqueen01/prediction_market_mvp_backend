from django.db import models

from main.MarketMakers.shares import SHARE_TYPE_BY_MARKET_TYPE, Share

from .PredictionMarketModel import PredictionMarket

class PortfolioManager(models.Manager):
    def create_portfolio(self, 
                         market: PredictionMarket, 
                         position_index: int, 
                         num_shares: float, 
                         buying_price: float):
        portfolio = self.create(
            market = market,
            position_index = position_index,
            num_shares = num_shares,
            average_buying_price = buying_price,
        )
        portfolio.save()
        return portfolio

class Portfolio(models.Model):
    market = models.ForeignKey(PredictionMarket, on_delete = models.CASCADE, related_name = 'portfolios')
    position_index = models.IntegerField(default = 0)
    num_shares = models.FloatField(default = 0)
    average_buying_price = models.FloatField(default = 0)
    

    objects = PortfolioManager()

    def _recalculate_buying_price(self,
                                  incomming_num_shares: float, 
                                  incomming_price: float,
                                  outgoing_num_shares: float,
                                  outgoing_price: float) -> None:
        
        net_num_shares = incomming_num_shares - outgoing_num_shares
        net_price = incomming_price - outgoing_price

        total_num_shares = self.num_shares + net_num_shares
        total_price = self.average_buying_price * self.num_shares + net_price

        if (total_price == 0 or total_num_shares == 0):
            self.average_buying_price = 0
            self.num_shares = 0
            self.save()
            return

        self.average_buying_price = total_price / total_num_shares
        self.num_shares = total_num_shares

        self.save()
        return 
    
    def add_shares(self, num_shares: float, price_bought: float) -> None:
        self._recalculate_buying_price(num_shares, price_bought, 0, 0)
        return
    
    def remove_shares(self, num_shares: float, price_sold: float) -> None:
        self._recalculate_buying_price(0, 0, num_shares, price_sold)
        
        if (self.num_shares == 0):
            self.delete()
    
        return
    
    def get_num_shares(self) -> float:
        return self.num_shares
    
    def get_current_value(self) -> float:
        share : Share = SHARE_TYPE_BY_MARKET_TYPE.get(self.market.market_maker.market_maker_type)(share_type=self.position_index, share_amount=self.num_shares)
        price = self.market._get_exact_share_prices(share)['returned_fund']
        price = round(price, 3)

        return price



     

