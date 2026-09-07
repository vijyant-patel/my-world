from django.core.management.base import BaseCommand
from cricket.models import Tournament, Team, Player, Match
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate the database with sample IPL 2026 data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting sample data generation...")

        # Create Tournament
        tournament, created = Tournament.objects.get_or_create(
            name="IPL 2026",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60)
        )

        # Create Teams
        teams_data = [
            ("Chennai Super Kings", "CSK"),
            ("Mumbai Indians", "MI"),
            ("Royal Challengers Bangalore", "RCB"),
            ("Kolkata Knight Riders", "KKR"),
            ("Delhi Capitals", "DC"),
        ]
        
        teams = {}
        for name, short_name in teams_data:
            team, _ = Team.objects.get_or_create(name=name, short_name=short_name)
            teams[short_name] = team

        # Create Players
        players_data = {
            "CSK": [("MS Dhoni", "Wicket-Keeper"), ("Ruturaj Gaikwad", "Batsman"), ("Ravindra Jadeja", "All-Rounder")],
            "MI": [("Rohit Sharma", "Batsman"), ("Jasprit Bumrah", "Bowler"), ("Suryakumar Yadav", "Batsman")],
            "RCB": [("Virat Kohli", "Batsman"), ("Glenn Maxwell", "All-Rounder"), ("Mohammed Siraj", "Bowler")],
        }

        for team_sn, players in players_data.items():
            team = teams[team_sn]
            for player_name, role in players:
                Player.objects.get_or_create(name=player_name, team=team, role=role, batting_style="Right Hand")

        # Create Matches
        match1 = Match.objects.create(
            tournament=tournament,
            team1=teams["CSK"],
            team2=teams["MI"],
            match_date=timezone.now() - timedelta(days=1),
            venue="Wankhede Stadium, Mumbai",
            match_type=Match.MatchType.T20,
            status=Match.MatchStatus.COMPLETED,
            winner=teams["CSK"]
        )

        match2 = Match.objects.create(
            tournament=tournament,
            team1=teams["RCB"],
            team2=teams["KKR"],
            match_date=timezone.now() + timedelta(days=1),
            venue="M. Chinnaswamy Stadium, Bengaluru",
            match_type=Match.MatchType.T20,
            status=Match.MatchStatus.UPCOMING
        )
        
        match3 = Match.objects.create(
            tournament=tournament,
            team1=teams["MI"],
            team2=teams["DC"],
            match_date=timezone.now(),
            venue="Arun Jaitley Stadium, Delhi",
            match_type=Match.MatchType.T20,
            status=Match.MatchStatus.ONGOING
        )

        self.stdout.write(self.style.SUCCESS("Successfully populated IPL 2026 sample data!"))
