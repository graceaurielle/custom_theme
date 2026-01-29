import frappe
from frappe.utils import cint, fmt_money
from webshop.webshop.product_data_engine.filters import ProductFiltersBuilder


def get_context(context):
    context.no_cache = 1

    # -------------------------
    # FORÇAGE DU GROUPE
    # -------------------------
    item_group = "carrelage"
    context.item_group = item_group

    # -------------------------
    # Paramètres URL autorisés
    # -------------------------
    search = frappe.form_dict.get("search")
    page = cint(frappe.form_dict.get("page", 1))

    # -------------------------
    # Filtres Webshop
    # -------------------------
    filter_engine = ProductFiltersBuilder(item_group=item_group)
    context.field_filters = filter_engine.get_field_filters()
    context.attribute_filters = filter_engine.get_attribute_filters()

    context.page_length = (
        cint(frappe.db.get_single_value("Webshop Settings", "products_per_page")) or 20
    )

    # -------------------------
    # Query Website Item
    # -------------------------
    filters = {
        "published": 1,
        "item_group": item_group,
    }

    website_items = frappe.get_all(
        "Website Item",
        filters=filters,
        fields=[
            "name",
            "item_code",
            "item_name",
            "route",
            "thumbnail",
            "website_image",
            "short_description",
            "description",
            "web_long_description",
            "item_group",
            "brand",
            "ranking",
        ],
        order_by="ranking desc",
        start=(page - 1) * context.page_length,
        page_length=context.page_length,
    )

    products = []

    currency = frappe.defaults.get_global_default("currency") or "XOF"

    for wi in website_items:
        # -------------------------
        # Recherche texte
        # -------------------------
        if search:
            text = (
                (wi.item_name or "")
                + (wi.short_description or "")
                + (wi.description or "")
            ).lower()
            if search.lower() not in text:
                continue

        # -------------------------
        # Prix
        # -------------------------
        price = frappe.db.get_value(
            "Item Price",
            {"item_code": wi.item_code, "selling": 1},
            "price_list_rate",
        )

        standard_rate = frappe.db.get_value(
            "Item", wi.item_code, "standard_rate"
        )

        final_price = price or standard_rate

        # Formatage officiel Frappe
        formatted_price = fmt_money(
            final_price,
            currency=currency,
            precision=0
        ) if final_price else None

        formatted_standard_rate = (
            fmt_money(standard_rate, currency=currency, precision=0)
            if standard_rate else None
        )

        # -------------------------
        # Wishlist
        # -------------------------
        in_wishlist = False
        if frappe.session.user != "Guest":
            in_wishlist = frappe.db.exists(
                "Wishlist Item",
                {
                    "item_code": wi.item_code,
                    "parent": frappe.session.user,
                }
            )

        # -------------------------
        # Produit final
        # -------------------------
        products.append({
            "item_code": wi.item_code,
            "name": wi.item_name,
            "route": wi.route,
            "image": wi.thumbnail or wi.website_image,
            "short_description": wi.short_description,
            "description": wi.description,

            # Valeurs affichables
            "price": formatted_price,
            "standard_rate": formatted_standard_rate,

            # Valeurs brutes (utile si besoin plus tard)
            "price_raw": final_price,
            "standard_rate_raw": standard_rate,

            "currency": currency,
            "brand": wi.brand,
            "in_wishlist": in_wishlist,
            "badge": "PROMO" if price and standard_rate and price < standard_rate else None,
        })

    context.products = products
    context.search = search
    context.page = page
