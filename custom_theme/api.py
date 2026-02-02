import frappe
from frappe import _
from frappe.utils import now_datetime, random_string

@frappe.whitelist(allow_guest=True)
def create_website_user(full_name, email, new_password, phone=None, company_name=None):
    """
    Création complète d'un utilisateur avec Customer associé
    """
    try:
        # Validation des champs
        if not all([full_name, email, new_password]):
            return {"success": False, "error": "Tous les champs obligatoires doivent être remplis"}
        
        # Vérifier si l'email existe déjà
        if frappe.db.exists("User", {"email": email}):
            return {"success": False, "error": "Un compte avec cet email existe déjà"}
        
        # Extraire prénom et nom
        name_parts = full_name.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # 1. CRÉER L'UTILISATEUR
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "new_password": new_password,
            "enabled": 1,
            "send_welcome_email": 0,  # Désactiver l'email par défaut de Frappe si je
        }).insert(ignore_permissions=True)
    

        # IMPORTANT : sauvegarder + reload
        user.save(ignore_permissions=True)
        frappe.db.commit()
        
        # 3. CRÉER LE CUSTOMER ASSOCIÉ
        customer_name = company_name or full_name
        
        # Générer un ID customer unique
        customer_id = email.replace('@', '_').replace('.', '_')
        
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",  # Ou "Company" si company_name fourni ici je les mis ainsi oh
            "customer_group": "Particulier",  # À adapter à ton groupe de clients
            "territory": "Ivory Coast",  # À adapter il doit pouvoir choisir
            "customer_primary_contact":phone,
            "customer_primary_address": None,  # À remplir plus tard
            "email_id": email,
            "mobile_no": phone,
            "user": user.name,
            "disabled": 0,
        }).insert(ignore_permissions=True)
        
       
        
        
        # 5. CRÉER UN CONTACT ASSOCIÉ
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": first_name,
            "last_name": last_name,
            "email_ids": [{
                "email_id": email,
                "is_primary": 1
            }],
            "phone_nos": [{
                "phone": phone,
                "is_primary_phone": 1
            }] if phone else [],
            "links": [
                {
                    "link_doctype": "Customer",
                    "link_name": customer.name
                },
                {
                    "link_doctype": "User",
                    "link_name": user.name
                }
            ]
        }).insert(ignore_permissions=True)
        
        # 6. Mettre à jour le Customer avec le contact
        customer.db_set("customer_primary_contact", contact.name)
        
        frappe.db.commit()

        return {
            "success": True, 
            "message": "Compte créé avec succès !",
            "user_id": user.name,
            "customer_id": customer.name,
            "contact_id": contact.name,
            "redirect": "/authentification/login"  # URL de redirection
        }
        
    except frappe.DuplicateEntryError:
        return {"success": False, "error": "Cet email est déjà utilisé"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Erreur création utilisateur")
        return {"success": False, "error": f"Erreur technique : {str(e)}"}



@frappe.whitelist()
def get_user_customer_details(user=None):
    """Récupérer les infos Customer d'un utilisateur"""
    if not user:
        user = frappe.session.user
    
    if user == "Guest":
        return {"success": False, "error": "Non connecté"}
    
    # Chercher le customer lié à l'utilisateur
    customer = frappe.db.get_value("Customer", 
        {"custom_user_linked": user}, 
        ["name", "customer_name", "email_id", "mobile_no"], 
        as_dict=True
    )
    
    if not customer:
        return {"success": False, "error": "Aucun client trouvé"}
    
    return {
        "success": True,
        "customer": customer
    }
    










    

@frappe.whitelist(allow_guest=True)
def custom_logout():
    # Déconnexion standard
    frappe.local.login_manager.logout()
    # Définir la redirection
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/accueil"