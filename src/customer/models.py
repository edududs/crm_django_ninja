from __future__ import annotations

from typing import Self

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from customer.manager import CustomerManager


class Customer(AbstractUser):
    class Gender(models.TextChoices):
        MALE = "M", _("Masculino")
        FEMALE = "F", _("Feminino")

    cpf_validator = RegexValidator(r"^\d{11}$", _("CPF deve conter 11 dígitos numéricos."))
    phone_validator = RegexValidator(
        r"^\d{10,11}$", _("Telefone deve conter 10 ou 11 dígitos numéricos (incluindo DDD).")
    )

    email = models.EmailField(_("E-mail"), unique=True)
    cpf = models.CharField(_("CPF"), max_length=11, validators=[cpf_validator], unique=True)
    phone = models.CharField(_("Telefone"), max_length=15, validators=[phone_validator])
    birth_date = models.DateField(_("Data de nascimento"), null=True, blank=True)
    gender = models.CharField(
        _("Gênero"),
        max_length=1,
        choices=Gender.choices,
        blank=True,
    )

    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    objects: CustomerManager[Self] = CustomerManager()
    loyalty: LoyaltyProgram | None
    addresses: models.QuerySet[Address]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.get_full_name()} - ({self.cpf})"


class Address(models.Model):
    customer = models.ForeignKey[Customer](
        Customer, on_delete=models.CASCADE, verbose_name=_("Cliente"), related_name="addresses"
    )
    name = models.CharField(_("Nome"), max_length=255, blank=True)
    latitude = models.FloatField(_("Latitude"), null=True, blank=True)
    longitude = models.FloatField(_("Longitude"), null=True, blank=True)
    zip_code = models.CharField(_("CEP"), max_length=255, blank=True)
    street = models.CharField(_("Rua"), max_length=255, blank=True)
    number = models.CharField(_("Número"), max_length=255, blank=True)
    complement = models.CharField(_("Complemento"), max_length=255, blank=True)
    neighborhood = models.CharField(_("Bairro"), max_length=255, blank=True)
    city = models.CharField(_("Cidade"), max_length=255, blank=True)
    state = models.CharField(_("Estado"), max_length=255, blank=True)
    country = models.CharField(_("País"), max_length=255, blank=True)
    details = models.TextField(_("Detalhes"), blank=True)

    main = models.BooleanField(_("Principal"), default=False)
    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Endereço")
        verbose_name_plural = _("Endereços")
        ordering = ["-customer__date_joined"]

    def __str__(self) -> str:
        return f"{self.customer!s} - ({self.city}, {self.number})"


class LoyaltyProgram(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="loyalty", verbose_name=_("Cliente")
    )
    points = models.PositiveIntegerField(_("Pontos"), default=0)
    tier = models.CharField(
        _("Nível"),
        max_length=20,
        choices=[("BRONZE", _("Bronze")), ("SILVER", _("Prata")), ("GOLD", _("Ouro"))],
        default=_("Bronze"),
    )

    class Meta:
        verbose_name = _("Programa de fidelidade")
        verbose_name_plural = _("Programas de fidelidade")
        ordering = ["-points"]

    def __str__(self) -> str:
        return f"{self.customer.get_full_name()} - ({self.points})"

    def add_points(self, amount: int) -> None:
        self.points += amount
        self.save()
