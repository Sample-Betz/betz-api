from django.urls import path

from betz.views import betz_views
from betz.views import espn_views

urlpatterns = [    
    # BETZ
    path('betz/moneyline', betz_views.moneyline, name='betz'),
    
    # ESPN
    path('espn/win-percentage', espn_views.win_percentage, name='espn'),
    path('espn/schedule', espn_views.schedule, name='espn'),
]