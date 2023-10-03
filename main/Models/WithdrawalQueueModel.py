from django.db import models
from django.utils import timezone

class WithdrawalQueueManager(models.Manager):
    def create_withdrawal(self, amount: float, bank_account: str, bank_code: str):
        withdrawal = self.create(
            withdrawal_amount = amount,
            withdrawing_bank_account = bank_account,
            withdrawing_bank_code = bank_code
        )
        withdrawal.save()
        return withdrawal
    
    def get_waiting_withdrawals(self):
        return self.filter(is_processed = 0, rejected = 0).order_by('created_at')
    
    def get_completed_withdrawals(self):
        return self.filter(is_processed = 1, rejected = 0).order_by('created_at')
    
    def get_rejected_withdrawals(self):
        return self.filter(rejected = 1).order_by('created_at')
    
    def withdrawal_process_complete(self, withdrawals: models.QuerySet):
        for withdrawal in withdrawals:
            withdrawal.process()
        return
    
    def reject_withdrawals(self, withdrawals: models.QuerySet):
        for withdrawal in withdrawals:
            withdrawal.reject()
        return


class WithdrawalQueue(models.Model):
    withdrawal_amount = models.FloatField(default = 0)
    is_processed = models.IntegerField(default = 0)
    rejected = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    processed_at = models.DateTimeField(auto_now_add = True)
    withdrawing_bank_account = models.CharField(default = '', max_length = 120)
    withdrawing_bank_code = models.CharField(default = '', max_length = 120)

    def is_waiting(self) -> bool:
        if self.is_processed == 0:
            return True
        return False
        
    def is_rejected(self) -> bool:
        if self.rejected == 1:
            return True
        return False

    def reject(self) -> None:
        self.rejected = 1
        self.is_processed = 1
        self.processed_at = timezone.now()
        self.save()

    def process(self) -> None:
        self.is_processed = 1
        self.processed_at = timezone.now()
        self.save()

    def is_completed(self) -> bool:
        if self.is_processed == 1 and self.rejected == 0:
            return True
        return False
    

