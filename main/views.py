from collections import defaultdict
from main.CoreLogics.main import *

from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view


from main.serializers import MarketBrowseSerializer, MultiplePortfolioSerialize, SinglePortfolioSerializer

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

@api_view(['GET'])
def get_entire_markets(request):
    markets = browse_markets()
    serializer = MarketBrowseSerializer(markets, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_portfolios_of_user(request):
    user_id = int(request.query_params['user_id'])
    user = User.objects.get_user_from_id(user_id)

    if user is None:
        raise exceptions.NotFound(detail="User not found")
    
    user_account = user.account
    portfolios = user_account.portfolios.all()

    serializer = SinglePortfolioSerializer(portfolios, many=True)
    portfolios_by_market_id = MultiplePortfolioSerialize(serializer)

    account = {}
    account['usable_cash'] = user.account.fund
    account['portfolios'] = portfolios_by_market_id

    return Response(account, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_portfolios_by_user_and_market(request):
    user_id = int(request.query_params['user_id'])
    market_id = int(request.query_params['market_id'])

    user = User.objects.get_user_from_id(user_id)
    market = PredictionMarket.objects.get_market_by_id(market_id)

    if (user is None) or (market is None):
        raise exceptions.NotFound(detail="User or market not found")

    portfolios = user.account.portfolios.filter(market__id = market_id)

    serializer = SinglePortfolioSerializer(portfolios, many=True)
    portfolios_by_market_id = MultiplePortfolioSerialize(serializer)

    return Response({portfolios: portfolios_by_market_id}, status=status.HTTP_200_OK)

@api_view(['POST'])
def buy_shares(request):
    user_id = int(request.data['user_id'])
    market_id = int(request.data['market_id'])
    share_option = int(request.data['share_option'])
    fund = float(request.data['fund'])

    user = User.objects.get_user_from_id(user_id)
    market = PredictionMarket.objects.get_market_by_id(market_id)

    if (user is None) or (market is None):
        raise exceptions.NotFound(detail="User or market not found")

    user_account = user.account

    try:
        new_order = make_buy_order(
            market = market,
            ordering_account = user_account,
            share_option = share_option,
            fund = fund
        )

        executed_result = execute_order(new_order)
    except:
        raise exceptions.ValidationError(detail="Not enough fund")

    return Response({'contracted_amount' : executed_result}, status=status.HTTP_200_OK)



@api_view(['GET'])
def buy_dummy(request):
    user1, is_created = User.objects.get_or_create(username="test_user1")

    user1_account = user1.account
    
    user1_account.get_fund(100.0)

    market = browse_markets().first()

    new_order = make_buy_order(
            market = market,
            ordering_account = user1_account,
            share_option = 0,
            fund = 50.0
        )

    executed_result = execute_order(new_order)

    return Response({'contracted_amount' : executed_result}, status=status.HTTP_200_OK)