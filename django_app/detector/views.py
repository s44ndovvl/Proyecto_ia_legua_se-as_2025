from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import time
import base64
from .detector_service import detector

def index(request):
    """Página principal del detector"""
    return render(request, 'index.html')

@csrf_exempt
def start_detection(request):
    """Iniciar la detección de señas con diagnóstico mejorado"""
    try:
        print("=== VISTA START_DETECTION LLAMADA ===")
        success = detector.start_detection()
        if success:
            return JsonResponse({
                'status': 'success', 
                'message': 'Detección iniciada correctamente',
                'camera_info': 'Cámara conectada y funcionando'
            })
        else:
            return JsonResponse({
                'status': 'error', 
                'message': 'No se pudo iniciar la detección'
            })
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error en start_detection: {error_msg}")
        
        # Mensajes de error más útiles
        if "No se encontraron cámaras disponibles" in error_msg:
            user_message = """No se pudo acceder a la cámara. 

Soluciones:
• Verifica que tu cámara esté conectada
• Cierra otras aplicaciones que usen la cámara (Zoom, Teams, etc.)
• Reinicia el navegador
• Verifica permisos de cámara en Windows"""
        else:
            user_message = f"Error técnico: {error_msg}"
        
        return JsonResponse({
            'status': 'error', 
            'message': user_message,
            'technical_details': error_msg
        })

@csrf_exempt
def stop_detection(request):
    """Detener la detección de señas"""
    try:
        detector.stop_detection()
        return JsonResponse({'status': 'success', 'message': 'Detección detenida'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def get_detection_data(request):
    """Obtener datos de detección actual"""
    try:
        if not detector.is_running:
            return JsonResponse({
                'letter': 'DETENIDO',
                'confidence': 0,
                'status': 'stopped'
            })
            
        frame_data, letter, confidence, training_result = detector.process_frame()
        
        if frame_data is None:
            return JsonResponse({
                'letter': 'ERROR',
                'confidence': 0,
                'status': 'error'
            })
            
        response_data = {
            'frame': frame_data,
            'letter': letter,
            'confidence': confidence,
            'status': 'running'
        }
        
        # Agregar información de entrenamiento si está activo
        training_status = detector.get_training_status()
        if training_status:
            response_data['training'] = training_status
            
        # Agregar resultado de entrenamiento si existe
        if training_result:
            response_data['training_result'] = training_result
            
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'letter': 'ERROR',
            'confidence': 0,
            'status': 'error',
            'message': str(e)
        })

def video_feed(request):
    """Stream de video para la cámara"""
    def generate():
        while detector.is_running:
            frame_data, letter, confidence, training_result = detector.process_frame()
            if frame_data:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       base64.b64decode(frame_data) + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return StreamingHttpResponse(generate(), 
                               content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
@require_http_methods(["POST"])
def toggle_detection(request):
    """Alternar entre iniciar y detener detección"""
    try:
        data = json.loads(request.body)
        action = data.get('action', 'toggle')
        
        if action == 'start' or (action == 'toggle' and not detector.is_running):
            detector.start_detection()
            return JsonResponse({
                'status': 'success', 
                'action': 'started',
                'message': 'Detección iniciada'
            })
        else:
            detector.stop_detection()
            return JsonResponse({
                'status': 'success', 
                'action': 'stopped',
                'message': 'Detección detenida'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        })

@csrf_exempt
def test_camera(request):
    """Probar si la cámara está disponible"""
    import cv2
    try:
        # Probar diferentes índices de cámara
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    return JsonResponse({
                        'status': 'success',
                        'camera_index': i,
                        'message': f'Cámara encontrada en índice {i}'
                    })
        
        return JsonResponse({
            'status': 'error',
            'message': 'No se encontró ninguna cámara disponible'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error probando cámara: {str(e)}'
        })

@csrf_exempt  
def test_model(request):
    """Probar si el modelo está cargado correctamente"""
    try:
        from .detector_service import detector
        model_info = {
            'model_loaded': hasattr(detector, 'model'),
            'class_names_count': len(detector.class_names),
            'is_running': detector.is_running
        }
        return JsonResponse({
            'status': 'success',
            'model_info': model_info
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error con el modelo: {str(e)}'
        })

@csrf_exempt
def start_training(request):
    """Iniciar modo entrenamiento"""
    try:
        from .detector_service import detector
        detector.start_training_mode()
        return JsonResponse({
            'status': 'success',
            'target_letter': detector.target_letter,
            'message': f'Modo entrenamiento iniciado. Haz la letra "{detector.target_letter}"'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error iniciando entrenamiento: {str(e)}'
        })

@csrf_exempt
def stop_training(request):
    """Detener modo entrenamiento"""
    try:
        from .detector_service import detector
        stats = detector.get_training_status()
        detector.stop_training_mode()
        return JsonResponse({
            'status': 'success',
            'final_stats': stats,
            'message': 'Entrenamiento terminado'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error deteniendo entrenamiento: {str(e)}'
        })

@csrf_exempt
def get_training_feedback(request):
    """Obtener retroalimentación del entrenamiento"""
    try:
        from .detector_service import detector
        if not detector.training_mode:
            return JsonResponse({
                'active': False,
                'message': 'Modo entrenamiento no activo'
            })
            
        # Verificar si hay una detección reciente correcta
        if detector.current_letter and detector.current_confidence >= 70:
            result = detector.check_training_success(detector.current_letter, detector.current_confidence)
            if result:
                return JsonResponse(result)
                
        return JsonResponse({
            'active': True,
            'target_letter': detector.target_letter,
            'current_letter': detector.current_letter,
            'confidence': detector.current_confidence
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error obteniendo feedback: {str(e)}'
        })

@csrf_exempt
def test_camera(request):
    """Probar acceso a la cámara sin iniciar detección completa"""
    try:
        import cv2
        
        results = {
            'available_cameras': [],
            'errors': [],
            'recommendation': ''
        }
        
        # Probar diferentes índices de cámara
        for i in [0, 1, 2]:
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        results['available_cameras'].append({
                            'index': i,
                            'resolution': f"{width}x{height}",
                            'status': 'working'
                        })
                    else:
                        results['errors'].append(f"Cámara {i}: No puede leer frames")
                else:
                    results['errors'].append(f"Cámara {i}: No se puede abrir")
                cap.release()
            except Exception as e:
                results['errors'].append(f"Cámara {i}: {str(e)}")
        
        if results['available_cameras']:
            results['recommendation'] = f"Usar cámara índice {results['available_cameras'][0]['index']}"
            return JsonResponse({
                'status': 'success',
                'message': f"Se encontraron {len(results['available_cameras'])} cámaras funcionando",
                'data': results
            })
        else:
            results['recommendation'] = "Verificar conexión de cámara y permisos"
            return JsonResponse({
                'status': 'error',
                'message': "No se encontraron cámaras funcionando",
                'data': results
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Error durante test de cámara: {str(e)}"
        })
