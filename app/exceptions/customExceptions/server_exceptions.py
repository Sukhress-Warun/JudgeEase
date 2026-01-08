from fastapi import status
from app.exceptions.customExceptions.CustomException import CustomException

class ServerError(CustomException):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message, status_code)