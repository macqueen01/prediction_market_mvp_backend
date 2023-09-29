
class MarketMakerInterface(object):

    def __init__(self, 
                 initial_fund, 
                 cap_price, 
                 initial_positive_probability, 
                 initial_negative_probability
                 ):
        pass 

    def price_calculate(self, share):
        raise NotImplementedError()
    
    def add_fund_to_positive_then_calculate_shares(self, fund):
        raise NotImplementedError()
    
    def remove_fund_from_positive_then_calculate_shares(self, shares):
        raise NotImplementedError()
    
    def add_fund_to_negative_then_calculate_shares(self, fund):
        raise NotImplementedError()
    
    def remove_fund_from_negative_then_calculate_shares(self, shares):
        raise NotImplementedError()
    