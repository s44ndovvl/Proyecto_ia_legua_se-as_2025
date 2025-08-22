#!/usr/bin/env python3
"""
Script para extraer imágenes de referencia del dataset3 y optimizar el rendimiento.
"""

import os
import shutil
import random
from collections import defaultdict

def find_class_images():
    """Encuentra una imagen representativa para cada clase del abecedario."""
    
    # Ruta base del dataset3
    dataset_path = os.path.join("..", "dataset3", "train")
    images_path = os.path.join(dataset_path, "images")
    labels_path = os.path.join(dataset_path, "labels")
    
    # Lista de clases esperadas (A-Z sin EYE)
    expected_classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    # Diccionario para almacenar archivos por clase
    class_files = defaultdict(list)
    
    print("Analizando archivos del dataset...")
    
    # Leer todas las etiquetas para clasificar por clase
    for label_file in os.listdir(labels_path):
        if label_file.endswith('.txt'):
            label_path = os.path.join(labels_path, label_file)
            
            try:
                with open(label_path, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        class_id = int(first_line.split()[0])
                        
                        # Mapear ID de clase a letra (según data.yaml)
                        class_mapping = {
                            0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'EYE', 6: 'F', 7: 'G', 8: 'H',
                            9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P',
                            17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'
                        }
                        
                        if class_id in class_mapping:
                            letter = class_mapping[class_id]
                            
                            # Solo procesar letras del abecedario (sin EYE)
                            if letter in expected_classes:
                                # Encontrar la imagen correspondiente
                                image_name = label_file.replace('.txt', '.jpg')
                                image_path = os.path.join(images_path, image_name)
                                
                                if os.path.exists(image_path):
                                    class_files[letter].append(image_path)
                                    
            except (ValueError, IndexError, IOError):
                continue
    
    print(f"Clases encontradas: {sorted(class_files.keys())}")
    print(f"Total de clases: {len(class_files)}")
    
    # Crear directorio de imágenes de referencia
    reference_dir = os.path.join("detector", "static", "detector", "reference_images")
    os.makedirs(reference_dir, exist_ok=True)
    
    # Seleccionar una imagen por clase
    selected_images = {}
    
    for letter in expected_classes:
        if letter in class_files and class_files[letter]:
            # Seleccionar una imagen aleatoria de la clase
            selected_image = random.choice(class_files[letter])
            
            # Copiar la imagen al directorio de referencia
            destination = os.path.join(reference_dir, f"{letter}.jpg")
            shutil.copy2(selected_image, destination)
            
            selected_images[letter] = f"detector/reference_images/{letter}.jpg"
            print(f"✓ {letter}: {os.path.basename(selected_image)}")
        else:
            print(f"✗ {letter}: No se encontraron imágenes")
    
    print(f"\nImágenes de referencia creadas: {len(selected_images)}")
    return selected_images

def create_optimized_reference_system():
    """Crea un sistema de referencia optimizado para mejor rendimiento."""
    
    # Extraer imágenes de referencia
    reference_images = find_class_images()
    
    # Crear archivo de configuración JavaScript
    js_config = """// Configuración de imágenes de referencia optimizada
const REFERENCE_CONFIG = {
    // Imágenes de referencia del dataset real
    images: {
"""
    
    for letter, path in sorted(reference_images.items()):
        js_config += f'        "{letter}": "{{% load static %}}{path}",\n'
    
    js_config += """    },
    
    // Configuración de rendimiento
    performance: {
        enableImagePreloading: true,
        useWebWorkers: false, // Deshabilitado para evitar overhead
        maxConcurrentDetections: 1,
        frameSkipRate: 2, // Procesar cada 2 frames para mejorar FPS
        cacheSize: 50
    },
    
    // Optimizaciones de UI
    ui: {
        animationDuration: 200, // Reducido de 300ms
        updateThrottle: 100, // Throttle de actualizaciones UI
        enableSmoothTransitions: true
    }
};

// Sistema de caché para imágenes
class ImageCache {
    constructor() {
        this.cache = new Map();
        this.maxSize = REFERENCE_CONFIG.performance.cacheSize;
    }
    
    get(key) {
        return this.cache.get(key);
    }
    
    set(key, value) {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }
    
    preloadImages() {
        Object.entries(REFERENCE_CONFIG.images).forEach(([letter, src]) => {
            if (!this.cache.has(letter)) {
                const img = new Image();
                img.onload = () => this.set(letter, img);
                img.src = src;
            }
        });
    }
}

// Instancia global del caché
const imageCache = new ImageCache();

// Precargar imágenes al cargar la página
if (REFERENCE_CONFIG.performance.enableImagePreloading) {
    document.addEventListener('DOMContentLoaded', () => {
        imageCache.preloadImages();
    });
}
"""
    
    # Guardar configuración JavaScript
    js_path = os.path.join("detector", "static", "detector", "js", "reference_config.js")
    os.makedirs(os.path.dirname(js_path), exist_ok=True)
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_config)
    
    print(f"✓ Configuración JavaScript guardada en: {js_path}")
    
    return reference_images

if __name__ == "__main__":
    print("=== Creando sistema de referencias optimizado ===")
    selected_images = create_optimized_reference_system()
    print(f"\n✓ Sistema creado exitosamente con {len(selected_images)} imágenes de referencia")
    print("\nPróximos pasos:")
    print("1. Actualizar templates/index.html para usar las nuevas imágenes")
    print("2. Optimizar detector_service.py para mejor rendimiento")
    print("3. Reiniciar el servidor Django")
