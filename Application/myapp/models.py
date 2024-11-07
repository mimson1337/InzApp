from django.db import models
from django.utils import timezone


class AudioFile(models.Model):
    url = models.URLField(null=True, blank=True)  # URLs
    local_file = models.FileField(upload_to='audio/', null=True, blank=True)  # Local file
    transcription_text = models.TextField()
    duration = models.FloatField()
    related_to_depression = models.BooleanField(default=False)
    found_keywords = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Set default value for existing rows

    def __str__(self):
        return self.url or self.local_file.name
