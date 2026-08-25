from fastapi import HTTPException
from typing import Any

class BadRequestException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=400, detail=f'Bad Request: {extra}' if extra else 'Bad Request')

class InternalServerErrorException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=500, detail=f'Internal Server Error: {extra}' if extra else 'Internal Server Error')

class UnauthorizedException(HTTPException):
    def __init__(self, extra: Any = None, headers={"WWW-Authenticate": "Basic"}):
        super().__init__(status_code=401, detail=f'Unauthorized: {extra}' if extra else 'Unauthorized',
                         headers=headers)

class ForbiddenException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=403, detail=f'Forbidden: {extra}' if extra else 'Forbidden')

class NotFoundException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=404, detail=f'Not Found: {extra}' if extra else 'Not Found')

class MethodNotAllowedException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=405, detail=f'Method Not Allowed: {extra}' if extra else 'Method Not Allowed')

class RequestTimeoutException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=408, detail=f'Request Timeout: {extra}' if extra else 'Request Timeout')

class ConflictException(HTTPException):
    def __init__(self, extra: Any = None):
        super().__init__(status_code=409, detail=f'Conflict: {extra}' if extra else 'Conflict')