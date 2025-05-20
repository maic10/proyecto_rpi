import threading
from flask import Flask, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from cliente import loop_transmision
from transmisor import detener_transmision
from led_control import actualizar_estado_leds
from config import JWT_SECRET_KEY

# Inicializa la aplicación Flask y configura JWT
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY # Clave secreta para firmar tokens
app.config["JWT_IDENTITY_CLAIM"] = "id"  
jwt = JWTManager(app)

@app.route("/stop_transmission", methods=["POST"])
@jwt_required()
def stop():
    """
    Punto de entrada para detener la transmisión.
    - Valida el JWT.
    - Extrae la identidad del token.
    - Llama a detener_transmision() y actualiza los LEDs.
    """    
    identity = get_jwt_identity()
    print(f"[RPI] Solicitud de parada recibida desde el servidor (identidad: {identity})")

    detener_transmision()
    actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)
    return {"mensaje": "Transmisión detenida correctamente"}, 200

def iniciar_flask():
    """Arranca el servidor Flask escuchando en todas las interfaces en el puerto 8080."""
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # Ejecuta Flask en un hilo separado para no bloquear el bucle principal
    flask_thread = threading.Thread(target=iniciar_flask, daemon=True)
    flask_thread.start()

    # Inicia el bucle que gestiona solicitud y control de transmisión
    loop_transmision()