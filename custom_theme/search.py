import frappe
from frappe.utils import cint

# API interne Webshop (utilisée officiellement par all-products)
from webshop.webshop.product_data_engine.filters import ProductFiltersBuilder


def get_context(context):
    context.no_cache = 1

    # -------------------------
    # Paramètres URL
    # -------------------------
    search = frappe.form_dict.get("search")
    item_group = frappe.form_dict.get("item_group")
    page = cint(frappe.form_dict.get("page", 1))

    # -------------------------
    # Filtres Webshop (comme all-products)
    # -------------------------
    filter_engine = ProductFiltersBuilder(item_group=item_group)
    context.field_filters = filter_engine.get_field_filters()
    context.attribute_filters = filter_engine.get_attribute_filters()

    context.page_length = (
        cint(frappe.db.get_single_value("Webshop Settings", "products_per_page")) or 20
    )

    # -------------------------
    # Query Website Item
    # (PAS get_doc, PAS d'attribut direct)
    # -------------------------
    filters = {"published": 1}

    if item_group:
        filters["item_group"] = item_group

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
        # Prix (Item Price > standard_rate)
        # -------------------------
        price = frappe.db.get_value(
            "Item Price",
            {
                "item_code": wi.item_code,
                "selling": 1,
            },
            "price_list_rate",
        )

        standard_rate = frappe.db.get_value(
            "Item", wi.item_code, "standard_rate"
        )

        final_price = price or standard_rate

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

            # Images
            "image": wi.thumbnail or wi.website_image,

            # Descriptions
            "short_description": wi.short_description,
            "description": wi.description,
            "web_long_description": wi.web_long_description,

            # Business
            "price": final_price,
            "currency": frappe.defaults.get_global_default("currency"),
            "brand": wi.brand,
            "item_group": wi.item_group,

            # UX
            "in_wishlist": in_wishlist,

            # Badge simple (exemple)
            "badge": "Sale" if price and standard_rate and price < standard_rate else None,
        })

    # -------------------------
    # Context HTML
    # -------------------------
    context.products = products
    context.search = search
    context.item_group = item_group
    context.page = page



@frappe.whitelist(allow_guest=True)
def autocomplete_products():
    query = frappe.form_dict.get("query")

    if not query:
        return []

    query = query.lower()

    website_items = frappe.get_all(
        "Website Item",
        filters={"published": 1},
        fields=[
            "item_name",
            "route",
            "thumbnail",
            "website_image",
            "item_code",
        ],
        limit_page_length=20,
    )

    results = []

    for wi in website_items:
        item = None

        if wi.item_code:
            item = frappe.db.get_value(
                "Item",
                wi.item_code,
                [
                    "item_name",
                    "item_group",
                    "description",
                ],
                as_dict=True,
            )

        searchable_text = " ".join(filter(None, [
            wi.item_name,
            item.item_name if item else "",
            item.item_group if item else "",
            item.description if item else "",
        ])).lower()

        if query not in searchable_text:
            continue

        results.append({
            "name": wi.item_name,
            "route": wi.route,
            "image": wi.thumbnail or wi.website_image,
        })

        if len(results) >= 8:
            break

    return results
