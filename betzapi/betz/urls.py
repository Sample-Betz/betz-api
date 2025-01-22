from django.urls import path

from betz.views import betz_views
from betz.views import nba_views

urlpatterns = [    
    # BETZ
    path('betz/hello', betz_views.hello_world, name='betz'),
    
    # ESPN
    
    # NBA
    path('betz/nba/props', nba_views.player_props, name='nba'),
]