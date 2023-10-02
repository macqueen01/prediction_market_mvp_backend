

class Share(object):
    def __init__(self, share_type, share_amount):
        self.share_type = share_type
        self.share_amount = share_amount
    
    def __call__(self) -> dict:
        return {
            'share_type': self.share_type,
            'share_amount': self.share_amount
        }
class BinaryShare(Share):
    def __call__(self) -> dict:
        return {
            'share_type': self.share_type,
            'share_amount': self.share_amount
        }
    
    def __init__(self, share_type: int | str, share_amount: float):
        if type(share_type) == int:
            if share_type == 0:
                share_type = 'positive'
            elif share_type == 1:
                share_type = 'negative'
            else:
                raise ValueError('share_type must be either 1 or 0')
        elif type(share_type) == str:
            if share_type == 'positive' or share_type == 'negative':
                pass
            else:
                raise ValueError('share_type must be either "positive" or "negative"')

        self.share_type = share_type
        self.share_amount = share_amount

class SharePoolState(object):
    def __init__(self, **kwargs):
        pass

class BinarySharePoolState(SharePoolState):
    def __init__(self, **kwargs):
        self.positive_shares = kwargs['positive_shares']
        self.negative_shares = kwargs['negative_shares']
    
    def __call__(self) -> dict:
        return {
            'positive_shares': self.positive_shares,
            'negative_shares': self.negative_shares
        }
    

POOL_STATE_TYPE = {
    'binary_constant_product': BinarySharePoolState
}

SHARE_TYPE_BY_MARKET_TYPE = {
    'binary_constant_product': BinaryShare
}

