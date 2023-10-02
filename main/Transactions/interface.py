# Transaction is a struct to be used in transaction business logic.
# Transaction fires user actions in most of business logics.

class TransactionInterface(object):

    
    def __init__(self, type):
        self.type = type
        pass