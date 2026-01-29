frappe.ready(() => {
    document.getElementById("btn-login").addEventListener("click", login);
});

function login() {
    const usr = document.getElementById("login-email").value;
    const pwd = document.getElementById("login-password").value;

    if (!usr || !pwd) {
        frappe.msgprint("Veuillez renseigner email et mot de passe");
        return;
    }

    frappe.call({
        method: "login",
        args: {
            usr: usr,
            pwd: pwd
        },
        freeze: true,
        callback: function (r) {
            if (!r.exc) {
                window.location.href = "/me";
            }
        },
        error: function () {
            frappe.msgprint("Identifiants incorrects");
        }
    });
}
