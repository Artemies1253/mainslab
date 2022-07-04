from django.urls import path, include

urlpatterns = [
    path("bill/", include("src.bill.urls")),
    path("client/", include("src.client.urls"))
]
