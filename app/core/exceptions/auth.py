"""
Исключения, связанные с аутентификацией, авторизацией и управлением пользователями.

Этот модуль содержит иерархию исключений для обработки различных ошибок,
связанных с процессами аутентификации и авторизации в приложении.

Иерархия исключений:
1. BaseAPIException (основной класс для всех API-исключений)
   └── AuthenticationError (базовый класс для ошибок аутентификации)
       ├── InvalidCredentialsError (неверные учетные данные)
       ├── InvalidEmailFormatError (неверный формат email)
       ├── InvalidPasswordError (неверный пароль)
       ├── WeakPasswordError (слабый пароль)
       └── TokenError (базовый класс для ошибок, связанных с токенами)
           ├── TokenMissingError (отсутствующий токен)
           ├── TokenExpiredError (истекший токен)
           └── TokenInvalidError (недействительный токен)

Все исключения наследуются от BaseAPIException, который предоставляет
общую структуру для HTTP-ответов об ошибках, включая статус-код,
детальное сообщение, тип ошибки и дополнительные данные.

Пример использования:
```python
# Проверка учетных данных пользователя
if not is_valid_credentials(email, password):
    raise InvalidCredentialsError()

# Проверка формата email
if not is_valid_email_format(email):
    raise InvalidEmailFormatError(email)

# Проверка токена
if token_expired(token):
    raise TokenExpiredError()
"""

from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class AuthenticationError(BaseAPIException):
    """
    Базовый класс для всех ошибок, связанных с аутентификацией и авторизацией.

    Этот класс устанавливает код статуса HTTP 401 (Unauthorized) и предоставляет
    базовую структуру для всех исключений, связанных с проверкой подлинности.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки для классификации на стороне клиента.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
        status_code (int): HTTP-код состояния (401 для ошибок аутентификации).
    """

    def __init__(
        self,
        detail: str = "Ошибка аутентификации",
        error_type: str = "authentication_error",
        status_code: int = 401,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AuthenticationError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            error_type (str): Тип ошибки для классификации.
            extra (dict): Дополнительные данные об ошибке.
        """
        super().__init__(
            status_code=status_code,
            detail=detail,
            error_type=error_type,
            extra=extra or {},
        )


class InvalidCredentialsError(AuthenticationError):
    """
    Исключение для неверных учетных данных пользователя.

    Возникает, когда пользователь предоставляет неверные логин или пароль
    при попытке аутентификации.

    Attributes:
        detail (str): Фиксированное сообщение "🔐 Неверный email или пароль".
        error_type (str): "invalid_credentials".
    """

    def __init__(self):
        """
        Инициализирует исключение InvalidCredentialsError с предопределенными значениями.
        """
        super().__init__(
            detail="🔐 Неверный email или пароль",
            error_type="invalid_credentials",
        )


class InvalidEmailFormatError(AuthenticationError):
    """
    Исключение для недействительного формата электронной почты.

    Возникает при попытке использовать строку, не соответствующую формату email.

    Attributes:
        detail (str): Сообщение с указанием недействительного email.
        error_type (str): "invalid_email_format".
        extra (dict): Содержит недействительный email в ключе "email".
    """

    def __init__(self, email: str):
        """
        Инициализирует исключение InvalidEmailFormatError.

        Args:
            email (str): Недействительный email, вызвавший ошибку.
        """
        super().__init__(
            detail=f"Неверный формат email: {email}",
            error_type="invalid_email_format",
            extra={"email": email},
        )


class InvalidPasswordError(AuthenticationError):
    """
    Исключение для неверного пароля.

    Возникает, когда пользователь предоставляет верный идентификатор,
    но неверный пароль при попытке аутентификации.

    Attributes:
        detail (str): "Неверный пароль".
        error_type (str): "invalid_password".
    """

    def __init__(self):
        """
        Инициализирует исключение InvalidPasswordError с предопределенными значениями.
        """
        super().__init__(
            detail="Неверный пароль",
            error_type="invalid_password",
        )


class InvalidCurrentPasswordError(AuthenticationError):
    """
    Исключение для неверного текущего пароля.

    Возникает, когда пользователь предоставляет неверный текущий пароль
    при попытке изменить пароль.

    Attributes:
        detail (str): "Текущий пароль неверен".
        error_type (str): "invalid_current_password".
    """

    def __init__(self):
        """
        Инициализирует исключение InvalidCurrentPasswordError с предопределенными значениями.
        """
        super().__init__(
            detail="Текущий пароль неверен",
            error_type="invalid_current_password",
        )


class WeakPasswordError(AuthenticationError):
    """
    Исключение для слабого пароля.

    Возникает при попытке установить пароль, не соответствующий
    минимальным требованиям безопасности.

    Attributes:
        detail (str): Детальное описание требований к паролю.
        error_type (str): "weak_password".
    """

    def __init__(
        self,
        detail: str = "Пароль должен быть минимум 8 символов, иметь заглавную и строчную букву, цифру, спецсимвол",
    ):
        """
        Инициализирует исключение WeakPasswordError.

        Args:
            detail (str): Детальное описание проблемы с паролем.
        """
        super().__init__(
            detail=detail,
            error_type="weak_password",
        )


class TokenError(AuthenticationError):
    """
    Базовый класс для всех ошибок, связанных с токенами аутентификации.

    Предоставляет общую структуру для ошибок, возникающих при работе
    с JWT или другими токенами аутентификации.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки для классификации.
        extra (Optional[Dict[str, Any]]): Дополнительные данные с флагом "token": True.
    """

    def __init__(
        self,
        detail: str,
        error_type: str = "token_error",
        status_code: int = 401,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение TokenError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            error_type (str): Тип ошибки для классификации.
            extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
        """
        super().__init__(
            detail=detail,
            error_type=error_type,
            status_code=status_code,
            extra=extra or {"token": True},
        )


class TokenMissingError(TokenError):
    """
    Исключение для отсутствующего токена.

    Возникает, когда требуется токен для аутентификации, но он не предоставлен
    в запросе (например, отсутствует заголовок Authorization).

    Attributes:
        detail (str): "Токен отсутствует".
        error_type (str): "token_missing".
    """

    def __init__(self):
        """
        Инициализирует исключение TokenMissingError с предопределенными значениями.
        """
        super().__init__(detail="Токен отсутствует", error_type="token_missing")


class TokenExpiredError(TokenError):
    """
    Исключение для истекшего токена.

    Возникает, когда предоставленный токен аутентификации больше не действителен
    из-за истечения срока действия.

    Attributes:
        detail (str): "Токен просрочен".
        error_type (str): "token_expired".
    """

    def __init__(self):
        """
        Инициализирует исключение TokenExpiredError с предопределенными значениями.
        """
        super().__init__(
            detail="Токен просрочен", error_type="token_expired", status_code=419
        )


class TokenInvalidError(TokenError):
    """
    Исключение для недействительного токена.

    Возникает, когда предоставленный токен имеет неверный формат,
    поврежден или подпись не может быть проверена.
    """

    def __init__(
        self, detail: str = "Невалидный токен", extra: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует исключение TokenInvalidError.

        Args:
            detail: Сообщение об ошибке
            extra: Дополнительные данные об ошибке
        """
        super().__init__(
            detail=detail, error_type="token_invalid", status_code=422, extra=extra
        )
