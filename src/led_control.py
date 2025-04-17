# src/led_control.py
from gpiozero import LED

# Configuración de los LEDs en los pines GPIO
led_blanco = LED(17)  # Transmisión activa
led_azul = LED(27)  # Sin transmisión
led_rojo = LED(22)  # Problemas con el servidor

def actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False):
    """Actualiza el estado de los LEDs según la transmisión y la conexión con el servidor."""
    if not conexion_exitosa:
        # Problemas con el servidor
        led_blanco.off()
        led_azul.off()
        led_rojo.on()
    elif transmision_activa:
        # Transmisión activa
        led_blanco.on()
        led_azul.off()
        led_rojo.off()
    else:
        # Sin transmisión
        led_blanco.off()
        led_azul.on()
        led_rojo.off()

def inicializar_leds():
    """Inicializa los LEDs al estado por defecto (sin transmisión)."""
    actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)