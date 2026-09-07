from django.contrib import admin
from .models import Tournament, Team, Player, Match, Inning, Delivery, BetHistory

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    search_fields = ('name', 'short_name')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'role')
    list_filter = ('team', 'role')
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'match_date', 'venue', 'status', 'match_type', 'winner')
    list_filter = ('status', 'match_type', 'tournament')
    search_fields = ('team1__name', 'team2__name', 'venue')
    actions = ['settle_match_bets']

    @admin.action(description='Settle all Match-type bets for selected matches (only if completed)')
    def settle_match_bets(self, request, queryset):
        bets_settled = 0
        for match in queryset.filter(status=Match.MatchStatus.COMPLETED):
            for bet in match.bets.filter(bet_type=BetHistory.BetType.MATCH):
                bet.settle()
                bets_settled += 1
        self.message_user(request, f"{bets_settled} bet(s) settled successfully.")

@admin.register(Inning)
class InningAdmin(admin.ModelAdmin):
    list_display = ('match', 'batting_team', 'bowling_team', 'total_runs', 'total_wickets')
    list_filter = ('batting_team', 'bowling_team')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('inning', 'over_number', 'ball_number', 'bowler', 'batsman', 'runs', 'is_wicket')
    list_filter = ('is_wicket',)
    search_fields = ('bowler__name', 'batsman__name')

@admin.register(BetHistory)
class BetHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'bet_type', 'stake', 'odds', 'profit_loss')
    list_filter = ('bet_type', 'user')
    search_fields = ('match__team1__name', 'match__team2__name', 'user__username')
    actions = ['settle_selected_bets']

    @admin.action(description='Settle selected bets')
    def settle_selected_bets(self, request, queryset):
        for bet in queryset:
            bet.settle()
        self.message_user(request, f"{queryset.count()} bet(s) processed for settlement.")
