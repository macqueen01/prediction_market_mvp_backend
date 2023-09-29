from .shares import BinaryShare
from .interface import MarketMakerInterface

class ConstantProductMarketMaker(MarketMakerInterface):
    
    def __init__(self, initial_fund, cap_price, initial_positive_probability, initial_negative_probability):
        self.initial_fund = initial_fund
        self.cap_price = cap_price
        self.num_positive = initial_fund / cap_price
        self.num_negative = initial_fund / cap_price
        # Constant product market maker is a binary market maker
        # that holds the product of num_positive and num_negative constant
        self.constant = self.num_positive * self.num_negative
    
    def price_calculate(self, share):
        assert(type(share) == BinaryShare)

        cap_price = self.cap_price * share.share_amount

        if share.share_type == 'positive':
            price_rate = self.num_negative / (self.num_positive + self.num_negative)
            return cap_price * price_rate
        
        price_rate = self.num_negative / (self.num_positive + self.num_negative)
        return cap_price * price_rate

    def add_fund_to_positive_then_calculate_shares(self, fund):
        num_shares = fund / self.cap_price

        num_positive = self.num_positive + num_shares
        num_negative = self.num_negative + num_shares

        new_positive_shares = self.constant / num_negative
        returned_shares = BinaryShare(
            share_type='positive', 
            share_amount=num_positive - new_positive_shares)
        
        return {
            'positive_shares': new_positive_shares,
            'negative_shares': num_negative,
            'returned_shares': returned_shares
        }
    
    def remove_fund_from_positive_then_calculate_shares(self, shares):
        assert(type(shares) == BinaryShare)
        assert(shares.share_type == 'positive')

        estimated_sell_price = self.price_calculate(shares)
        num_shares = estimated_sell_price / self.cap_price

        num_positive = self.num_positive - num_shares
        num_negative = self.num_negative - num_shares

        new_positive_shares = self.constant / num_negative

        return {
            'positive_shares': new_positive_shares,
            'negative_shares': num_negative,
            'returned_fund': estimated_sell_price
        }
    

    def add_fund_to_negative_then_calculate_shares(self, fund):
        num_shares = fund / self.cap_price

        num_positive = self.num_positive + num_shares
        num_negative = self.num_negative + num_shares

        new_negative_shares = self.constant / num_positive
        returned_shares = BinaryShare(
            share_type='negative', 
            share_amount=num_negative - new_negative_shares)
        
        return {
            'positive_shares': num_positive,
            'negative_shares': new_negative_shares,
            'returned_shares': returned_shares
        }
    
    def remove_fund_from_negative_then_calculate_shares(self, shares):
        assert(type(shares) == BinaryShare)
        assert(shares.share_type == 'negative')

        estimated_sell_price = self.price_calculate(shares)
        num_shares = estimated_sell_price / self.cap_price

        num_positive = self.num_positive - num_shares
        num_negative = self.num_negative - num_shares

        new_negative_shares = self.constant / num_positive

        return {
            'positive_shares': num_positive,
            'negative_shares': new_negative_shares,
            'returned_fund': estimated_sell_price
        }
    

    def set_num_shares(self, num_positive, num_negative):
        self.num_positive = num_positive
        self.num_negative = num_negative
        return None
    



        
    

