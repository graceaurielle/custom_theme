import frappe

def get_context(context):
	# do your magic here
	pass


def after_insert(doc, method=None):
    # Crée un nouvel utilisateur Website User
    user = frappe.get_doc({
        "doctype": "User",
        "email": doc.email,
        "first_name": doc.full_name.split()[0] if ' ' in doc.full_name else doc.full_name,
        "last_name": doc.full_name.split()[1] if ' ' in doc.full_name else '',
        "new_password": doc.new_password,
        "roles": [{"role": "Website User"}]  # Assigne rôle Website User
    })
    user.insert(ignore_permissions=True)
    frappe.db.commit()
