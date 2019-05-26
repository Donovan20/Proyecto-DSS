from django.db import models

class PIB(models.Model):
    periodo = models.IntegerField(max_length=5)
    frecuencia = models.DecimalField(max_digits=10, decimal_places=4)

class Dolar(models.Model):
    periodo = models.IntegerField(max_length=5)
    frecuencia = models.DecimalField(max_digits=10, decimal_places=4)


