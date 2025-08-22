import cv2
import mediapipe as mp
from ultralytics import YOLO
from collections import deque, Counter
import numpy as np
import threading
import base64
from django.conf import settings
import os
import time

class SignLanguageDetector:
    def __init__(self):
        # Cargar YOLO model - ruta fija
        model_path = os.path.join(settings.BASE_DIR.parent, 'runs/detect/train3/weights/best.pt')

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No se encontró el modelo en: {model_path}")
            
        print(f"Cargando modelo desde: {model_path}")
        self.model = YOLO(model_path)
        
        # Inicializar MediaPipe con configuración optimizada
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,  # Aumentado para mejor precisión
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Diccionario de clases YOLO
        self.class_names = {
            0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H", 8: "I", 9: "J",
            10: "K", 11: "L", 12: "M", 13: "N", 14: "O", 15: "P", 16: "Q", 17: "R", 18: "S",
            19: "T", 20: "U", 21: "V", 22: "W", 23: "X", 24: "Y", 25: "Z"
        }
        
        # Historial para suavizado (aumentado para mejor estabilidad)
        self.history = deque(maxlen=7)
        
        # Estado de la detección
        self.current_letter = "NINGUNA"
        self.current_confidence = 0.0
        self.is_running = False
        self.cap = None
        
        # Variables de optimización de rendimiento
        self.frame_skip_counter = 0
        self.frame_skip_rate = 2  # Procesar cada 2 frames
        self.last_frame = None
        self.last_detection_time = 0
        self.detection_interval = 0.05  # 50ms mínimo entre detecciones
        
        # Cache para frames procesados
        self.frame_cache = {}
        self.cache_max_size = 10
        
        # Modo entrenamiento
        self.training_mode = False
        self.target_letter = None
        self.correct_detections = 0
        self.total_attempts = 0
        self.consecutive_correct = 0
        self.training_alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.current_training_index = 0
        
    def start_detection(self):
        """Iniciar la detección con diagnóstico mejorado"""
        try:
            print("=== INICIANDO DETECCIÓN DE CÁMARA ===")
            
            # Liberar cualquier cámara previa
            if self.cap is not None:
                self.cap.release()
                time.sleep(0.5)  # Esperar a que se libere
            
            # Probar diferentes índices de cámara
            camera_indices = [0, 1, 2]
            success = False
            
            for camera_index in camera_indices:
                print(f"Probando cámara índice {camera_index}...")
                
                try:
                    # Crear captura con configuración específica
                    self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # DirectShow en Windows
                    
                    if not self.cap.isOpened():
                        print(f"No se pudo abrir cámara {camera_index}")
                        continue
                    
                    # Configurar propiedades optimizadas
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Probar lectura de frame
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        height, width = test_frame.shape[:2]
                        print(f"✅ Cámara {camera_index} funcionando - Resolución: {width}x{height}")
                        success = True
                        break
                    else:
                        print(f"❌ Cámara {camera_index} no puede leer frames")
                        self.cap.release()
                        
                except Exception as e:
                    print(f"❌ Error con cámara {camera_index}: {str(e)}")
                    if self.cap:
                        self.cap.release()
                    continue
            
            if not success:
                error_msg = """
                ❌ No se pudo acceder a ninguna cámara.
                
                Soluciones sugeridas:
                1. Verificar que la cámara esté conectada y funcionando
                2. Cerrar otras aplicaciones que puedan estar usando la cámara (Zoom, Teams, etc.)
                3. Verificar permisos de cámara en Windows
                4. Reiniciar el navegador y la aplicación
                5. Verificar drivers de la cámara
                """
                print(error_msg)
                raise Exception("No se encontraron cámaras disponibles")
            
            self.is_running = True
            print("✅ Detección iniciada correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando detección: {str(e)}")
            self.is_running = False
            if self.cap:
                self.cap.release()
                self.cap = None
            raise e
        
    def stop_detection(self):
        """Detener la detección"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            
    def process_frame(self):
        """Procesar un frame optimizado con frame skipping y caché"""
        try:
            # Control de tiempo para evitar procesamiento excesivo
            current_time = time.time()
            if current_time - self.last_detection_time < self.detection_interval:
                # Retornar último frame conocido si está disponible
                if self.last_frame is not None:
                    return self.last_frame, self.current_letter, self.current_confidence
                    
            self.last_detection_time = current_time
            
            if not self.cap or not self.cap.isOpened():
                print("Error: Cámara no está disponible")
                return None, None, None
                
            ret, frame = self.cap.read()
            if not ret:
                print("Error: No se pudo leer frame de la cámara")
                return None, None, None
                
            # Implementar frame skipping para mejor rendimiento
            self.frame_skip_counter += 1
            if self.frame_skip_counter < self.frame_skip_rate:
                # Retornar último frame procesado si está disponible
                if self.last_frame is not None:
                    return self.last_frame, self.current_letter, self.current_confidence
                    
            self.frame_skip_counter = 0
            
            # Voltear frame para efecto espejo
            frame = cv2.flip(frame, 1)
            output_frame = frame.copy()
            
            detected_letter = "NINGUNA"
            confidence_percent = 0
            
            # YOLO detección con configuración optimizada
            results = self.model.predict(
                source=frame, 
                conf=0.6,  # Aumentado para mejor precisión
                show=False, 
                verbose=False,
                imgsz=640  # Tamaño de imagen optimizado
            )
            
            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    # Procesar solo la detección con mayor confianza
                    best_box = max(result.boxes, key=lambda x: float(x.conf[0]))
                    
                    # Coordenadas del bounding box
                    x1, y1, x2, y2 = map(int, best_box.xyxy[0])
                    cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    
                    # Clase y confianza YOLO
                    class_id = int(best_box.cls[0])
                    confidence = float(best_box.conf[0]) * 100
                    letter = self.class_names.get(class_id, "?")
                    
                    # Validación del tamaño del recorte
                    hand_region = frame[y1:y2, x1:x2]
                    if hand_region.size == 0 or hand_region.shape[0] < 50 or hand_region.shape[1] < 50:
                        continue
                        
                    # Validación con MediaPipe (solo si YOLO tiene alta confianza)
                    valid = True
                    if confidence > 60:  # Solo validar con MediaPipe si YOLO está confiado
                        hand_region_rgb = cv2.cvtColor(hand_region, cv2.COLOR_BGR2RGB)
                        results_hands = self.hands.process(hand_region_rgb)
                        
                        if results_hands.multi_hand_landmarks:
                            for hand_landmarks in results_hands.multi_hand_landmarks:
                                # Convertir coordenadas relativas a absolutas de forma optimizada
                                h_region, w_region = hand_region.shape[:2]
                                h_frame, w_frame = frame.shape[:2]
                                
                                for landmark in hand_landmarks.landmark:
                                    landmark.x = (landmark.x * w_region + x1) / w_frame
                                    landmark.y = (landmark.y * h_region + y1) / h_frame
                                
                                # Dibujar landmarks de forma más eficiente
                                self.mp_drawing.draw_landmarks(
                                    output_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                                )
                        else:
                            valid = False
                    
                    # Validación y suavizado temporal
                    if valid:
                        self.history.append(letter)
                        detected_letter = letter
                        confidence_percent = int(confidence)
                        
                        # Suavizado temporal mejorado
                        if len(self.history) >= 3:  # Requerir al menos 3 detecciones
                            counter = Counter(self.history)
                            most_common = counter.most_common(1)[0]
                            if most_common[1] >= 2:  # Al menos 2 coincidencias
                                detected_letter = most_common[0]
                    
                    # Mostrar información en pantalla de forma optimizada
                    text = f"{detected_letter} ({confidence_percent}%)"
                    
                    # Colores según confianza
                    if confidence_percent >= 70:
                        color = (0, 255, 0)  # Verde
                    elif confidence_percent >= 50:
                        color = (0, 255, 255)  # Amarillo
                    else:
                        color = (0, 165, 255)  # Naranja
                    
                    # Texto más grande y legible
                    cv2.putText(output_frame, text, (x1, y1 - 15),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 4)
                    
                    break  # Solo procesar la mejor detección
            
            # Información general optimizada
            cv2.putText(output_frame, "DETECTOR DE LENGUAJE DE SEÑAS", (10, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            
            cv2.putText(output_frame, f"LETRA: {detected_letter}", (10, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)
            
            cv2.putText(output_frame, f"CONFIANZA: {confidence_percent}%", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)
            
            # Actualizar estado
            self.current_letter = detected_letter
            self.current_confidence = confidence_percent
            
            # Verificar entrenamiento si está activo
            training_result = None
            if self.training_mode:
                training_result = self.check_training_success(detected_letter, confidence_percent)
                
                # Agregar información de entrenamiento en pantalla
                if self.target_letter:
                    cv2.putText(output_frame, f"OBJETIVO: {self.target_letter}", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
                    
                    cv2.putText(output_frame, f"ACIERTOS: {self.correct_detections}/{self.total_attempts}", (10, 190), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Codificar frame como JPEG con calidad optimizada
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # Calidad reducida para mejor rendimiento
            _, buffer = cv2.imencode('.jpg', output_frame, encode_params)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Actualizar caché con el último frame procesado
            self.last_frame = frame_base64
            
            # Gestión de caché para evitar uso excesivo de memoria
            if len(self.frame_cache) >= self.cache_max_size:
                self.frame_cache.clear()
            
            return frame_base64, detected_letter, confidence_percent, training_result
            
        except Exception as e:
            print(f"Error procesando frame: {e}")
            return None, None, None, None
    
    def get_current_detection(self):
        """Obtener la detección actual"""
        return {
            'letter': self.current_letter,
            'confidence': self.current_confidence
        }
    
    def start_training_mode(self):
        """Iniciar modo entrenamiento"""
        import random
        self.training_mode = True
        self.target_letter = random.choice(self.training_alphabet)
        self.correct_detections = 0
        self.total_attempts = 0
        self.consecutive_correct = 0
        print(f"Modo entrenamiento iniciado. Letra objetivo: {self.target_letter}")
        
    def stop_training_mode(self):
        """Detener modo entrenamiento"""
        self.training_mode = False
        self.target_letter = None
        
    def get_next_training_letter(self):
        """Obtener siguiente letra para entrenar"""
        import random
        self.target_letter = random.choice(self.training_alphabet)
        return self.target_letter
        
    def check_training_success(self, detected_letter, confidence):
        """Verificar si la detección es correcta en modo entrenamiento"""
        if not self.training_mode or not self.target_letter:
            return None
            
        self.total_attempts += 1
        
        if detected_letter == self.target_letter and confidence >= 70:
            self.correct_detections += 1
            self.consecutive_correct += 1
            
            # Obtener nueva letra después de éxito
            import random
            old_letter = self.target_letter
            self.target_letter = random.choice(self.training_alphabet)
            
            return {
                'success': True,
                'message': f'¡FELICITACIONES! 🎉 Hiciste correctamente la "{old_letter}"',
                'next_letter': self.target_letter,
                'stats': {
                    'correct': self.correct_detections,
                    'total': self.total_attempts,
                    'consecutive': self.consecutive_correct,
                    'accuracy': round((self.correct_detections / self.total_attempts) * 100, 1) if self.total_attempts > 0 else 0
                }
            }
        else:
            self.consecutive_correct = 0
            if detected_letter != self.target_letter and detected_letter != "NINGUNA":
                return {
                    'success': False,
                    'message': f'Casi! Detecté "{detected_letter}" pero necesito "{self.target_letter}"',
                    'target_letter': self.target_letter
                }
        
        return None
        
    def get_training_status(self):
        """Obtener estado del entrenamiento"""
        if not self.training_mode:
            return None
            
        return {
            'active': True,
            'target_letter': self.target_letter,
            'correct_detections': self.correct_detections,
            'total_attempts': self.total_attempts,
            'consecutive_correct': self.consecutive_correct,
            'accuracy': round((self.correct_detections / self.total_attempts) * 100, 1) if self.total_attempts > 0 else 0
        }

# Instancia global del detector
detector = SignLanguageDetector()
