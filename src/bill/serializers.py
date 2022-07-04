from rest_framework import serializers

from src.bill.models import Bill


class UploadBillFromFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        good_format = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if value.content_type == good_format:
            return value
        else:
            raise serializers.ValidationError("Формат файла должен быть xlsx")


class DetailBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"
