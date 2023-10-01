

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
    
    def __init__(self, share_type, share_amount):
        self.share_type = share_type
        self.share_amount = share_amount
    

