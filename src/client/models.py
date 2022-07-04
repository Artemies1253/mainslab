from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Имя клиента")

    def __str__(self):
        return f"Клиент {self.name}"


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Имя организации")
    address = models.CharField(max_length=255, null=True, verbose_name="Адрес организации")
    fraud_weight = models.PositiveIntegerField(default=0, verbose_name="Количество бракованных счетов")

    def __str__(self):
        return f"Организация {self.name}"


class ClientOrganization(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="organizations")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="clients")

    class Meta:
        unique_together = ('client', 'organization')
