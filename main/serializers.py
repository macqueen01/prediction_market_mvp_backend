from django.forms import ImageField
from rest_framework import serializers

from main.Models.PredictionMarketModel import PredictionMarket

class MarketBrowseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(max_length=4000)
    start_date = serializers.DateTimeField()
    end_date = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    is_active = serializers.IntegerField()

    thumbnail = serializers.SerializerMethodField()
    pool_state = serializers.SerializerMethodField()
    past_pool_state = serializers.SerializerMethodField()
    is_resolved = serializers.SerializerMethodField()

    
    def get_pool_state(self, obj):
        return obj.get_current_shares()
    
    def get_thumbnail(self, obj):
        try:
            url = obj.thumbnail.url.split('?')[0]
            return url
        except:
            return None
    
    def get_end_date(self, obj):
        if obj.end_date is None:
            return None
        return serializers.DateTimeField().to_representation(obj.end_date)
    
    def get_past_pool_state(self, obj):
        snapshot = obj.get_snapshot_a_day_ago()

        if snapshot is None:
            return obj.get_current_shares()
        
        return snapshot.to_dict_without_timestamp()
    
    def get_is_resolved(self, obj):
        return obj.is_resolved()
    

    class Meta:
        model = PredictionMarket
        fields = (
                'id', 
                'title', 
                'description', 
                'start_date', 
                'end_date', 
                'created_at', 
                'is_active', 
                'thumbnail', 
                'pool_state', 
                'past_pool_state',
                'is_resolved'
                )
        
class SinglePortfolioSerializer(serializers.ModelSerializer):
    position_index = serializers.IntegerField()
    num_shares = serializers.FloatField()
    average_price = serializers.FloatField()

    market_id = serializers.SerializerMethodField()
    market_title = serializers.SerializerMethodField()
    market_image = serializers.SerializerMethodField()  
    current_price = serializers.SerializerMethodField()
    probability_of_share_type = serializers.SerializerMethodField()
    max_future_resolve_value_per_share = serializers.SerializerMethodField()
    min_future_resolve_value_per_share = serializers.SerializerMethodField()

    def get_market_id(self, obj):
        return obj.market.id
    
    def get_market_title(self, obj):
        return obj.market.title
    
    def get_market_image(self, obj):
        try:
            url = obj.market.thumbnail.url.split('?')[0]
            return url
        except:
            return None
        
    def get_current_price(self, obj):
        return obj.get_current_value()
    
    def get_probability_of_share_type(self, obj):
        reserve_pool = obj.market.reserve_pool
        share_type = reserve_pool.get_share_options()[self.position_index]
        probability = reserve_pool.get_probability_of_share_type(share_type)
        parsed_probability = round(probability, 3)
        return parsed_probability
    
    def get_max_future_resolve_value_per_share(self, obj):
        return obj.market.market_maker.cap_price
    
    def get_min_future_resolve_value_per_share(self, obj):
        return 0
    
    class Meta:
        model = PredictionMarket
        fields = (
            'position_index',
            'num_shares',
            'average_price',
            'market_id',
            'market_title',
            'market_image',
            'current_price',
            'probability_of_share_type',
            'max_future_resolve_value_per_share',
            'min_future_resolve_value_per_share'
        )


    
