async function enviarPregunta(pregunta) {
  const API_URL = "https://eca2-34-90-169-47.ngrok-free.app/preguntar"; // Actualiza si ngrok cambia
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: pregunta })
    });

    if (!response.ok) throw new Error("Fallo en la API");
    const data = await response.json();
    mostrarRespuesta(data.respuesta);
  } catch (error) {
    mostrarRespuesta("Hubo un problema al contactar al asistente. Inténtalo más tarde.");
  }
}

function handleInput(event) {
  if (event.key === "Enter" || event.type === "click") {
    const input = document.getElementById('user-input');
    const texto = input.value.trim();
    if (texto) {
      mostrarPregunta(texto);
      enviarPregunta(texto);
      input.value = "";
    }
  }
}

function mostrarPregunta(texto) {
  const entrada = document.createElement("div");
  entrada.className = "message user";
  entrada.innerText = texto;
  document.querySelector(".chat-panel").appendChild(entrada);
}

function mostrarRespuesta(texto) {
  const salida = document.createElement("div");
  salida.className = "message bot";
  salida.innerText = texto;
  document.querySelector(".chat-panel").appendChild(salida);
}