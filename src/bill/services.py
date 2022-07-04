import django.db
import pyexcel
from django.core.files import File
from typing import List

import random

from src.base.exceptions import ValidationError
from src.bill.models import Bill
from src.client.models import Client, Organization

SERVICES_DICT = {"1": "консультация", "2": "лечение", "3": "стационар", "4": "диагностика", "5": "лаборатория"}


def fraud_detector(service: str) -> float:
    """Определяет правильность чека и выдаёт вероятность от 0 до 1"""
    return round(random.random(), 1)


def service_classifier(service: str) -> dict:
    """Определяет сервис класс сервиса и отдаёт его в виде словаря"""
    service_class = random.randint(1, 5)
    service_name = SERVICES_DICT.get(str(service_class))
    return {"service_class": service_class, "service_name": service_name}


def validate_bills_data_on_unique_values(bills_data):
    bills_list_unique_values = []
    for i, bill_data in enumerate(bills_data):
        client_name, client_org, number_bill, value, date, service = bill_data
        unique_value = (client_org, number_bill)
        if unique_value in bills_list_unique_values:
            raise ValidationError(
                f"Значение {unique_value} повторяется в строках "
                f"{bills_list_unique_values.index(unique_value) + 1} и {i + 1}"
            )
        else:
            bills_list_unique_values.append(unique_value)


def get_validate_bills_data(bills_data: list) -> List[dict]:
    """Валидирует и дополняет информацию по чекам"""
    correct_bills_list = []
    for bill_data in bills_data:
        client_name, client_org, number_bill, value, date, service = bill_data
        if not client_name or client_name == "client_name":
            continue
        fraud_score = fraud_detector(service)
        service_info = service_classifier(service)
        bill_info = {
            "client_name": client_name,
            "client_org": client_org,
            "number_bill": number_bill,
            "value": value,
            "date": date,
            "service": service,
            "service_class": service_info.get("service_class"),
            "service_name": service_info.get("service_name"),
            "fraud_score": fraud_score
        }
        correct_bills_list.append(bill_info)
    return correct_bills_list


def create_bills(validate_bills_data: List[dict]):
    for validate_bill_data in validate_bills_data:
        client = Client.objects.filter(name=validate_bill_data.get("client_name"))
        organization = Organization.objects.filter(name=validate_bill_data.get("client_org"))
        if organization.exists() and client.exists():
            organization = organization.first()
            try:
                Bill.objects.create(
                    client=client.first(),
                    organization=organization,
                    number=validate_bill_data.get("number_bill"),
                    value=validate_bill_data.get("value"),
                    date=validate_bill_data.get("date"),
                    service=validate_bill_data.get("service"),
                    service_class=validate_bill_data.get("service_class"),
                    service_name=validate_bill_data.get("service_name"),
                    fraud_score=validate_bill_data.get("fraud_score")
                )
                if validate_bill_data.get("fraud_score") >= 0.9:
                    organization.fraud_weight += 1
                    organization.save()
            except django.db.IntegrityError:
                pass


def create_bills_from_file(file: File):
    book_dict = pyexcel.get_book_dict(file_type="xlsx", file_content=file.file)
    bills_data = book_dict["Лист1"]
    validate_bills_data_on_unique_values(bills_data)
    validate_bills_data = get_validate_bills_data(bills_data)
    create_bills(validate_bills_data)
