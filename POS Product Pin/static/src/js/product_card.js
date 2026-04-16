import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

ProductCard.props = {
    ...ProductCard.props,
    disablePin: { type: Boolean, optional: true },
    onTogglePin: { type: Function, optional: true },
};