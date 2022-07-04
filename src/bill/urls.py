from django.urls import path

from src.bill.api import UploadBillFromFileAPIView, ListBillAPIView

urlpatterns = [
    path("upload_from_file", UploadBillFromFileAPIView.as_view()),
    path("list", ListBillAPIView.as_view())
]
