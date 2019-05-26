from django.db import models

class PIB(models.Model):
    periodo = models.IntegerField(max_length=5)
    frecuencia = models.DecimalField(max_digits=10)

class Dolar(models.Model):
    periodo = models.IntegerField(max_length=5)
    frecuencia = models.DecimalField(max_digits=10)


