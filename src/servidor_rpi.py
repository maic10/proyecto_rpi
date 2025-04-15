from flask import Flask
from transmisor import detener_transmision

app = Flask(__name__)

@app.route('/stop_transmission', methods=['POST'])
def detener():
    print("[RPI] Solicitud de parada recibida del servidor")
    detener_transmision()
    return {"mensaje": "Transmisión detenida correctamente"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
