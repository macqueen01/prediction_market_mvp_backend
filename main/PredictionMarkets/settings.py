
class MarketSettings(object):
    def __init__(self, 
                 initial_fund, 
                 cap_price, 
                 initial_positive_probability, 
                 initial_negative_probability,
                 is_binary = True,
                 is_constant_product = True):
                
        self.initial_fund = initial_fund
        self.cap_price = cap_price
        self.initial_positive_probability = initial_positive_probability
        self.initial_negative_probability = initial_negative_probability
        self.num_positive = initial_fund / cap_price
        self.num_negative = initial_fund / cap_price

        if (is_binary and is_constant_product):
            self.market_maker_type = 'binary_constant_product'
        else:
            raise NotImplementedError('Only binary constant product market maker is supported at the moment')
