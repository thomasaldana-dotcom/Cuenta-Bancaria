from django.shortcuts import render, redirect
from django.views import View

# Create your views here.


#Pantalla de inicio

class HomeView(View):
    def get(self, request): 
        return render(request, 'CuentaBancaria/home.html')
    
    def post(self, request):
        return redirect('login')


#Pantalla de login

class LoginView(View):
    def get(self, request):
        return render(request, 'CuentaBancaria/login.html')
    
    def post(self, request):
        return redirect('home')


#Pantalla de registro

class RegisterView(View):
    def get(self, request):
        return render(request, 'CuentaBancaria/register.html')
    
    def post(self, request):
        return redirect('login')

