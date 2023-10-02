from .interface import TransactionInterface


class MarketTransaction(TransactionInterface):
    
    def __init__(self):
        self.type = 'market'
        self.order_type = None
        pass
        
