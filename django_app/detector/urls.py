from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start_detection, name='start_detection'),
    path('stop/', views.stop_detection, name='stop_detection'),
    path('detection-data/', views.get_detection_data, name='get_detection_data'),
    path('video-feed/', views.video_feed, name='video_feed'),
    path('toggle-detection/', views.toggle_detection, name='toggle_detection'),
    path('test-camera/', views.test_camera, name='test_camera'),
    path('test-model/', views.test_model, name='test_model'),
    path('start-training/', views.start_training, name='start_training'),
    path('stop-training/', views.stop_training, name='stop_training'),
    path('training-feedback/', views.get_training_feedback, name='training_feedback'),
]
