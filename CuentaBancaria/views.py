from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente, Transaccion
from django.db import transaction
from django.conf import settings
from deep_translator import GoogleTranslator

import random
import requests

# Create your views here.


# Pantalla de inicio


class HomeView(View):
    def get(self, request):
        return render(request, "CuentaBancaria/home.html")

    def post(self, request):
        return redirect("login")


# Pantalla de login


class LoginView(View):
    def get(self, request):
        return render(request, "CuentaBancaria/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("menu")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect("login")


# Pantalla de registro


class RegisterView(View):
    def get(self, request):
        return render(request, "CuentaBancaria/register.html")

    def post(self, request):
        username = request.POST.get("username")
        email = username
        name = request.POST.get("name")
        lastname = request.POST.get("lastname")
        age = request.POST.get("age")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        numero_cuenta = random.randint(1000000000, 9999999999)

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(
                request, "El usuario/correo ya existe, si no tiene cuenta cree una"
            )
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=username,
            password=password,
            first_name=name,
            last_name=lastname,
        )

        Cliente.objects.create(
            user=user,
            email=email,
            age=age,
            name=name,
            lastname=lastname,
            numero_cuenta=numero_cuenta,
            saldo=0,
        )

        messages.success(request, "Usuario creado correctamente")

        return redirect("login")


# Pantalla de menu


class menuView(LoginRequiredMixin, View):
    login_url = "login"

    #API

    def obtener_frase_api(self):
        url = "https://dummyjson.com/quotes/random"

        try:
            response = requests.get(url, timeout = 3, verify = False)
            data = response.json()

            frase_en = data.get("quote")
            autor = data.get("author")

            traductor = GoogleTranslator(source='en', target='es')
            frase_es = traductor.translate(frase_en)

            return{
                "contenido_en": frase_en,
                "contenido_es": frase_es,
                "autor": autor,
            }
        except Exception as e:
            print("error",e)
            return{
                "contenido_en": "No se pudo obtener la frase",
                "contenido_es": "No se pudo obtener la frase",
                "autor": "ThomBank"
            }


    def get(self, request):
        datos_api = self.obtener_frase_api()
        cliente = Cliente.objects.get(user=request.user)
        context = {
            "cliente": cliente,
            "mostrar_deposito": False,
            "mostrar_retiro": False,
            "mostrar_transferencia": False,
            "frase_en": datos_api["contenido_en"],
            "frase_es": datos_api["contenido_es"],
            "autor": datos_api["autor"],
        }
        return render(request, "CuentaBancaria/menu.html", context)

    def post(self, request):
        datos_api = self.obtener_frase_api()
        cliente = Cliente.objects.get(user=request.user)
        context = {
            "cliente": cliente,
            "mostrar_deposito": False,
            "mostrar_retiro": False,
            "mostrar_transferencia": False,
            "frase_en": datos_api["contenido_en"],
            "frase_es": datos_api["contenido_es"],
            "autor": datos_api["autor"],
        }

        if request.method == "POST":
            accion = request.POST.get("accion")
            monto = request.POST.get("monto")
            cuenta_destino = request.POST.get("cuenta_destino")

            # Navegacion del menu
            if accion == "depositar":
                context["mostrar_deposito"] = True

            elif accion == "retirar":
                context["mostrar_retiro"] = True

            elif accion == "transferencia":
                context["mostrar_transferencia"] = True

            elif accion == "confirmar_deposito":
                if monto:
                    cliente.saldo += int(monto)
                    cliente.save()

                    #Guardar historial de deposito

                    Transaccion.objects.create(
                        cliente = cliente,
                        tipo = "Deposito",
                        monto = int(monto),
                    )
                    messages.success(request, "Deposito exitoso")

                else:
                    messages.error(request, "Monto inválido")
                    context["mostrar_deposito"] = True

            elif accion == "confirmar_retiro":
                if monto:
                    if int(monto) > cliente.saldo:
                        messages.error(request, "No tienes saldo suficiente")
                        context["mostrar_retiro"] = True
                    else:
                        cliente.saldo -= int(monto)
                        cliente.save()

                        #Guardar historial de retiro

                        Transaccion.objects.create(
                            cliente = cliente,
                            tipo = "Retiro",
                            monto = int(monto),
                        )

                        messages.success(request, "Retiro exitoso")
                else:
                    messages.error(request, "Monto inválido")
                    context["mostrar_retiro"] = True

            elif accion == "confirmar_transferencia":
                if not monto or not cuenta_destino:
                    messages.error(request, "Datos incompletos")
                    context["mostrar_transferencia"] = True
                else:
                    if int(monto) > cliente.saldo:
                        messages.error(request, "No tienes saldo suficiente")
                        context["mostrar_transferencia"] = True
                    else:
                        try:
                            cliente_destino = Cliente.objects.get(
                                numero_cuenta=cuenta_destino
                            )
                            if cliente_destino == cliente:
                                messages.error(
                                    request, "No puedes transferir a ti mismo"
                                )
                                context["mostrar_transferencia"] = True
                            else:
                                with transaction.atomic():
                                    cliente.saldo -= int(monto)
                                    cliente.save()
                                    cliente_destino.saldo += int(monto)
                                    cliente_destino.save()

                                    #Guardar historial de transferencia

                                    Transaccion.objects.create(
                                        cliente = cliente,
                                        tipo = "Transferencia",
                                        monto = int(monto),
                                        destinatario = cliente_destino,
                                    )
                                messages.success(request, "Transferencia exitosa")

                        except Cliente.DoesNotExist:
                            messages.error(request, "No se encontro la cuenta destino")
                            context["mostrar_transferencia"] = True

        return render(request, "CuentaBancaria/menu.html", context)





