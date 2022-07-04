from django.db import models

from src.client.models import Client, Organization


class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент", related_name="bills")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, verbose_name="Организация", related_name="bills"
    )
    number = models.PositiveIntegerField(verbose_name="Номер чека в определенной организации")
    value = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Общая стоимость чека")
    date = models.DateField(verbose_name="Дата выпуска чека")
    service = models.CharField(max_length=255, verbose_name="Оказанная услуга")
    service_class = models.IntegerField(
        verbose_name="Идентификатор класса услуги")  # TODO По задания это должено быть поле, но я бы сделал это отдельной таблицей
    service_name = models.CharField(max_length=255, verbose_name="Название сервиса")
    fraud_score = models.FloatField(default=0, verbose_name="Достоверность чека")

    class Meta:
        unique_together = ('organization', 'number')
