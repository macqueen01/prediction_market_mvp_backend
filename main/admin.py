from django.contrib import admin

from main.models import User, Account, ReservePool, PredictionMarket

# Register your models here.

admin.site.site_header = "Prediction Market Admin"
admin.site.register(User)
admin.site.register(Account)
admin.site.register(ReservePool)
admin.site.register(PredictionMarket)