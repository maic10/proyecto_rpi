import gi
import threading
import time
from led_control import actualizar_estado_leds 
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
from config import *

# Inicializar GStreamer solo una vez
Gst.init(None)

pipeline = None
loop = None

def iniciar_transmision():
    """
    Crea y arranca el pipeline de GStreamer para capturar video de la cámara,
    codificarlo en H.264 y enviarlo por UDP al servidor.
    También inicia un loop de GLib en un hilo separado para procesar mensajes.
    """    
    global pipeline, loop

    if pipeline is not None:
        print("[RPI] Transmisión ya en curso.")
        return

    print("[RPI] Iniciando transmisión de video...")

    # Construye el pipeline usando parámetros de configuración
    pipeline = Gst.parse_launch(
        f"libcamerasrc ! "
        f"video/x-raw,width={VIDEO_WIDTH},height={VIDEO_HEIGHT},format=NV12,framerate={VIDEO_FRAMERATE} ! "
        f"videoconvert ! "
        f"x264enc tune=zerolatency bitrate={BITRATE_VIDEO} key-int-max={KEY_INT_MAX} speed-preset=ultrafast ! "
        f"h264parse config-interval=1 ! "
        f"rtph264pay config-interval=1 pt=96 mtu={MTU_VIDEO} ! "
        f"udpsink host={VIDEO_HOST} port={PUERTO_VIDEO} sync={'true' if SYNC_ENABLED else 'false'} async=false"
    )

    # Crea el loop de mensajes de GStreamer
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_bus_message, loop)

    # Arranca el pipeline; si falla, muestra error y termina
    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("[RPI] Error al iniciar el pipeline")
        return

    threading.Thread(target=loop.run, daemon=True).start()
    print("[RPI] Transmisión iniciada.")
    actualizar_estado_leds(conexion_exitosa=True, transmision_activa=True)

def detener_transmision():
    """
    Detiene el pipeline de GStreamer y cierra el loop.
    Actualiza el estado de los LEDs para indicar que la transmisión ha parado.
    """
    global pipeline, loop

    if pipeline is None:
        print("[RPI] No hay transmisión activa.")
        return

    print("[RPI] Deteniendo transmisión...")
    pipeline.set_state(Gst.State.NULL)
    pipeline = None

    if loop and loop.is_running():
        loop.quit()
        loop = None

    actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)

def on_bus_message(bus, message, loop):
    """
    Callback para recibir eventos del bus de GStreamer:
    - EOS: fin de stream.
    - ERROR: error en el pipeline.
    - STATE_CHANGED: cambio de estado, útil para debug.
    """
    t = message.type
    if t == Gst.MessageType.EOS:
        print("[RPI] Fin de la transmisión")
        loop.quit()
        actualizar_estado_leds(conexion_exitosa=True, transmision_activa=False)
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"[RPI] Error en transmisión: {err}")
        loop.quit()
        actualizar_estado_leds(conexion_exitosa=False, transmision_activa=False)
    elif t == Gst.MessageType.STATE_CHANGED:
        old, new, _ = message.parse_state_changed()
        if message.src == pipeline:
            print(f"[RPI] Estado: {old.value_nick} -> {new.value_nick}")
    return True
    
def transmision_activa():
    """
    Indica si actualmente existe un pipeline activo.
    Devuelve True si la transmisión está en curso.
    """
    return pipeline is not None