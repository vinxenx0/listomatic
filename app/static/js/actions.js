document.addEventListener("DOMContentLoaded", function () {

    // ✅ Manejo de Likes y Dislikes con mensajes flash
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function () {
            let listId = this.dataset.listId;
            let action = this.dataset.action;

            fetch(`/lists/${listId}/like/${action}`, {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.querySelector(`[data-list-id='${listId}'] .like-count`).innerText = data.likes;
                    document.querySelector(`[data-list-id='${listId}'] .dislike-count`).innerText = data.dislikes;
                }
                showFlashMessages(data.messages);
            });
        });
    });

    // ✅ Manejo de Seguir / Dejar de Seguir con mensajes flash
    document.querySelectorAll(".follow-btn").forEach(button => {
        button.addEventListener("click", function () {
            let listId = this.dataset.listId;
            let icon = this.querySelector("i");

            fetch(`/following/toggle_ajax/${listId}`, {  // 🔥 Ahora usamos la nueva ruta
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // ✅ Actualizar el icono dinámicamente
                    icon.className = data.following ? "bi bi-heart-fill text-danger" : "bi bi-heart text-primary";
                }
                showFlashMessages(data.messages);
            });
        });
    });

});

// ✅ Función para mostrar mensajes flash dinámicamente
function showFlashMessages(messages) {
    let container = document.getElementById("flash-messages");

    // 🔥 Si el contenedor no existe, lo creamos y lo añadimos al body
    if (!container) {
        container = document.createElement("div");
        container.id = "flash-messages";
        container.className = "flash-messages";
        document.body.appendChild(container);
    }

    // 🔥 Limpiar mensajes anteriores
    container.innerHTML = "";

    messages.forEach(([category, message]) => {
        let alert = document.createElement("div");
        alert.className = `alert alert-${category} alert-dismissible fade show shadow-lg flash-message`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.appendChild(alert);

        // 🔥 Desvanecer después de 3 segundos
        setTimeout(() => {
            alert.classList.add("fade-out");
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });
}

// ✅ Obtener CSRF Token de Flask-WTF
function getCSRFToken() {
    return document.querySelector("meta[name='csrf-token']").getAttribute("content");
}
