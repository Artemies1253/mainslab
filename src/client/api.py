from django.db.models import Sum, Count
from rest_framework import generics
from rest_framework.response import Response
from django.db import transaction

from src.client.models import Client
from src.client.serializers import UploadClientFromFileSerializer, ClientListSerializer
from src.client.services import create_clients_from_file


class UploadClientFromFileAPIView(generics.GenericAPIView):
    serializer_class = UploadClientFromFileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            create_clients_from_file(serializer.validated_data.get("file"))
            return Response({"success": True})


class ClientListAPIView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    queryset = Client.objects.all().annotate(
        count_organization=Count("clientorganization"),
        all_income=Sum("clientorganization__organization__bills__value"),
    )
