from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager

if TYPE_CHECKING:
    from customer.models import Customer


class CustomerManager[T: Customer](BaseUserManager[T]):
    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> T:
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> T:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
