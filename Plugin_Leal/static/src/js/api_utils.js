/** @odoo-module **/

export async function lealLogin(usuario, contrasena) {
    const apiCall = await fetch("https://testapi.puntosleal.com/api/com_usuarios/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            usuario,
            contrasena,
        }),
    });
    const data = await apiCall.json();
    if (data.code == 100) {
        localStorage.setItem("_leal_token", data.data.token);
        localStorage.setItem("_leal_refresh_token", data.data.refresh_token);
        return {
            code: data.code,
            message: "OK"
        };

    }
}

export async function SendOTPToCostumer() {

}