from fastapi import status
from app.exceptions.customExceptions.CustomException import CustomException

class ClientError(CustomException):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message, status_code)


class NotFoundError(ClientError):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_404_NOT_FOUND)
