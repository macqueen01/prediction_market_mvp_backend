
from typing import Dict
from main.MarketMakers.shares import Share


class MarketMakerInterface(object):

    def __init__(self, 
                 initial_fund, 
                 cap_price, 
                 initial_positive_probability, 
                 initial_negative_probability
                 ):
        pass 

    def price_calculate(self, shares) -> float:
        raise NotImplementedError()
    
    def estimated_price_for_single_share(self) -> dict:
        raise NotImplementedError()
    
    def price_for_single_share(self) -> dict:
        raise NotImplementedError()
    
    def add_fund_to_positive_then_calculate_shares(self, fund: float) -> Dict[str, float | Share]:
        raise NotImplementedError()
    
    def remove_fund_from_positive_then_calculate_shares(self, shares: Share) -> Dict[str, float]:
        raise NotImplementedError()
    
    def add_fund_to_negative_then_calculate_shares(self, fund: float) -> Dict[str, float | Share]:
        raise NotImplementedError()
    
    def remove_fund_from_negative_then_calculate_shares(self, shares: Share) -> Dict[str, float]:
        raise NotImplementedError()
    
    def get_num_shares(self) -> dict:
        raise NotImplementedError()
    
    def set_num_shares(self, num_positive: float, num_negative: float) -> dict:
        raise NotImplementedError()
    