from .shares import BinaryShare, Share
from .interface import MarketMakerInterface

from main.utils import equationroots

class ConstantProductMarketMaker(MarketMakerInterface):
    
    def __init__(self, initial_fund: float, cap_price: float, initial_positive_probability = None, initial_negative_probability = None):
        self.initial_fund = initial_fund
        self.cap_price = cap_price
        self.num_positive = initial_fund / cap_price
        self.num_negative = initial_fund / cap_price
        # Constant product market maker is a binary market maker
        # that holds the product of num_positive and num_negative constant
        self.constant = self.num_positive * self.num_negative
    
    def price_calculate(self, share: Share):
        assert(type(share) == BinaryShare)

        if share.share_type == 'positive':
            num_positive = self.num_positive + share.share_amount
            num_negative = self.num_negative
            
        else:
            num_positive = self.num_positive
            num_negative = self.num_negative + share.share_amount

        delta_price = min(equationroots(1, - (num_positive + num_negative), num_positive * num_negative - self.constant))
        
        return delta_price
    
    def price_calculate_based_on_probabilities(self, shares: Share) -> float:
        assert(type(shares) == BinaryShare)

        if shares.share_type == 'positive':
            price_rate = self.num_negative / (self.num_positive + self.num_negative)
        else:
            price_rate = self.num_positive / (self.num_positive + self.num_negative)
        
        return price_rate * self.cap_price * shares.share_amount


    def add_fund_to_positive_then_calculate_shares(self, fund: float):
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
    
    def remove_fund_from_positive_then_calculate_shares(self, shares: Share):
        assert(type(shares) == BinaryShare)
        assert(shares.share_type == 'positive')

        num_positive = self.num_positive + shares.share_amount
        num_negative = self.num_negative
        delta_price = self.price_calculate(shares)

        new_positive_shares = num_positive - delta_price
        new_negative_shares = num_negative - delta_price
        
        return {
            'positive_shares': new_positive_shares,
            'negative_shares': new_negative_shares,
            'returned_fund': delta_price
        }
    

    def add_fund_to_negative_then_calculate_shares(self, fund: float):
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
    
    def remove_fund_from_negative_then_calculate_shares(self, shares: Share):
        assert(type(shares) == BinaryShare)
        assert(shares.share_type == 'negative')

        num_positive = self.num_positive
        num_negative = self.num_negative + shares.share_amount
        delta_price = self.price_calculate(shares)

        new_positive_shares = num_positive - delta_price
        new_negative_shares = num_negative - delta_price
        
        return {
            'positive_shares': new_positive_shares,
            'negative_shares': new_negative_shares,
            'returned_fund': delta_price
        }
    

    def set_num_shares(self, num_positive, num_negative):
        self.num_positive = num_positive
        self.num_negative = num_negative
        return self.get_num_shares()
    
    def get_num_shares(self):
        return {
            'positive_shares': self.num_positive,
            'negative_shares': self.num_negative
        }
    



        
    

