class AppError(Exception):
    """Базовое доменное исключение, не зависящее от HTTP-слоя."""

    status_code: int = 400
    default_detail: str = "Ошибка запроса"

    def __init__(self, detail: str | None = None, headers: dict[str, str] | None = None):
        self.detail = detail or self.default_detail
        self.headers = headers
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    default_detail = "Объект не найден"


class ConflictError(AppError):
    status_code = 409
    default_detail = "Конфликт данных"


class ForbiddenError(AppError):
    status_code = 403
    default_detail = "Недостаточно прав"


class UnauthorizedError(AppError):
    status_code = 401
    default_detail = "Требуется авторизация"

    def __init__(self, detail: str | None = None):
        super().__init__(detail, headers={"WWW-Authenticate": "Bearer"})


class PaymentError(AppError):
    status_code = 502
    default_detail = "Ошибка платёжного провайдера"
