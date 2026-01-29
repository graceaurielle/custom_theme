import frappe

@frappe.whitelist(allow_guest=True)
def create_website_user(full_name, email, new_password):
    try:
        if not all([full_name, email, new_password]):
            return {"success": False, "error": "Tous les champs sont obligatoires"}

        if frappe.db.exists("User", {"email": email}):
            return {"success": False, "error": "Cet email est déjà utilisé"}

        first_name = full_name.split()[0] if ' ' in full_name else full_name
        last_name = " ".join(full_name.split()[1:]) if ' ' in full_name else ""

        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "new_password": new_password,
            "enabled": 1,
            "send_welcome_email": 1
        }).insert(ignore_permissions=True)

        frappe.db.commit()

        return {"success": True, "message": "Compte créé avec succès"}

    except frappe.DuplicateEntryError:
        return {"success": False, "error": "Cet email existe déjà"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Erreur register custom")
        return {"success": False, "error": str(e)}