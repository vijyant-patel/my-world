from django.db import models
from django.conf import settings
class Tournament(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='teams/', null=True, blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    role = models.CharField(max_length=50, choices=[('Batsman', 'Batsman'), ('Bowler', 'Bowler'), ('All-Rounder', 'All-Rounder'), ('Wicket-Keeper', 'Wicket-Keeper')])
    batting_style = models.CharField(max_length=50, null=True, blank=True)
    bowling_style = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.team.short_name})"

class Match(models.Model):
    class MatchType(models.TextChoices):
        T20 = 'T20', 'T20'
        ODI = 'ODI', 'ODI'
        TEST = 'Test', 'Test'
        
    class MatchStatus(models.TextChoices):
        UPCOMING = 'Upcoming', 'Upcoming'
        ONGOING = 'Ongoing', 'Ongoing'
        COMPLETED = 'Completed', 'Completed'

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    match_type = models.CharField(max_length=10, choices=MatchType.choices, default=MatchType.T20)
    status = models.CharField(max_length=20, choices=MatchStatus.choices, default=MatchStatus.UPCOMING)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')

    def __str__(self):
        return f"{self.team1.short_name} vs {self.team2.short_name} on {self.match_date.date()}"

class Inning(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='innings')
    batting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='batting_innings')
    bowling_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bowling_innings')
    total_runs = models.IntegerField(default=0)
    total_wickets = models.IntegerField(default=0)
    overs_played = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)

    def __str__(self):
        return f"{self.batting_team.short_name} Inning - {self.match}"

class Delivery(models.Model):
    inning = models.ForeignKey(Inning, on_delete=models.CASCADE, related_name='deliveries')
    over_number = models.IntegerField()
    ball_number = models.IntegerField()
    bowler = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='balls_bowled')
    batsman = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='balls_faced')
    runs = models.IntegerField(default=0)
    extras = models.IntegerField(default=0)
    is_wicket = models.BooleanField(default=False)

    def __str__(self):
        return f"Over {self.over_number}.{self.ball_number} - {self.bowler.name} to {self.batsman.name}"

class BetHistory(models.Model):
    class BetType(models.TextChoices):
        MATCH = 'Match', 'Full Match'
        OVER = 'Over', 'Over-based'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bets')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets')
    bet_type = models.CharField(max_length=20, choices=BetType.choices, default=BetType.MATCH)
    over_number = models.IntegerField(null=True, blank=True, help_text="Over number if bet is over-based")
    stake = models.DecimalField(max_digits=10, decimal_places=2)
    odds = models.DecimalField(max_digits=5, decimal_places=2)
    predicted_value = models.CharField(max_length=255, help_text="What the user predicted (e.g., 'Team A wins', '15 runs in over')")
    actual_value = models.CharField(max_length=255, null=True, blank=True, help_text="The actual outcome")
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def settle(self):
        """
        Settles the bet based on its type.
        For 'Match' type, it checks if the predicted_value matches the match winner.
        For 'Over' type, actual_value must be filled manually or by another system, then we check if it matches predicted_value.
        """
        if self.bet_type == self.BetType.MATCH:
            if self.match.status != self.Match.MatchStatus.COMPLETED:
                return # Cannot settle uncompleted match
            
            if self.match.winner and self.match.winner.short_name.lower() == self.predicted_value.lower():
                self.actual_value = self.match.winner.short_name
                self.profit_loss = self.stake * self.odds - self.stake
            else:
                self.actual_value = self.match.winner.short_name if self.match.winner else "Draw/NR"
                self.profit_loss = -self.stake
            self.save()
            
        elif self.bet_type == self.BetType.OVER:
            if not self.actual_value:
                return # Needs actual value to settle over bets
                
            if self.actual_value.lower() == self.predicted_value.lower():
                self.profit_loss = self.stake * self.odds - self.stake
            else:
                self.profit_loss = -self.stake
            self.save()

    def __str__(self):
        return f"Bet by {self.user} on {self.match} - Stakes: {self.stake}"
