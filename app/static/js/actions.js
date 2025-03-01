document.addEventListener("DOMContentLoaded", function () {

    // ✅ Manejo de Likes y Dislikes
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function () {
            let listId = this.dataset.listId;
            let action = this.dataset.action;

            fetch(`/lists/${listId}/like_ajax/${action}`, {
                method: "POST",
                headers: { 
                    "X-CSRFToken": getCSRFToken(),
                    "Accept": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error === "auth_required") {
                    showFlashMessage("⚠️ Debes iniciar sesión para dar like o dislike.", "warning");
                    return;
                }

                if (data.success) {
                    document.querySelector(`[data-list-id='${listId}'] .like-count`).innerText = data.likes;
                    document.querySelector(`[data-list-id='${listId}'] .dislike-count`).innerText = data.dislikes;
                }

                data.messages.forEach(msg => showFlashMessage(msg[1], msg[0]));
            })
            .catch(error => console.error("Error en AJAX (like/dislike):", error));
        });
    });

    // ✅ Manejo de Seguir / Dejar de Seguir
    document.querySelectorAll(".follow-btn").forEach(button => {
        button.addEventListener("click", function () {
            let listId = this.dataset.listId;
            let buttonElement = this; // Guardamos referencia al botón completo

            fetch(`/following/toggle_ajax/${listId}`, {
                method: "POST",
                headers: { 
                    "X-CSRFToken": getCSRFToken(),
                    "Accept": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error === "auth_required") {
                    showFlashMessage("⚠️ Debes iniciar sesión para seguir listas.", "warning");
                    return;
                }

                if (data.success) {
                    let icon = buttonElement.querySelector("i"); // Asegurar que el icono existe antes de modificarlo
                    if (icon) {
                        icon.className = data.following ? "bi bi-heart-fill text-danger" : "bi bi-heart text-primary";
                    }
                }

                data.messages.forEach(msg => showFlashMessage(msg[1], msg[0]));
            })
            .catch(error => console.error("Error en AJAX (follow/unfollow):", error));
        });
    });

});

// ✅ Obtener CSRF Token
function getCSRFToken() {
    return document.querySelector("meta[name='csrf-token']").getAttribute("content");
}

// ✅ Mostrar mensajes flash correctamente
function showFlashMessage(message, category = "info") {
    let flashContainer = document.getElementById("flash-messages");

    if (!flashContainer) {
        flashContainer = document.createElement("div");
        flashContainer.id = "flash-messages";
        flashContainer.style.position = "fixed";
        flashContainer.style.top = "10px";
        flashContainer.style.right = "10px";
        flashContainer.style.zIndex = "9999";
        document.body.appendChild(flashContainer);
    }

    let alertClass = {
        "success": "alert-success",
        "info": "alert-info",
        "warning": "alert-warning",
        "danger": "alert-danger"
    }[category] || "alert-secondary";

    let flashMessage = document.createElement("div");
    flashMessage.className = `alert ${alertClass} alert-dismissible fade show`;
    flashMessage.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    flashContainer.appendChild(flashMessage);

    setTimeout(() => flashMessage.remove(), 3000);
}
