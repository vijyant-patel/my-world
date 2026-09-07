from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Match, Player, Team, BetHistory

def dashboard(request):
    upcoming_matches = Match.objects.filter(status=Match.MatchStatus.UPCOMING).order_by('match_date')[:5]
    ongoing_matches = Match.objects.filter(status=Match.MatchStatus.ONGOING).order_by('-match_date')
    recent_matches = Match.objects.filter(status=Match.MatchStatus.COMPLETED).order_by('-match_date')[:5]
    
    # Calculate total bets
    if request.user.is_authenticated:
        user_bets = BetHistory.objects.filter(user=request.user)
        total_staked = sum(bet.stake for bet in user_bets)
        total_profit = sum(bet.profit_loss for bet in user_bets if bet.profit_loss is not None)
    else:
        user_bets = None
        total_staked = 0
        total_profit = 0

    context = {
        'upcoming_matches': upcoming_matches,
        'ongoing_matches': ongoing_matches,
        'recent_matches': recent_matches,
        'user_bets': user_bets,
        'total_staked': total_staked,
        'total_profit': total_profit,
    }
    return render(request, 'cricket/dashboard.html', context)

def match_list(request):
    matches = Match.objects.all().order_by('-match_date')
    return render(request, 'cricket/matches.html', {'matches': matches})

def team_list(request):
    teams = Team.objects.all()
    return render(request, 'cricket/teams.html', {'teams': teams})

def player_list(request):
    players = Player.objects.all().select_related('team')
    return render(request, 'cricket/players.html', {'players': players})

def betting_history(request):
    if request.user.is_authenticated:
        bets = BetHistory.objects.filter(user=request.user).select_related('match')
    else:
        bets = None
    return render(request, 'cricket/betting.html', {'bets': bets})

# --- Teams CRUD ---

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    fields = ['name', 'short_name', 'logo']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:teams')

class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    fields = ['name', 'short_name', 'logo']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:teams')

class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = 'cricket/confirm_delete.html'
    success_url = reverse_lazy('cricket:teams')

# --- Players CRUD ---

class PlayerCreateView(LoginRequiredMixin, CreateView):
    model = Player
    fields = ['name', 'team', 'role', 'batting_style', 'bowling_style']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:players')

class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    fields = ['name', 'team', 'role', 'batting_style', 'bowling_style']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:players')

class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    model = Player
    template_name = 'cricket/confirm_delete.html'
    success_url = reverse_lazy('cricket:players')

# --- Matches CRUD ---

class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    fields = ['tournament', 'team1', 'team2', 'match_date', 'venue', 'match_type', 'status', 'winner']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:matches')

class MatchUpdateView(LoginRequiredMixin, UpdateView):
    model = Match
    fields = ['tournament', 'team1', 'team2', 'match_date', 'venue', 'match_type', 'status', 'winner']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:matches')

class MatchDeleteView(LoginRequiredMixin, DeleteView):
    model = Match
    template_name = 'cricket/confirm_delete.html'
    success_url = reverse_lazy('cricket:matches')

# --- Betting CRUD ---

class BetHistoryCreateView(LoginRequiredMixin, CreateView):
    model = BetHistory
    fields = ['match', 'bet_type', 'over_number', 'stake', 'odds', 'predicted_value']
    template_name = 'cricket/form.html'
    success_url = reverse_lazy('cricket:betting')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BetHistoryDeleteView(LoginRequiredMixin, DeleteView):
    model = BetHistory
    template_name = 'cricket/confirm_delete.html'
    success_url = reverse_lazy('cricket:betting')

