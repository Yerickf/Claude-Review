import sys

problemas = []
try:
    import cv2
    if not (hasattr(cv2, "aruco") and hasattr(cv2.aruco, "ArucoDetector")):
        problemas.append("OpenCV %s não tem ArucoDetector (precisa de 4.7 ou superior)" % cv2.__version__)
    else:
        print("    OpenCV %s com ArucoDetector: ok" % cv2.__version__)
except ImportError:
    problemas.append("opencv-python não está instalado")

for mod in ("numpy", "PIL", "yaml", "fastapi", "uvicorn", "websockets"):
    try:
        __import__(mod)
    except ImportError:
        problemas.append("falta a biblioteca %s" % mod)

for p in problemas:
    print("    PROBLEMA:", p)
sys.exit(1 if problemas else 0)
