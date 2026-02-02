# pyright: reportIncompatibleVariableOverride=false, reportUninitializedInstanceVariable=false, reportImportCycles=false
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.models import Product


class Campaign(models.Model):
    name = models.CharField(_("Nome da Campanha"), max_length=255)
    description = models.TextField(_("Descrição"), blank=True)
    start_date = models.DateTimeField(_("Data de Início"))
    end_date = models.DateTimeField(_("Data de Término"))
    is_active = models.BooleanField(_("Ativa"), default=True)
    budget = models.DecimalField(_("Orçamento"), max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Campanha")
        verbose_name_plural = _("Campanhas")

    def __str__(self) -> str:
        return self.name


class Coupon(models.Model):
    code = models.CharField(_("Código do Cupom"), max_length=50, unique=True)
    offer = models.ForeignKey["Offer"]("Offer", on_delete=models.CASCADE, related_name="coupons")

    # Limites
    max_usages = models.PositiveIntegerField(_("Limite Global de Uso"), default=100)
    current_usages = models.PositiveIntegerField(_("Usos Atuais"), default=0)
    max_usages_per_customer = models.PositiveIntegerField(_("Limite por Cliente"), default=1)

    valid_from = models.DateTimeField(_("Válido de"))
    valid_until = models.DateTimeField(_("Válido até"))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Cupom")
        verbose_name_plural = _("Cupons")

    def __str__(self) -> str:
        return self.code

    def is_valid(self) -> bool:
        from django.utils import timezone

        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_until
            and self.current_usages < self.max_usages
        )


class Offer(models.Model):
    OFFER_TYPES = [
        ("PERCENTAGE", _("Percentual")),
        ("FIXED_AMOUNT", _("Valor Fixo")),
        ("BOGO", _("Leve X Pague Y")),  # Buy One Get One
    ]

    campaign = models.ForeignKey[Campaign | None](
        Campaign, on_delete=models.SET_NULL, related_name="offers", null=True
    )
    name = models.CharField(_("Nome da Oferta"), max_length=255)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default="PERCENTAGE")
    discount_value = models.DecimalField(_("Valor do Desconto"), max_digits=10, decimal_places=2)

    # Condições
    min_purchase_amount = models.DecimalField(
        _("Compra Mínima"), max_digits=10, decimal_places=2, default=0
    )
    products = models.ManyToManyField(
        Product, related_name="offers", verbose_name=_("Produtos Elegíveis")
    )

    # Público-alvo (opcional)
    is_exclusive_for_loyalty = models.BooleanField(_("Exclusivo Fidelidade"), default=False)

    class Meta:
        verbose_name = _("Oferta")
        verbose_name_plural = _("Ofertas")

    def __str__(self) -> str:
        return self.name


class Contact(models.Model):
    class Type(models.TextChoices):
        PHONE = "PHONE", _("Telefone")
        EMAIL = "EMAIL", _("E-mail")
        WHATSAPP = "WHATSAPP", _("WhatsApp")
        OTHER = "OTHER", _("Outro")

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    value = models.CharField(_("Valor"), max_length=255)
    is_active = models.BooleanField(_("Ativo"), default=True)

    class Meta:
        verbose_name = _("Contato")
        verbose_name_plural = _("Contatos")

    def __str__(self) -> str:
        return f"{self.type} - {self.value}"


class SocialMedia(models.Model):
    class Type(models.TextChoices):
        FACEBOOK = "FACEBOOK", _("Facebook")
        INSTAGRAM = "INSTAGRAM", _("Instagram")
        TWITTER = "TWITTER", _("Twitter")
        OTHER = "OTHER", _("Outro")

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    value = models.CharField(_("Valor"), max_length=255)
    is_active = models.BooleanField(_("Ativo"), default=True)

    class Meta:
        verbose_name = _("Rede Social")
        verbose_name_plural = _("Redes Sociais")

    def __str__(self) -> str:
        return f"{self.type} - {self.value}"
