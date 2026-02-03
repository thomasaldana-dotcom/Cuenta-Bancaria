import zoneinfo
from django.utils import timezone 

class ZonaHorariaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                zona_usuario = request.user.cliente.zona_horaria
                timezone.activate(zoneinfo.ZoneInfo(zona_usuario))
            except Exception:
                timezone.deactivate()
        else:
            timezone.deactivate()
            
        response = self.get_response(request)
        return response
