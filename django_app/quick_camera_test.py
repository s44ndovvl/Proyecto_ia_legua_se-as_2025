import cv2
import sys

print("Probando acceso a cámara...")

try:
    # Probar con DirectShow (Windows)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ Cámara funcionando con DirectShow")
            height, width = frame.shape[:2]
            print(f"Resolución: {width}x{height}")
        else:
            print("❌ No se pueden leer frames con DirectShow")
        cap.release()
    else:
        print("❌ No se puede abrir cámara con DirectShow")
        
    # Probar sin backend específico
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ Cámara funcionando sin backend específico")
        else:
            print("❌ No se pueden leer frames sin backend")
        cap.release()
    else:
        print("❌ No se puede abrir cámara sin backend")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("Diagnóstico completado.")
