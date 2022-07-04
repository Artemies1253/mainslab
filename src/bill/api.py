from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response

from src.bill.filters import BillListFilter
from src.bill.models import Bill
from src.bill.serializers import UploadBillFromFileSerializer, DetailBillSerializer
from src.bill.services import create_bills_from_file


class UploadBillFromFileAPIView(generics.GenericAPIView):
    serializer_class = UploadBillFromFileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            create_bills_from_file(serializer.validated_data.get("file"))
            return Response({"success": True})

        return Response({"success": False})


class ListBillAPIView(generics.ListAPIView):
    serializer_class = DetailBillSerializer
    queryset = Bill.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BillListFilter
