from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Rating(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    reviewer = models.ForeignKey(
        'accounts.Users',
        on_delete=models.CASCADE,
        related_name='ratings_given',
    )
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    rated_jobseeker = models.ForeignKey(
        'accounts.JobSeeker',
        on_delete=models.CASCADE,
        related_name='ratings_received',
        null=True, blank=True,
    )
    rated_employer = models.ForeignKey(
        'accounts.Employer',
        on_delete=models.CASCADE,
        related_name='ratings_received',
        null=True, blank=True,
    )
    score = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'ratings'
        unique_together = ('reviewer', 'application', 'rated_jobseeker', 'rated_employer')
        ordering = ['-created_at']

    def __str__(self):
        target = self.rated_jobseeker or self.rated_employer
        return f"{self.reviewer.username} → {target} | {self.score}★"

    @property
    def star_range(self):
        return range(1, self.score + 1)

    @property
    def empty_star_range(self):
        return range(self.score + 1, 6)