from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("Nome"), max_length=255)
    description = models.TextField(_("Descrição"))
    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(_("Nome"), max_length=255)
    description = models.TextField(_("Descrição"))
    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Marca")
        verbose_name_plural = _("Marcas")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


# Create your models here.
class Product(models.Model):
    class Unit(models.TextChoices):
        UN = "UN", _("Unidade")
        KG = "KG", _("Kilograma")
        L = "L", _("Litro")
        PC = "PC", _("Peça")
        M = "M", _("Metro")
        CX = "CX", _("Caixa")

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Ativo")
        INACTIVE = "INACTIVE", _("Inativo")

    name = models.CharField(_("Nome"), max_length=255)
    description = models.TextField(_("Descrição"))
    price = models.DecimalField(_("Preço"), max_digits=10, decimal_places=2)
    sku = models.CharField(_("SKU"), max_length=255, unique=True)
    barcode = models.CharField(_("Código de barras"), max_length=255, unique=True)
    brand = models.ForeignKey["Brand"](
        "Brand",
        on_delete=models.SET_NULL,
        verbose_name=_("Marca"),
        null=True,
        related_name="products",
    )
    stock = models.PositiveIntegerField(_("Estoque"), default=0)
    category = models.ForeignKey[Category](
        Category,
        on_delete=models.SET_NULL,
        verbose_name=_("Categoria"),
        null=True,
        related_name="products",
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[("ACTIVE", _("Ativo")), ("INACTIVE", _("Inativo"))],
        default=_("Ativo"),
    )

    unit = models.CharField(
        _("Unidade"),
        max_length=255,
        choices=Unit.choices,
        default=Unit.UN,
    )

    created_at = models.DateTimeField(_("Data de criação"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Data de atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Produto")
        verbose_name_plural = _("Produtos")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.category!s}"
