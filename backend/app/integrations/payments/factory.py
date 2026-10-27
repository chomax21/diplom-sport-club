from app.core.config import settings
from app.integrations.payments.base import PaymentProvider
from app.integrations.payments.mock import MockPaymentProvider

_PROVIDERS: dict[str, type[PaymentProvider]] = {
    "mock": MockPaymentProvider,
}


def get_payment_provider() -> PaymentProvider:
    """FastAPI-зависимость: выбирает провайдера по настройке PAYMENT_PROVIDER."""
    provider_cls = _PROVIDERS.get(settings.payment_provider.lower())
    if provider_cls is None:
        raise RuntimeError(f"Неизвестный платёжный провайдер: {settings.payment_provider}")
    return provider_cls()
