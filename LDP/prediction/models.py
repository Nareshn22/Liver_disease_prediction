

from django.db import models
from datetime import datetime
from django.utils import timezone


class Prediction(models.Model):
    age = models.FloatField()
    direct_bilirubin = models.FloatField()
    alkaline_phosphotase = models.FloatField()
    alamine_aminotransferase = models.FloatField()
    aspartate_aminotransferase = models.FloatField()
    total_proteins = models.FloatField()
    albumin = models.FloatField()
    albumin_and_globulin_ratio = models.FloatField()
    gender_female = models.FloatField()
    gender_male = models.FloatField()
    prediction = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return f'Prediction {self.id}'

