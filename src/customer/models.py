# pyright: reportIncompatibleVariableOverride=false, reportUninitializedInstanceVariable=false, reportImportCycles=false
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Self

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from customer.manager import CustomerManager

if TYPE_CHECKING:
    from group.models import Group


class CustomerDocument(models.Model):
    class DocumentType(models.TextChoices):
        CPF = "CPF", _("CPF")
        CNPJ = "CNPJ", _("CNPJ")
        RG = "RG", _("RG")
        CNH = "CNH", _("CNH")
        PASSPORT = "PASSPORT", _("Passaporte")
        OTHER = "OTHER", _("Outro")

    id = models.AutoField(_("ID"), primary_key=True)
    document_type = models.CharField(
        _("Tipo de documento"),
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.CPF,
    )
    document_number = models.CharField(_("Número do documento"), max_length=255)

    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Documento do cliente")
        verbose_name_plural = _("Documentos do cliente")
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.document_type} - {self.document_number}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Remover caracteres não numéricos
        clean_number = re.sub(r"\D", "", self.document_number)

        if self.document_type == self.DocumentType.CPF:
            # CPF: 11 dígitos
            if not re.fullmatch(r"\d{11}", clean_number):
                raise ValidationError(_("CPF deve conter exatamente 11 dígitos numéricos."))
            self.document_number = clean_number

        elif self.document_type == self.DocumentType.CNPJ:
            # CNPJ: 14 dígitos
            if not re.fullmatch(r"\d{14}", clean_number):
                raise ValidationError(_("CNPJ deve conter exatamente 14 dígitos numéricos."))
            self.document_number = clean_number

        super().save(*args, **kwargs)


class Address(models.Model):
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

    customers: models.QuerySet[Customer]
    groups: models.QuerySet[Group]

    class Meta:
        verbose_name = _("Endereço")
        verbose_name_plural = _("Endereços")
        ordering = ["-customer__date_joined"]

    def __str__(self) -> str:
        return f"{self.name} - ({self.city}, {self.number})"


class Customer(AbstractUser):
    class Gender(models.TextChoices):
        MALE = "M", _("Masculino")
        FEMALE = "F", _("Feminino")

    cpf_validator = RegexValidator(r"^\d{11}$", _("CPF deve conter 11 dígitos numéricos."))
    phone_validator = RegexValidator(
        r"^\d{10,11}$", _("Telefone deve conter 10 ou 11 dígitos numéricos (incluindo DDD).")
    )

    email = models.EmailField(_("E-mail"), unique=True)
    document = models.OneToOneField[CustomerDocument](
        CustomerDocument,
        on_delete=models.CASCADE,
        related_name="customer",
        verbose_name=_("Documento"),
    )
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
    adresses = models.ManyToManyField(Address, related_name="customers")

    objects: CustomerManager[Self] = CustomerManager()
    loyalty: LoyaltyProgram | None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.get_full_name()} - ({self.document!s})"


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
