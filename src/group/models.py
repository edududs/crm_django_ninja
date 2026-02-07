# pyright: reportIncompatibleVariableOverride=false, reportUninitializedInstanceVariable=false
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from customer.models import Address, Customer
from marketing.models import Contact


# Create your models here.
class Group(models.Model):
    id = models.AutoField(_("ID"), primary_key=True)
    status = models.BooleanField(_("Status"), default=True)
    email = models.EmailField(_("E-mail"), unique=True)
    name = models.CharField(_("Nome"), max_length=255)
    short_name = models.CharField(_("Nome curto"), max_length=255)
    full_name = models.CharField(_("Nome completo"), max_length=255)
    cnpj = models.CharField(_("CNPJ"), max_length=255)
    phone = models.CharField(_("Telefone"), max_length=255)
    owner = models.ForeignKey[Customer](
        Customer,
        on_delete=models.CASCADE,
        related_name="owned_groups",
        verbose_name=_("Cliente"),
    )
    addresses = models.ManyToManyField(Address, related_name="groups", blank=True)

    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Grupo")
        verbose_name_plural = _("Grupos")
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.name} - {self.owner!s}"


class Store(models.Model):
    id = models.AutoField(_("ID"), primary_key=True)
    group = models.ForeignKey[Group](
        Group,
        on_delete=models.CASCADE,
        related_name="stores",
        verbose_name=_("Grupo"),
    )
    status = models.BooleanField(_("Status"), default=True)
    name = models.CharField(_("Nome"), max_length=255)
    cnpj = models.CharField(_("CNPJ"), max_length=255)
    phone = models.CharField(_("Telefone"), max_length=255)
    address = models.ForeignKey[Address](
        Address,
        on_delete=models.CASCADE,
        related_name="stores",
        verbose_name=_("Endereço"),
    )
    contacts = models.ManyToManyField(Contact, related_name="stores", blank=True)

    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Loja")
        verbose_name_plural = _("Lojas")
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.name} - {self.group!s}"
