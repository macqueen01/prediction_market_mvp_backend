from main.CoreLogics.main import *

from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view


from main.serializers import MarketBrowseSerializer

# ONLY FOR TEST USE !
# REMOVE THIS IN PRODUCTION

@api_view(['GET'])
def make_dummy_market_and_users(request):
        settings = MarketSettings(
            100, 1, 0.5, 0.5, True, True
        )

        # Create a test PredictionMarket instance
        prediction_market = PredictionMarket.objects.create_market(
            title="2024년 대한민국 22대 총선의 다수당은 민주당이 될 것이다",
            description="여러 조건과 다양한 설명 첨부 필요",
            start_date=timezone.now(),
            end_date  = timezone.now() + timezone.timedelta(days=365),
            settings=settings
        )

        user1, is_created = User.objects.get_or_create(username="test_user1")
        user2, is_created = User.objects.get_or_create(username="test_user2")

        reserve_pool = prediction_market.reserve_pool

        prediction_market.activate()

        serializer = MarketBrowseSerializer(prediction_market)

        return Response(serializer.data, status=status.HTTP_200_OK)

# END OF TEST USE

@api_view(['GET', 'OPTIONS'])
def get_entire_markets(request):
    markets = browse_markets()
    serializer = MarketBrowseSerializer(markets, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
