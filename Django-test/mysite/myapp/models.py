from django.db import models

# Create your models here.
from django.db import models

class Company(models.Model):
    stockid = models.CharField(max_length=20, unique=True)
    abbreviation = models.CharField(max_length=50)
    url = models.URLField(max_length=200)
    industryname = models.CharField(max_length=100)

    class Meta:
        db_table = "company"
