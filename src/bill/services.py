import django.db
import pyexcel
from django.core.files import File
from typing import List
from datetime import datetime
import random

from src.base.exceptions import ValidationError, CustomError
from src.bill.models import Bill
from src.client.models import Client, Organization

SERVICES_DICT = {"1": "консультация", "2": "лечение", "3": "стационар", "4": "диагностика", "5": "лаборатория"}

VARIATION_NAMES_DICT = {
    "client_name": ["client_name", "client"],
    "organization_name": ["client_org", "organization", "org"],
    "number_bill": ["№", "bill_number", "number"],
    "value": ["sum", "total_sum", "total"],
    "created_date": ["date", "created_date", "created"],
    "service": ["service", "service_name"]
}


def fraud_detector(service: str) -> float:
    """Определяет правильность чека и выдаёт вероятность от 0 до 1"""
    return round(random.random(), 1)


def service_classifier(service: str) -> dict:
    """Определяет сервис класс сервиса и отдаёт его в виде словаря"""
    service_class = random.randint(1, 5)
    service_name = SERVICES_DICT.get(str(service_class))
    return {"service_class": service_class, "service_name": service_name}


def get_valida_field_name(field: str):
    """Преобразует имя поля клиента в валидное имя поля хранящееся в системе"""
    for validata_name, options in VARIATION_NAMES_DICT.items():
        if field in options:
            return validata_name


def get_fields_index_dict(list_fields: list):
    """Отдаёт словарь ключа которого является имя валидного поля хранящееся в система, а значение индекс в list_fields
    """
    fields_index_dict = {
        "client_name": None,
        "organization_name": None,
        "number_bill": None,
        "value": None,
        "created_date": None,
        "service": None,
    }
    for i, field in enumerate(list_fields):
        valida_field = get_valida_field_name(field)
        if valida_field:
            fields_index_dict[valida_field] = i
    return fields_index_dict


def bill_data_is_empty(bill_data: list):  # TODO Переписать через цикл
    """Если все значения списка пусты, то возвращает True"""
    client_name, created_date, number_bill, organization_name, service, value = bill_data
    if not client_name and not created_date and not number_bill and not organization_name and not service and not value:
        return True


def get_correct_bills_data(bills_data: List[list]):
    fields_index_dict = get_fields_index_dict(bills_data[0])
    correct_bills_data = []
    for i, bill_data in enumerate(bills_data):
        if i == 0:
            continue
        if bill_data_is_empty(bill_data):
            continue
        correct_bills_data.append(
            {
                "client_name": bill_data[fields_index_dict["client_name"]],
                "organization_name": bill_data[fields_index_dict["organization_name"]],
                "number_bill": bill_data[fields_index_dict["number_bill"]],
                "value": bill_data[fields_index_dict["value"]],
                "created_date": bill_data[fields_index_dict["created_date"]],
                "service": bill_data[fields_index_dict["service"]],
                "index_in_file": i + 1
            }
        )
    return correct_bills_data


def validate_bills_data(bills_data):
    bills_list_unique_values = []
    for bill_data in bills_data:
        value = bill_data.get("value")
        if isinstance(value, float) or (isinstance(value, int)):
            pass
        else:
            raise ValidationError(
                f"Не корректное значение поля value в строке {bill_data.get('index_in_file')} - {value}"
            )

        service = bill_data.get("service")
        if not service or service == "-":
            raise ValidationError(
                f"Поля сервиса не может быть пустым {bill_data.get('index_in_file')} - {service}"
            )

        created_date = bill_data.get("created_date")
        if not isinstance(created_date, datetime):
            raise ValidationError(
                f"Не корректное значение поля даты чека в строке {bill_data.get('index_in_file')} - {created_date}"
            )

        number_bill = bill_data.get("number_bill")
        if not isinstance(number_bill, int):
            raise ValidationError(
                f"Номер чека должен быть числом {bill_data.get('index_in_file')} - {number_bill}"
            )
        client_name = bill_data.get("client_name")
        if not client_name or client_name == "-":
            raise ValidationError(
                f"Имя клиента не может быть пусто {bill_data.get('index_in_file')} - {client_name}"
            )
        organization_name = bill_data.get("organization_name")
        if not organization_name or organization_name == "-":
            raise ValidationError(
                f"Название организации не может быть пусто в строке {bill_data.get('index_in_file')} - {organization_name}"
            )
        number_bill = bill_data.get("number_bill")
        unique_value = (organization_name, number_bill)
        if unique_value in bills_list_unique_values:
            raise ValidationError(
                f"Значение {unique_value} повторяется в строках "
                f"{bills_list_unique_values.index(unique_value) + 2} и {bill_data.get('index_in_file')}"
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


def create_bills(correct_bills_data: List[dict]):
    """Создание чеков"""
    for bill_data in correct_bills_data:
        client = Client.objects.filter(name=bill_data.get("client_name"))
        organization = Organization.objects.filter(name=bill_data.get("organization_name"))
        if organization.exists() and client.exists():
            organization = organization.first()
            try:
                service = bill_data.get("service")
                fraud_score = fraud_detector(service)
                service_info = service_classifier(service)

                Bill.objects.create(
                    client=client.first(),
                    organization=organization,
                    number=bill_data.get("number_bill"),
                    value=bill_data.get("value"),
                    date=bill_data.get("created_date"),
                    service=bill_data.get("service"),
                    service_class=service_info.get("service_class"),
                    service_name=service_info.get("service_name"),
                    fraud_score=fraud_score
                )
                if fraud_score >= 0.9:
                    organization.fraud_weight += 1
                    organization.save()
            except django.db.IntegrityError:

                pass


def create_bills_from_file(file: File):
    """Создание чеков из файла форматом xlsx"""
    try:
        book_dict = pyexcel.get_book_dict(file_type="xlsx", file_content=file.file)
    except Exception:
        raise ValidationError("Файл испорчен")
    try:
        bills_data = book_dict["Лист1"]
    except Exception:
        raise ValidationError("Информация о чеках должна содержаться в листи с насваением Лист1")
    try:
        correct_bills_data = get_correct_bills_data(bills_data)
        validate_bills_data(correct_bills_data)
        create_bills(correct_bills_data)
    except Exception as ex:
        raise CustomError(f"{ex}")
