from rest_framework.exceptions import APIException
from rest_framework import status


from loguru import logger
from django.conf import settings

class CustomError(APIException):
    def __init__(self, error_message: str, code: str = "server_error"):
        """Базовый класс для создания собственных ошибок
        """
        logger.add(
            f"{settings.BASE_DIR}/src/logs/error.log",
            format="{time} {level} {message}",
            level="ERROR",
            rotation="1 MB",
            compression="zip",
            encoding="utf-8"
        )
        self.code = code
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.errors_list = []
        logger.error(error_message)
        self.detail = {"error": error_message}


class ValidationError(CustomError):
    def __init__(self, error_message: str):
        self.code = "validation_error"
        super().__init__(error_message, code=self.code)
        self.status_code = status.HTTP_400_BAD_REQUEST
