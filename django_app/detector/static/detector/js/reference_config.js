// Configuración de imágenes de referencia optimizada
const REFERENCE_CONFIG = {
    // Imágenes de referencia del dataset real
    images: {
        "A": "{% load static %}detector/reference_images/A.jpg",
        "B": "{% load static %}detector/reference_images/B.jpg",
        "C": "{% load static %}detector/reference_images/C.jpg",
        "D": "{% load static %}detector/reference_images/D.jpg",
        "E": "{% load static %}detector/reference_images/E.jpg",
        "F": "{% load static %}detector/reference_images/F.jpg",
        "G": "{% load static %}detector/reference_images/G.jpg",
        "H": "{% load static %}detector/reference_images/H.jpg",
        "I": "{% load static %}detector/reference_images/I.jpg",
        "J": "{% load static %}detector/reference_images/J.jpg",
        "K": "{% load static %}detector/reference_images/K.jpg",
        "L": "{% load static %}detector/reference_images/L.jpg",
        "M": "{% load static %}detector/reference_images/M.jpg",
        "N": "{% load static %}detector/reference_images/N.jpg",
        "O": "{% load static %}detector/reference_images/O.jpg",
        "P": "{% load static %}detector/reference_images/P.jpg",
        "Q": "{% load static %}detector/reference_images/Q.jpg",
        "R": "{% load static %}detector/reference_images/R.jpg",
        "S": "{% load static %}detector/reference_images/S.jpg",
        "T": "{% load static %}detector/reference_images/T.jpg",
        "U": "{% load static %}detector/reference_images/U.jpg",
        "V": "{% load static %}detector/reference_images/V.jpg",
        "W": "{% load static %}detector/reference_images/W.jpg",
        "X": "{% load static %}detector/reference_images/X.jpg",
        "Y": "{% load static %}detector/reference_images/Y.jpg",
        "Z": "{% load static %}detector/reference_images/Z.jpg",
    },
    
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
