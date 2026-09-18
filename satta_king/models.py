from django.db import models

class DailyNumber(models.Model):
    CATEGORY_CHOICES = [
        ('DSWR', 'DSWR'),
        ('DLBZ', 'DLBZ'),
        ('SRGN', 'SRGN'),
        ('FRBD', 'FRBD'),
        ('GZBD', 'GZBD'),
        ('GALI', 'GALI'),
    ]

    index_num = models.IntegerField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    number = models.IntegerField()

    class Meta:
        unique_together = ('index_num', 'category')
        ordering = ['index_num']

    def __str__(self):
        return f"Index {self.index_num} - {self.category}: {self.number}"
