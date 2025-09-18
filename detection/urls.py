from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('detect/', views.detect_retinopathy, name='detect_retinopathy'),
    path('history/', views.test_history, name='test_history'),
    # urls.py
    path("diet/", views.dietary_recommendations, name="dietary_recommendations"),

    path('diet/<str:stage>/<str:country>/', views.dietary_recommendations, name='dietary_recommendations_country'),

    path('change-language/', views.change_language, name='change_language'),
    path('result/<int:test_id>/', views.detection_result, name='detection_result'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('test/delete/<int:test_id>/', views.delete_test, name='delete_test'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),
]