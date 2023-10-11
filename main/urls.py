from django.urls import path, include

from main.views import *

urlpatterns = [
    path('markets/browse/', get_entire_markets),
    path('make-dummy/', make_dummy_market_and_users),
]
