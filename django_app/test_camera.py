import cv2
import numpy as np

def test_camera_access():
    """Función para probar el acceso a la cámara"""
    print("=== DIAGNÓSTICO DE CÁMARA ===")
    
    # Probar diferentes índices de cámara
    camera_indices = [0, 1, 2, -1]
    working_cameras = []
    
    for i in camera_indices:
        print(f"\nProbando cámara índice {i}...")
        try:
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"✅ Cámara {i}: FUNCIONANDO")
                    print(f"   Resolución: {width}x{height}")
                    
                    # Probar propiedades
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    print(f"   FPS: {fps}")
                    
                    working_cameras.append(i)
                else:
                    print(f"❌ Cámara {i}: No puede leer frames")
            else:
                print(f"❌ Cámara {i}: No se puede abrir")
            
            cap.release()
        except Exception as e:
            print(f"❌ Cámara {i}: Error - {str(e)}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Cámaras funcionando: {working_cameras}")
    
    if not working_cameras:
        print("❌ No se encontraron cámaras funcionando")
        print("\nSoluciones sugeridas:")
        print("1. Verificar que la cámara esté conectada")
        print("2. Cerrar otras aplicaciones que usen la cámara")
        print("3. Reiniciar el sistema")
        print("4. Verificar drivers de la cámara")
    else:
        print(f"✅ Usar cámara índice: {working_cameras[0]}")
    
    return working_cameras

if __name__ == "__main__":
    test_camera_access()
