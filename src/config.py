# src/config.py

ID_RPI = "rpi_001"
SERVIDOR_URL = "http://192.168.1.91:5000"
PUERTO_VIDEO = 5000

# Comando GStreamer
GST_COMMAND = (
    "gst-launch-1.0 libcamerasrc ! "
    "video/x-raw,width=640,height=480,framerate=30/1 ! "
    "videoconvert ! "
    "x264enc tune=zerolatency bitrate=1000 ! "
    "h264parse config-interval=1 ! "
    "rtph264pay config-interval=1 pt=96 mtu=1200 ! "
    f"udpsink host=192.168.1.91 port={PUERTO_VIDEO} sync=false async=false"
)
