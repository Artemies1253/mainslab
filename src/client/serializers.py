from rest_framework import serializers

from src.client.models import Client


class UploadClientFromFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        good_format = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if value.content_type == good_format:
            return value
        else:
            raise serializers.ValidationError("Формат файла должен быть xlsx")


class ClientListSerializer(serializers.ModelSerializer):
    count_organization = serializers.IntegerField()
    all_income = serializers.FloatField()

    class Meta:
        model = Client
        fields = ("name", "count_organization", "all_income")
