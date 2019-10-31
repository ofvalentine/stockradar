from django.db import models
from django.contrib.postgres.fields import ArrayField


class Headline(models.Model):
    source = models.CharField(max_length=25)
    headline = models.TextField(primary_key=True)
    keywords = ArrayField(models.TextField(), blank=True)
    fetched_on = models.DateTimeField()
    link = models.TextField()

    class Meta:
        db_table = 'headlines'

    def __str__(self):
        return self.headline
