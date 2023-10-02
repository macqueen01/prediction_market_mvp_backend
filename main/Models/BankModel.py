from django.db import models

# Bank is a Singleton that calls the BankModel
# This BankModel should be used to store the bank's information
# and be created only once in the database and called by the Bank singleton only.

class BankModel(models.Model):
    # total balance is the sum of the reserved balance, the liquidity balance, and the uncategorized balance
    total_balance = models.FloatField(default = 0)

    # Asset allocated to reserved pools
    reserved_balance = models.FloatField(default = 0)
    # Asset allocated to accounts
    liquidity_balance = models.FloatField(default = 0)
    # Asset not allocated to any pool or account
    # Any asset if not specified should be uncategorized
    uncategorized_balance = models.FloatField(default = 0)

    def safe_check(self):
        if (self.total_balance != self.reserved_balance + self.liquidity_balance + self.uncategorized_balance):
            raise False
        return True
    
    

    class Meta:
        db_table = 'bank'


class Bank(object):
    _instance = None
    _bank = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Bank, cls).__new__(cls)
            cls._bank = BankModel.objects.get_or_create(id = 1)[0]
        return cls._instance
    
    def _safe_check(self):
        if self._bank is None:
            raise False
        
        # financial diagnostics
        return self._bank.safe_check()

    def get_total_balance(self):
        return self._bank.total_balance
    
    def get_reserved_balance(self):
        return self._bank.reserved_balance
    
    def get_liquidity_balance(self):
        return self._bank.liquidity_balance


    def _add_total_balance(self, amount):
        self._bank.total_balance += amount
        self._bank.save()
        return self._bank.total_balance
    
    def _add_uncategorized_balance(self, amount):
        self._bank.uncategorized_balance += amount
        self._bank.save()
        return self._bank.uncategorized_balance
    
    def _add_liquidity_balance(self, amount):
        self._bank.liquidity_balance += amount
        self._bank.save()
        return self._bank.liquidity_balance
    
    def _add_reserved_balance(self, amount):
        self._bank.reserved_balance += amount
        self._bank.save()
        return self._bank.reserved_balance
    
    def _subtract_uncaategorized_balance(self, amount):
        self._bank.uncategorized_balance -= amount
        self._bank.save()
        return self._bank.uncategorized_balance

    def _subtract_liquidity_balance(self, amount):
        self._bank.liquidity_balance -= amount
        self._bank.save()
        return self._bank.liquidity_balance
    
    def _subtract_reserved_balance(self, amount):
        self._bank.reserved_balance -= amount
        self._bank.save()
        return self._bank.reserved_balance
    
    # Asset transfer methods
    # these methods can be called from outside

    def uncategorized_to_liquidity(self, amount):
        if (amount < 0):
            return False
        
        if (self._bank.uncategorized_balance < amount):
            return False

        if self._safe_check() is False:
            return False

        self._subtract_uncaategorized_balance(amount)
        self._add_liquidity_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.uncategorized_balance, self._bank.liquidity_balance
    

    def liquidity_to_uncategorized(self, amount):
        if (amount < 0):
            return False
        
        if (self._bank.liquidity_balance < amount):
            return False

        if self._safe_check() is False:
            return False

        self._subtract_liquidity_balance(amount)
        self._add_uncategorized_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.liquidity_balance, self._bank.uncategorized_balance
    
    def uncategorized_to_reserved(self, amount):
        if (amount < 0):
            return False
        
        if (self._bank.uncategorized_balance < amount):
            return False

        if self._safe_check() is False:
            return False

        self._subtract_uncaategorized_balance(amount)
        self._add_reserved_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.uncategorized_balance, self._bank.reserved_balance
    
    def reserved_to_uncategorized(self, amount):
        if (amount < 0):
            return False
        
        if (self._bank.reserved_balance < amount):
            return False

        if self._safe_check() is False:
            return False

        self._subtract_reserved_balance(amount)
        self._add_uncategorized_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.reserved_balance, self._bank.uncategorized_balance
    
    def liquidity_to_reserved(self, amount):
        if (amount < 0):
            return False
        
        if (self._bank.liquidity_balance < amount):
            return False

        if self._safe_check() is False:
            return False

        self._subtract_liquidity_balance(amount)
        self._add_reserved_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.liquidity_balance, self._bank.reserved_balance
    

    def reserved_to_liquidity(self, amount):
        if (amount < 0):
            return False
        
        if (self._bank.reserved_balance < amount):
            return False

        if self._safe_check() is False:
            return False

        self._subtract_reserved_balance(amount)
        self._add_liquidity_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.reserved_balance, self._bank.liquidity_balance
    
    def add_to_bank_through_uncategorized(self, amount):
        """
        This method should only be called when adding 
        additional asset to the bank.
        When successfully added, the amount of asset is allocated to 
        the uncategorized balance.
        """

        if (amount < 0):
            return False
        
        if self._safe_check() is False:
            return False

        self._add_total_balance(amount)
        self._add_uncategorized_balance(amount)
        
        if self._safe_check() is False:
            return False

        return self._bank.total_balance
    
    def subtract_from_bank_through_uncategorized(self, amount):
        """
        This method should only be called when subtracting
        asset from the bank.
        When successfully subtracted, the amount of asset is subtracted from 
        the uncategorized balance.

        Important: This method only subtracts from uncategorized balance.
        """

        if (amount < 0):
            return False
        
        if (self._bank.uncategorized_balance < amount):
            return False
        
        if self._safe_check() is False:
            return False
        
        self._subtract_uncaategorized_balance(amount)
        self._subtract_uncaategorized_balance(amount)

        if self._safe_check() is False:
            return False
        
        return self._bank.total_balance
    
    def checkout(self, amount):
        """
        Checkouts the given amount of asset out of the liquidity balance.
        This wll be used by the account model to checkout asset from the bank.
        """

        if (amount < 0):
            return False
        
        self.liquidity_to_uncategorized(amount)
        return self.subtract_from_bank_through_uncategorized(amount)
    
    
    