# main_rpi.py
import threading
from flask import Flask, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from cliente import loop_transmision
from transmisor import detener_transmision
from led_control import actualizar_estado_leds  # Importar desde led_control
from config import JWT_SECRET_KEY

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY  
jwt = JWTManager(app)

@app.route("/stop_transmission", methods=["POST"])
@jwt_required()
def stop():
    identity = get_jwt_identity()
    print(f"[RPI] Solicitud de parada recibida desde el servidor (identidad: {identity})")
    detener_transmision()
    actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)  # Actualizar LEDs tras detener
    return {"mensaje": "Transmisión detenida correctamente"}, 200

def iniciar_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=iniciar_flask, daemon=True)
    flask_thread.start()
    loop_transmision()