from django.db.models import Min, F, ExpressionWrapper, IntegerField, Case, When, Value, OuterRef, Subquery

from main.models import *
from django.utils import timezone

from datetime import datetime


def browse_markets() -> models.QuerySet:
    return PredictionMarket.objects.all()

def search_markets(request):
    pass

def create_market(
        title: str, 
        description: str, 
        start_date: datetime, 
        end_date: datetime, 
        settings: MarketSettings) -> PredictionMarket:
    return PredictionMarket.objects.create_market(
        title = title,
        description = description,
        start_date = start_date,
        end_date = end_date,
        settings = settings
    )

def add_thumbnail_to_market(image: Image.Image, market: PredictionMarket):
    market.set_thumbnail(image)
    return market

def get_market_by_id(id: int) -> PredictionMarket:
    return PredictionMarket.objects.get_market_by_id(id)

def make_buy_order(
        market: PredictionMarket, 
        ordering_account: Account, 
        share_option: int, 
        fund: float) -> Order:
    return Order.objects.create_buy_order(
        market = market,
        ordering_account = ordering_account,
        share_option = share_option,
        fund = fund
    )

def make_sell_order(
        market: PredictionMarket, 
        ordering_account: Account, 
        share_option: int, 
        num_shares: float) -> Order:
    return Order.objects.create_sell_order(
        market = market,
        ordering_account = ordering_account,
        share_option = share_option,
        num_shares = num_shares
    )

def execute_order(order: Order) -> Share | float:
    """
    Executes the order and updates the state of the market
    """
    assert(order.market.is_active == 1)

    exchanged_asset: Share | float = None

    if order.is_buy():
        if order.share_option == 0:
            exchanged_asset = order.market.buy_positive(order.fund)
        elif order.share_option == 1:
            exchanged_asset = order.market.buy_negative(order.fund)
        else:
            order.reject()
            raise ValueError('Invalid share option')
    elif order.is_sell():
        exchanged_asset = order.market.sell(order.order_content['shares'])
    else:
        order.reject()
        raise ValueError('Invalid order type')

    order.resolve_order(exchanged_asset)
    return exchanged_asset
    

def cancel_order(order: Order) -> None:
    order.reject()
    return

def browse_portfolio_of_account(account: Account) -> models.QuerySet:
    return account.portfolios.all()

def browse_portfolios_of_account_by_market(account: Account, market: PredictionMarket) -> models.QuerySet:
    portfolios = browse_portfolio_of_account(account)
    return portfolios.filter(market = market)

def _portfolio_to_share(portfolio: Portfolio) -> Share:
    share_factory = SHARE_TYPE_BY_MARKET_TYPE.get(portfolio.market.market_maker.market_maker_type)
    shares = share_factory(
        share_type=portfolio.position_index,
        share_amount=portfolio.num_shares
    )
    return shares

def get_estimated_current_share_prices_of_account(account: Account) -> dict:
    portfolios = browse_portfolio_of_account(account)
    share_prices = {}

    for portfolio in portfolios:
        market = portfolio.market
        shares = _portfolio_to_share(portfolio)
        share_prices[market] = market._get_exact_share_prices(shares)

    return share_prices

def get_average_share_buying_prices_of_account(account: Account) -> dict:
    portfolios = browse_portfolio_of_account(account)
    share_prices = {}

    for portfolio in portfolios:
        market = portfolio.market
        share_price = portfolio.average_buying_price
        share_prices[market] = share_price

    return share_prices

def view_portfolio_of_user(request):
    pass

def view_market_history(request):
    pass

def current_market_pool_state(market: PredictionMarket) -> dict:
    pool_state = market.get_current_shares()
    exact_price_per_share = market._get_exact_price_for_single_share()

    for key in exact_price_per_share.keys():
        pool_state[key] = exact_price_per_share[key]
    
    return pool_state

def withdraw_fund_from_account(account: Account, fund: float, bank_account: str, bank_code: str) -> None:
    Account.withdraw_fund(account, fund, bank_account, bank_code)

def _date_period(start_date: datetime, end_date: datetime, num_periods: int):
    assert(num_periods > 0)
    assert(start_date < end_date)

    period_duration = (end_date - start_date) / num_periods

    period_list = []

    for i in range(num_periods):
        period_list.append(start_date + i * period_duration)

    return period_list

def _get_base_period(date_period: list, date: datetime) -> datetime:
    return min([base - date for base in date_period if base > date])

def _trimed_snapshots_by_sub_periods(market: PredictionMarket, start_date: datetime, end_date: datetime, num_sub_intervals: int) -> tuple:
    assert(num_sub_intervals > 0)

    intervals = _date_period(start_date, end_date, num_sub_intervals)

    unique_snapshot_in_sub_period = market.snapshot.get_snapshots().filter(
        period = OuterRef('period')
    ).order_by('id').values('id')[:1]

    sampled_snapshots = market.snapshot.get_snapshots().filter(
        _timestamp__gte = start_date,
        _timestamp__lte = end_date,
    ).annotate(
        period = _get_base_period(intervals, F('_timestamp')),
    ).filter(
        id__in = Subquery(unique_snapshot_in_sub_period)
    ).order_by('_timestamp')

    return sampled_snapshots, intervals

def _snapshots_to_dict(snapshots: models.QuerySet, intervals: list) -> dict:
    intervals = dict.fromkeys(intervals, None)

    for snapshot in snapshots:
        intervals[snapshot.period] = snapshot.to_dict_without_timestamp()
    
    return intervals

def view_entire_market_snapshot(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, start_date, end_date, 50)
    return _snapshots_to_dict(snapshots, intervals)

def view_past_three_months_snapshot(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    current_date = timezone.now()

    # check if the market is older than 3 months
    if (current_date - start_date).days < 90:
        raise ValueError('The market is not older than 3 months')
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, current_date - datetime.timedelta(days=90), end_date, 50)
    return _snapshots_to_dict(snapshots, intervals)


def view_past_one_month_snapshot(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    current_date = timezone.now()

    # check if the market is older than 1 month
    if (current_date - start_date).days < 30:
        raise ValueError('The market is not older than 1 month')
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, current_date - datetime.timedelta(days=30), end_date, 50)
    return _snapshots_to_dict(snapshots, intervals)

def view_past_one_week_snapshot(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    current_date = timezone.now()

    # check if the market is older than 1 week
    if (current_date - start_date).days < 7:
        raise ValueError('The market is not older than 1 week')
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, current_date - datetime.timedelta(days=7), end_date, 50)
    return _snapshots_to_dict(snapshots, intervals)

def view_past_two_days_snapshot(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    current_date = timezone.now()
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, current_date - datetime.timedelta(days=2), end_date, 50)
    return _snapshots_to_dict(snapshots, intervals)

def view_past_one_day_snapshot(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    current_date = timezone.now()
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, current_date - datetime.timedelta(days=1), end_date, 50)
    return _snapshots_to_dict(snapshots, intervals)

def view_past_snapshots_for_markets_younger_than_one_day(market: PredictionMarket) -> dict:
    snapshots = market.snapshot.get_snapshots()
    start_date = snapshots.first()._timestamp
    end_date = snapshots.last()._timestamp
    current_date = timezone.now()

    # check if the market is older than 1 day
    if (current_date - start_date).days > 1:
        raise ValueError('The market is older than 1 day')
    
    snapshots, intervals = _trimed_snapshots_by_sub_periods(market, start_date, end_date, 20)
    return _snapshots_to_dict(snapshots, intervals)
    