import frappe

@frappe.whitelist()
def search_products(query, limit=8):
	if not query:
		return []

	query = f"%{query}%"

	items = frappe.db.sql("""
		SELECT
			i.item_code,
			i.item_name,
			i.image,
			wi.route
		FROM `tabItem` i
		INNER JOIN `tabWebsite Item` wi ON wi.item_code = i.item_code
		WHERE
			i.disabled = 0
			AND wi.published = 1
			AND (
				i.item_name LIKE %(query)s
				OR i.item_code LIKE %(query)s
			)
		ORDER BY wi.rank DESC, i.modified DESC
		LIMIT %(limit)s
	""", {
		"query": query,
		"limit": int(limit)
	}, as_dict=True)

	return items