#Pantalla Historial de Transacciones

class HistorialTransaccionesView(View):
    login_url = "login"

    def get(self, request):
        cliente = Cliente.objects.get(user=request.user)
        transacciones = Transaccion.objects.filter(cliente=cliente).order_by("-fecha")

        context = {
            "transacciones": transacciones
        }
        return render(request, "CuentaBancaria/historial_transacciones.html", context)

    def post(self, request):
        transaccion_id = request.POST.get("transaccion_id")

        if transaccion_id:
            transaccion = get_object_or_404(Transaccion, id=transaccion_id, cliente__user=request.user)
            transaccion.delete()
            messages.success(request, "Transaccion eliminada exitosamente")
            return redirect("historial_transacciones")



#APIS

#Tasa de Cambio


class TasaCambioView(View):
    def get(self, request):
        context = self.obtener_tasas()
        return render(request, "CuentaBancaria/tasa_cambio.html", context)

    def post(self, request):
        monto = float(request.POST.get("monto"))
        unidad = request.POST.get("unidad")

        context = self.obtener_tasas()

        tasas = context["tasas"]
        tasa_seleccionada = tasas[unidad]

        resultado = monto / tasa_seleccionada

        context["resultado"] = round(resultado, 2)
        context["monto"] = monto
        context["unidad"] = unidad

        return render(request, "CuentaBancaria/tasa_cambio.html", context)

    def obtener_tasas(self):
        url = "https://api.exchangerate-api.com/v4/latest/COP"
        response = requests.get(url)
        data = response.json()

        # invertir tasas para que sea: 1 USD = X COP
        tasas = {
            "USD": round(1 / data["rates"]["USD"], 2),
            "EUR": round(1 / data["rates"]["EUR"], 2),
            "GBP": round(1 / data["rates"]["GBP"], 2),
        }

        return {
            "tasas": tasas
        }




#Chatbot

class ChatbotView(View):
    def get(self, request):
        return render(request, "CuentaBancaria/chatbot.html")

    def post(self, request):
        mensaje_usuario = request.POST.get("mensaje_usuario")
        respuesta_bot = self.obtener_respuesta_chat(mensaje_usuario)

        context = {
            "mensaje_usuario": mensaje_usuario,
            "respuesta_bot": respuesta_bot
        }

        return render(request, "CuentaBancaria/chatbot.html", context)

    
    def obtener_respuesta_chat(self, mensaje_usuario):
        url = "https://api.cerebras.ai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "llama3.1-8b",
            "messages": [
                {"role": "system", "content": "Eres un asistente útil para un banco y das consejos financieros simples."},
                {"role": "user", "content": mensaje_usuario},
            ],
            "temperature": 0.7,
            "max_tokens": 200,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code != 200:
                print("Error Cerebras:", response.text)
                return "El bot no pudo responder ahora mismo."

            respuesta = response.json()
            return respuesta["choices"][0]["message"]["content"]

        except Exception as e:
            print("Error Cerebras:", e)
            return "El bot no pudo responder ahora mismo."
















# Cerrar sesion

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")
