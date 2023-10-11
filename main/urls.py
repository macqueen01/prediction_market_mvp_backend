from django.urls import path, include

from main.views import *

urlpatterns = [
    path('markets/browse/', get_entire_markets),
    path('markets/portfolios/', get_portfolios_of_user, name='get_portfolios_of_user'),

    # Dummy rest call for testing
    path('make-dummy/', make_dummy_market_and_users),
    path('buy-dummy/', buy_dummy),
]
