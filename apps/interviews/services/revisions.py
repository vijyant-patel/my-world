from datetime import timedelta
from django.utils import timezone
from apps.interviews.models import RevisionTracker

class RevisionService:
    @staticmethod
    def process_revision(revision_tracker: RevisionTracker, quality: int):
        """
        Process a revision using a simplified SuperMemo-2 (SM-2) algorithm.
        quality: 0-5 (0=blackout, 5=perfect response)
        """
        if quality < 3:
            # Failed to recall
            revision_tracker.revision_streak = 0
            revision_tracker.interval_days = 1
        else:
            # Successfully recalled
            if revision_tracker.revision_streak == 0:
                revision_tracker.interval_days = 1
            elif revision_tracker.revision_streak == 1:
                revision_tracker.interval_days = 6
            else:
                revision_tracker.interval_days = round(revision_tracker.interval_days * revision_tracker.ease_factor)
            
            revision_tracker.revision_streak += 1

        # Update ease factor (min 1.3)
        revision_tracker.ease_factor = max(
            1.3,
            revision_tracker.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )

        revision_tracker.last_revised_date = timezone.now().date()
        revision_tracker.next_revision_date = revision_tracker.last_revised_date + timedelta(days=revision_tracker.interval_days)
        
        # Update Question status if mastery is achieved (e.g., interval > 21 days)
        if revision_tracker.interval_days > 21:
            revision_tracker.question.status = 'mastered'
            revision_tracker.question.save()

        revision_tracker.save()
        return revision_tracker
