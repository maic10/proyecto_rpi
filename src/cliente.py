# src/cliente.py
import time
import requests
from led_control import actualizar_estado_leds  # Cambiar a led_control
from config import ID_RPI, SERVIDOR_URL
from transmisor import iniciar_transmision, detener_transmision, transmision_activa

def obtener_token():
    try:
        print("[CLIENTE] Solicitando token JWT al servidor...")
        res = requests.post(f"{SERVIDOR_URL}/api/auth/raspberry", json={
            "id_raspberry_pi": ID_RPI
        })
        if res.status_code == 200:
            data = res.json()
            token = data["token"]
            print("[CLIENTE] Token JWT obtenido con éxito")
            actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)
            return token
        else:
            print(f"[CLIENTE] Error al obtener token: {res.status_code} - {res.text}")
            actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
            return None
    except Exception as e:
        print(f"[CLIENTE] Error al conectar con el servidor para obtener token: {e}")
        actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
        return None

# Configurar headers con el token
token = obtener_token()
if not token:
    print("[CLIENTE] No se pudo obtener el token. Finalizando...")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}
PUERTO_RPI = 8080

def solicitar_transmision():
    try:
        print("[CLIENTE] Solicitando inicio de transmisión al servidor...")
        res = requests.post(f"{SERVIDOR_URL}/api/transmision/iniciar", json={
            "id_raspberry_pi": ID_RPI,
            "port": PUERTO_RPI
        }, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data.get("permitido"):
                print(f"[CLIENTE] Transmisión permitida para clase: {data['id_clase']}")
                actualizar_estado_leds(conexion_exitosa=True, transmision_activa=True)
                return data["id_clase"]
            else:
                print(f"[CLIENTE] Transmisión denegada: {data.get('motivo', 'Sin motivo')}")
                actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)
        else:
            print(f"[CLIENTE] Error en respuesta del servidor: {res.status_code} - {res.text}")
            actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
    except Exception as e:
        print(f"[CLIENTE] Error de conexión con el servidor: {e}")
        actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
    return None

def verificar_estado_transmision():
    try:
        res = requests.post(f"{SERVIDOR_URL}/api/transmision/estado", json={
            "id_raspberry_pi": ID_RPI
        }, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if not data.get("transmitir") and transmision_activa():
                print(f"[CLIENTE] Deteniendo transmisión: {data.get('motivo')}")
                detener_transmision()
            actualizar_estado_leds(conexion_exitosa=True, transmision_activa=data.get("transmitir", False))
            return data.get("transmitir", False)
        else:
            print(f"[CLIENTE] Error al verificar estado: {res.status_code} - {res.text}")
            actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
    except Exception as e:
        print(f"[CLIENTE] Error de conexión al verificar estado: {e}")
        actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
    return False

def loop_transmision():
    while True:
        if not transmision_activa():
            id_clase = solicitar_transmision()
            if id_clase:
                iniciar_transmision()
                print("[CLIENTE] Transmisión iniciada.")
            else:
                print("[CLIENTE] Reintento en 30 segundos...")
            time.sleep(30)
        else:
            if not verificar_estado_transmision():
                print("[CLIENTE] Transmisión detenida por el servidor.")
            else:
                print("[CLIENTE] Transmisión en curso. Verificando estado en 15 segundos...")
            time.sleep(15)

if __name__ == "__main__":
    inicializar_leds()  # Inicializar LEDs desde led_control
    loop_transmision()