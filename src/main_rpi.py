import threading
from flask import Flask
from cliente import loop_transmision
from transmisor import detener_transmision

# ========== FLASK PARA DETENER ==========
app = Flask(__name__)

@app.route("/stop_transmission", methods=["POST"])
def stop():
    print("[RPI] Solicitud de parada recibida desde el servidor")
    detener_transmision()
    return {"mensaje": "Transmisión detenida correctamente"}, 200


def iniciar_flask():
    app.run(host="0.0.0.0", port=8080)

# ========== INICIO UNIFICADO ==========
if __name__ == "__main__":
    # Lanzar Flask en segundo plano
    flask_thread = threading.Thread(target=iniciar_flask, daemon=True)
    flask_thread.start()

    # Iniciar lógica principal de transmisión
    loop_transmision()
