from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.billing_usage_line_item_attributes import (
        BillingUsageLineItemAttributes,
    )
    from ..models.billing_usage_line_item_pricing_dimensions import (
        BillingUsageLineItemPricingDimensions,
    )


T = TypeVar("T", bound="BillingUsageLineItem")


@_attrs_define
class BillingUsageLineItem:
    """
    Attributes:
        product_name (str): Human-readable label for the billed product. Display-only and not stable; do not key logic
            off this value.
        quantity (str): Total usage for the window in the product's native unit, as a decimal string.
        unit_price (str): Per-unit price in USD, as a decimal string.
        cost (str): Total cost for the line item in USD, as a decimal string.
        pricing_dimensions (BillingUsageLineItemPricingDimensions): Rate-determining dimensions as string key-value
            pairs. Varies by product.
        attributes (BillingUsageLineItemAttributes): Resource identifiers for attribution as string key-value pairs.
            `api_key_id` and `project_id` are present for all line items.
    """

    product_name: str
    quantity: str
    unit_price: str
    cost: str
    pricing_dimensions: BillingUsageLineItemPricingDimensions
    attributes: BillingUsageLineItemAttributes
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        product_name = self.product_name

        quantity = self.quantity

        unit_price = self.unit_price

        cost = self.cost

        pricing_dimensions = self.pricing_dimensions.to_dict()

        attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "product_name": product_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "cost": cost,
                "pricing_dimensions": pricing_dimensions,
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.billing_usage_line_item_attributes import (
            BillingUsageLineItemAttributes,
        )
        from ..models.billing_usage_line_item_pricing_dimensions import (
            BillingUsageLineItemPricingDimensions,
        )

        d = dict(src_dict)
        product_name = d.pop("product_name")

        quantity = d.pop("quantity")

        unit_price = d.pop("unit_price")

        cost = d.pop("cost")

        pricing_dimensions = BillingUsageLineItemPricingDimensions.from_dict(
            d.pop("pricing_dimensions")
        )

        attributes = BillingUsageLineItemAttributes.from_dict(d.pop("attributes"))

        billing_usage_line_item = cls(
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            cost=cost,
            pricing_dimensions=pricing_dimensions,
            attributes=attributes,
        )

        billing_usage_line_item.additional_properties = d
        return billing_usage_line_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
