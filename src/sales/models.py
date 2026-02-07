# pyright: reportIncompatibleVariableOverride=false, reportUninitializedInstanceVariable=false, reportImportCycles=false
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.models import Product
from customer.models import Customer

if TYPE_CHECKING:
    from decimal import Decimal


# Create your models here.
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pendente")
        PAID = "PAID", _("Pago")
        CANCELLED = "CANCELLED", _("Cancelado")

    customer = models.ForeignKey[Customer | None](
        Customer,
        on_delete=models.SET_NULL,
        verbose_name=_("Cliente"),
        null=True,
        related_name="orders",
    )
    external_id = models.CharField(_("ID externo"), max_length=255, unique=True)
    total_amount = models.DecimalField(_("Valor total"), max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(
        _("Desconto aplicado"), max_digits=10, decimal_places=2, default=0
    )

    sale_date = models.DateTimeField(_("Data da venda"), help_text="Data e hora da venda")
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        ordering = ["-sale_date"]

    def __str__(self) -> str:
        return f"{self.external_id} - {self.customer!s} - {self.total_amount}"


class OrderItem(models.Model):
    order = models.ForeignKey[Order](
        Order, on_delete=models.CASCADE, verbose_name=_("Pedido"), related_name="items"
    )
    product = models.ForeignKey[Product](
        Product,
        on_delete=models.SET_NULL,
        verbose_name=_("Produto"),
        related_name="items",
    )
    quantity = models.PositiveIntegerField(_("Quantidade"), default=1)
    price = models.DecimalField(_("Preço"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Item do pedido")
        verbose_name_plural = _("Itens do pedido")
        ordering = ["-order__sale_date"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.quantity} - {self.price}"

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.price
