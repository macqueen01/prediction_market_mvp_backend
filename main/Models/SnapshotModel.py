from django.db import models
from django.utils import timezone

class Snapshot(models.Model):
    market_type = models.CharField(max_length = 120, default = 'binary_constant_product')
    
    def get_market_type(self) -> str:
        return self.market_type
    
    def get_snapshots(self) -> models.QuerySet:
        return SNAPSHOT_TYPE.get(self.market_type).objects.filter(snapshots = self).order_by('-_timestamp')
    
    def record_snapshot(self, **kwargs: dict):
        for key in SNAPSHOT_ARGUMENT_CHECK.get(self.market_type):
            if key not in kwargs:
                raise Exception(f'Argument {key} not found')
            
        kwargs['snapshots'] = self
            
        snapshot = SNAPSHOT_TYPE.get(self.market_type).objects.create(**kwargs)
        return snapshot
        

class BinarySnapshotManager(models.Manager):
    def create(self, **kwargs):
        positive_shares = kwargs.get('positive_shares')
        negative_shares = kwargs.get('negative_shares')
        positive_market_size = kwargs.get('positive_market_size')
        negative_market_size = kwargs.get('negative_market_size')
        snapshots = kwargs.get('snapshots')
        
        binary_snapshot = self.model(
            snapshots = snapshots,
            _positive = positive_shares,
            _negative = negative_shares,
            _positive_market_size = positive_market_size,
            _negative_market_size = negative_market_size,
            _timestamp = timezone.now()
        )
        binary_snapshot.save()
        return binary_snapshot


class BinarySnapshot(models.Model):

    snapshots = models.ForeignKey(Snapshot, on_delete = models.CASCADE, related_name='binary_snapshots')

    _positive = models.FloatField(default = 0)
    _negative = models.FloatField(default = 0)

    _positive_market_size = models.FloatField(default = 0)
    _negative_market_size = models.FloatField(default = 0)
    _timestamp = models.DateTimeField(auto_now_add = True)

    objects = BinarySnapshotManager()


    def to_dict_without_timestamp(self) -> dict:
        return {
            'positive_shares': self._positive,
            'negative_shares': self._negative,
            'positive_market_size': self._positive_market_size,
            'negative_market_size': self._negative_market_size,
        }
    
    def to_dict(self) -> dict:
        return {
            'positive_shares': self._positive,
            'negative_shares': self._negative,
            'positive_market_size': self._positive_market_size,
            'negative_market_size': self._negative_market_size,
            'timestamp': self._timestamp
        }

    def get_positive_shares(self) -> float: 
        return self._positive
    
    def get_negative_shares(self) -> float:
        return self._negative
    
    def get_total_shares(self) -> float:
        return self._positive + self._negative
    
    def get_positive_market_size(self) -> float:
        return self._positive_market_size
    
    def get_negative_market_size(self) -> float:
        return self._negative_market_size
    
    def get_total_market_size(self) -> float:
        return self._positive_market_size + self._negative_market_size
    
    def get_timestamp(self) -> timezone.datetime:
        return self._timestamp
    
    def __str__(self) -> str:
        return f'snapshot at {self._timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
    
    def __repr__(self) -> str:
        return self.__str__()


SNAPSHOT_TYPE = {
    'binary_constant_product': BinarySnapshot,
}

SNAPSHOT_ARGUMENT_CHECK = {
    'binary_constant_product': ['positive_shares', 'negative_shares', 'positive_market_size', 'negative_market_size']
}