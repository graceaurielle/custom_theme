import frappe

@frappe.whitelist(allow_guest=True)
def login_user(email, password):
    try:
        if not email or not password:
            return {"success": False, "error": "Email et mot de passe obligatoires"}

        # Tentative de connexion
        user = frappe.authenticate(email, password)
        
        if not user:
            return {"success": False, "error": "Email ou mot de passe incorrect"}

        # Récupérer l'utilisateur
        user_doc = frappe.get_doc("User", user)

        # Vérifier qu'il est Website User (optionnel mais recommandé)
        if user_doc.user_type != "Website User":
            return {"success": False, "error": "Cet utilisateur n'est pas autorisé sur le site web"}

        # Connexion réussie (Frappe gère déjà la session)
        frappe.login_manager.login_user(user, password)

        return {"success": True, "message": "Connexion réussie"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Erreur login custom")
        return {"success": False, "error": "Erreur lors de la connexion"}
    

