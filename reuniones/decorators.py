# reuniones/decorators.py
from django.shortcuts import redirect
from django.core.cache import cache
from functools import wraps

def zoom_login_required(function):
    """
    Decorador personalizado que verifica si existe el token de Zoom en la caché.
    Si no existe, redirige a la vista 'zoom_login'.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # Verificamos el token igual que lo haces en tu vista de 'inicio'
        if cache.get('zoom_access_token') is None:
            # Si no hay token, mandamos a iniciar el flujo OAuth
            return redirect('zoom_login') 
        return function(request, *args, **kwargs)
    return wrap