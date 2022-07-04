from random import randint

import pyexcel
from django.core.files import File

from src.base.exceptions import ValidationError
from src.client.models import Client, Organization, ClientOrganization


def validate_clients_data_on_unique_values(clients_data: list):
    clients_list_unique_values = []
    for i, client_data in enumerate(clients_data):
        for name in client_data:
            if name in clients_list_unique_values:
                raise ValidationError(
                    f"Значение {name} повторяется в строках "
                    f"{clients_list_unique_values.index(name) + 1} и {i + 1}"
                )
            else:
                clients_list_unique_values.append(name)


def validate_organization_data_on_unique_values(bills_data: list):
    orfanization_list_unique_values = []
    for i, organization_data in enumerate(bills_data):
        client_name, name, address = organization_data
        unique_value = (client_name, name)
        if unique_value in orfanization_list_unique_values:
            raise ValidationError(
                f"Значение {unique_value} повторяется в строках "
                f"{orfanization_list_unique_values.index(unique_value) + 1} и {i + 1}"
            )
        else:
            orfanization_list_unique_values.append(unique_value)


def create_clients(clients_data: list):
    for client_data in clients_data:
        for name in client_data:
            if name == "name":
                continue
            Client.objects.get_or_create(name=name)


def create_organization(organizations_data: list):
    for organization_data in organizations_data:
        client_name, name, address = organization_data
        if not client_name or client_name == "client_name":
            continue

        if address:
            address = f"Адрес: {address}"
        organization = Organization.objects.get_or_create(name=name, address=address)[0]
        client = Client.objects.get_or_create(name=client_name)[0]  # TODO Я могу создать тут клиента или нет?
        ClientOrganization.objects.get_or_create(organization=organization, client=client)


def create_clients_from_file(file: File):
    book_dict = pyexcel.get_book_dict(file_type="xlsx", file_content=file.file)
    clients_data = book_dict["client"]
    validate_clients_data_on_unique_values(clients_data)
    create_clients(clients_data)
    organization_data = book_dict["organization"]
    validate_organization_data_on_unique_values(organization_data)
    create_organization(organization_data)
