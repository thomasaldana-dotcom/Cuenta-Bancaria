from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('menu/', views.menuView.as_view(), name='menu'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('tasa_cambio/', views.TasaCambioView.as_view(), name='tasa_cambio'),
    path('chatbot/', views.ChatbotView.as_view(), name='chatbot'),
]
