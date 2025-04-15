# transmisor.py
import gi
import threading
import time
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

# Inicializar GStreamer solo una vez
Gst.init(None)

pipeline = None
loop = None

def iniciar_transmision():
    global pipeline, loop

    if pipeline is not None:
        print("[RPI] Transmisión ya en curso.")
        return

    print("[RPI] Iniciando transmisión de video...")

    pipeline = Gst.parse_launch(
        "libcamerasrc ! "
        "video/x-raw,width=640,height=480,format=NV12,framerate=30/1 ! "
        "videoconvert ! "
        "x264enc tune=zerolatency bitrate=1000 key-int-max=15 speed-preset=ultrafast ! "
        "h264parse config-interval=1 ! "
        "rtph264pay config-interval=1 pt=96 mtu=1200 ! "
        "udpsink host=192.168.1.91 port=5000 sync=false async=false"
    )

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_bus_message, loop)

    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("[RPI] Error al iniciar el pipeline")
        return

    threading.Thread(target=loop.run, daemon=True).start()
    print("[RPI] Transmisión iniciada.")

def detener_transmision():
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

def on_bus_message(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        print("[RPI] Fin de la transmisión")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"[RPI] Error en transmisión: {err}")
        loop.quit()
    elif t == Gst.MessageType.STATE_CHANGED:
        old, new, _ = message.parse_state_changed()
        if message.src == pipeline:
            print(f"[RPI] Estado: {old.value_nick} -> {new.value_nick}")
    return True
    
def transmision_activa():
    return pipeline is not None
