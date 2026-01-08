from fastapi import status

class CustomException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.status_code = status_code
        self.message = message
        super().__init__(message)