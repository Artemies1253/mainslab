from django.urls import path

from src.client.api import UploadClientFromFileAPIView, ClientListAPIView

urlpatterns = [

    path("upload_from_file", UploadClientFromFileAPIView.as_view()),
    path("list", ClientListAPIView.as_view())
]
