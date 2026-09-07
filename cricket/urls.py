from django.urls import path
from . import views

app_name = 'cricket'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Teams
    path('teams/', views.team_list, name='teams'),
    path('teams/add/', views.TeamCreateView.as_view(), name='team_add'),
    path('teams/<int:pk>/edit/', views.TeamUpdateView.as_view(), name='team_edit'),
    path('teams/<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),

    # Players
    path('players/', views.player_list, name='players'),
    path('players/add/', views.PlayerCreateView.as_view(), name='player_add'),
    path('players/<int:pk>/edit/', views.PlayerUpdateView.as_view(), name='player_edit'),
    path('players/<int:pk>/delete/', views.PlayerDeleteView.as_view(), name='player_delete'),

    # Matches
    path('matches/', views.match_list, name='matches'),
    path('matches/add/', views.MatchCreateView.as_view(), name='match_add'),
    path('matches/<int:pk>/edit/', views.MatchUpdateView.as_view(), name='match_edit'),
    path('matches/<int:pk>/delete/', views.MatchDeleteView.as_view(), name='match_delete'),

    # Betting
    path('betting/', views.betting_history, name='betting'),
    path('betting/add/', views.BetHistoryCreateView.as_view(), name='betting_add'),
    path('betting/<int:pk>/delete/', views.BetHistoryDeleteView.as_view(), name='betting_delete'),
]
