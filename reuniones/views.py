# ========================================
# reuniones/views.py
# Vistas para OAuth User-Level (gratuito)
# ========================================
from .models import Reunion # Asegúrate de que esta línea esté arriba
from django.utils import timezone # Para los contadores de fecha
from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import zoom_login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.cache import cache
from .zoom_service import ZoomService
from .models import Reunion, Participante
from datetime import datetime

from .decorators import zoom_login_required
from django.contrib.auth.models import User
from django.contrib.auth import login

from django.views.decorators.csrf import csrf_exempt  # Desactivar CSRF para webhook
from django.http import JsonResponse  # Respuesta JSON
import json  # Parser JSON

# =====================================
# VISTAS DE AUTENTICACIÓN OAUTH
# =====================================

def zoom_login(request):
    """
    Redirige al usuario a la página de autorización de Zoom.
    Primera vez que el usuario autoriza la app.
    """
    zoom_service = ZoomService()
    authorization_url = zoom_service.get_authorization_url()
    return redirect(authorization_url)


def zoom_oauth_callback(request):
    """
    Callback de Zoom después de que el usuario autoriza.
    Recibe el código y lo intercambia por access token.
    """
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, '❌ Error: No se recibió código de autorización')
        return redirect('inicio')
    
    try:
        zoom_service = ZoomService()
        token_data = zoom_service.exchange_code_for_token(code)
        
        user_info = zoom_service.get_user_info() # Necesitarías implementar esto
        email = user_info['email']
        
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        login(request, user)
        
        messages.success(request, '✅ Autorización exitosa! Ya puedes crear reuniones.')
        return redirect('inicio')
    
    except Exception as e:
        messages.error(request, f'❌ Error al autorizar: {str(e)}')
        return redirect('inicio')


def verificar_autorizacion(request):
    """
    API para verificar si ya hay token (usuario ya autorizó).
    Usado por JavaScript en el frontend.
    """
    tiene_token = cache.get('zoom_access_token') is not None
    return JsonResponse({'autorizado': tiene_token})


# =====================================
# VISTAS PRINCIPALES
# =====================================

from django.utils import timezone
from .models import Reunion

def inicio(request):
    """
    Página de inicio con todos los contadores activos.
    """
    tiene_token = cache.get('zoom_access_token') is not None
    ahora = timezone.now() # Obtenemos la fecha y hora de este preciso momento

    context = {
        'autorizado': tiene_token,
        # Cuenta todas sin filtro
        'total_reuniones': Reunion.objects.count(),
        
        # Filtra las que su 'fecha_inicio' es MAYOR que ahora (__gt = Greater Than)
        'proximas': Reunion.objects.filter(fecha_inicio__gt=ahora).count(),
        
        # Filtra las que su 'fecha_inicio' es MENOR que ahora (__lt = Less Than)
        'pasadas': Reunion.objects.filter(fecha_inicio__lt=ahora).count(),
    }
    
    return render(request, 'reuniones/inicio.html', context)
    """
    Página de inicio con contadores reales.
    """
    tiene_token = cache.get('zoom_access_token') is not None
    ahora = timezone.now()

    # --- AQUÍ AGREGAMOS LA MAGIA ---
    context = {
        'autorizado': tiene_token,
        'total_reuniones': Reunion.objects.count(),
        'proximas': Reunion.objects.filter(fecha_inicio__gt=ahora).count(),
        'pasadas': Reunion.objects.filter(fecha_inicio__lt=ahora).count(),
    }
    # -------------------------------
    
    return render(request, 'reuniones/inicio.html', context)


@zoom_login_required
def crear_reunion(request):
    """
    Vista para crear una reunión de Zoom.
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            topic = request.POST.get('topic')
            start_time = request.POST.get('start_time')  # "2024-03-15T10:00"
            duration = int(request.POST.get('duration'))
            
            # Convertir a formato ISO 8601
            # start_datetime = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            # start_time_iso = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
            
            fecha_str = request.POST.get('start_date')  # Ejemplo: "2026-01-28"
            hora_str = request.POST.get('start_time')
            fecha_completa_str = f"{fecha_str}T{hora_str}"
            start_datetime = datetime.strptime(fecha_completa_str, '%Y-%m-%dT%H:%M')
            start_time_iso = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Crear reunión en Zoom
            zoom_service = ZoomService()
            meeting_data = zoom_service.crear_reunion(
                topic=topic,
                start_time=start_time_iso,
                duration=duration
            )
            
            email_zoom = meeting_data.get('host_email') 
            
            if not email_zoom:
                # Fallback por si la API cambia: Usar un usuario por defecto (el admin)
                usuario_asignado = User.objects.filter(is_superuser=True).first()
            else:
                # B. Buscamos si existe un usuario con ese email, si no, lo creamos
                usuario_asignado, created = User.objects.get_or_create(
                    username=email_zoom,  # Usamos el email como nombre de usuario
                    defaults={'email': email_zoom}
                )
            
            # Guardar en base de datos
            reunion = Reunion.objects.create(
                titulo=topic,
                zoom_meeting_id=meeting_data['id'],
                join_url=meeting_data['join_url'],
                start_url=meeting_data['start_url'],
                fecha_inicio=start_datetime,
                duracion=duration,
                creador=usuario_asignado
            )
            
            messages.success(request, f'✅ Reunión "{topic}" creada exitosamente!')
            return redirect('lista_reuniones')
        
        except Exception as e:
            messages.error(request, f'❌ Error al crear reunión: {str(e)}')
    
    return render(request, 'reuniones/crear_reunion.html')


@zoom_login_required
def lista_reuniones(request):
    """
    Lista todas las reuniones creadas.
    """
    reuniones = Reunion.objects.filter(creador=request.user)
    
    context = {
        'reuniones': reuniones
    }
    return render(request, 'reuniones/lista_reuniones.html', context)


@zoom_login_required
def detalle_reunion(request, reunion_id):
    """
    Muestra detalles de una reunión específica.
    """
    reunion = get_object_or_404(Reunion, id=reunion_id, creador=request.user)
    
    context = {
        'reunion': reunion
    }
    return render(request, 'reuniones/detalle_reunion.html', context)


@zoom_login_required
def eliminar_reunion(request, reunion_id):
    """
    Elimina una reunión de Zoom y de la base de datos.
    """
    reunion = get_object_or_404(Reunion, id=reunion_id, creador=request.user)
    
    try:
        # Eliminar de Zoom
        zoom_service = ZoomService()
        zoom_service.eliminar_reunion(reunion.zoom_meeting_id)
        
        # Eliminar de base de datos
        titulo = reunion.titulo
        reunion.delete()
        
        messages.success(request, f'✅ Reunión "{titulo}" eliminada correctamente.')
    
    except Exception as e:
        messages.error(request, f'❌ Error al eliminar: {str(e)}')
    
    return redirect('lista_reuniones')


@zoom_login_required
def sincronizar_reuniones(request):
    """
    Sincroniza reuniones desde Zoom API.
    Útil para obtener reuniones creadas directamente en Zoom.
    """
    try:
        zoom_service = ZoomService()
        meetings = zoom_service.listar_reuniones()
        
        count = 0
        for meeting in meetings:
            # Crear o actualizar en base de datos
            Reunion.objects.update_or_create(
                zoom_meeting_id=meeting['id'],
                defaults={
                    'titulo': meeting['topic'],
                    'join_url': meeting['join_url'],
                    'start_url': meeting.get('start_url', ''),
                    'fecha_inicio': datetime.strptime(
                        meeting['start_time'], 
                        '%Y-%m-%dT%H:%M:%SZ'
                    ),
                    'duracion': meeting['duration'],
                    'creador': request.user
                }
            )
            count += 1
        
        messages.success(request, f'✅ Sincronizadas {count} reuniones desde Zoom.')
    
    except Exception as e:
        messages.error(request, f'❌ Error al sincronizar: {str(e)}')
    
    return redirect('lista_reuniones')

@csrf_exempt  # Zoom no puede enviar CSRF token
def zoom_webhook(request):
    """
    Endpoint que recibe notificaciones de Zoom
    URL debe ser pública: https://tudominio.com/api/zoom/webhook/
    """
    
    if request.method == 'POST':  # Zoom envía POST
        
        # Parsear payload JSON
        payload = json.loads(request.body)  # Convierte string a dict
        
        # Obtener tipo de evento
        event_type = payload.get('event')  # Ejemplo: "meeting.participant_joined"
        
        # Validación de URL (solo primera vez)
        if event_type == 'endpoint.url_validation':  # Zoom valida la URL
            plain_token = payload.get('payload', {}).get('plainToken')  # Token enviado
            return JsonResponse({  # Responder con token encriptado
                'plainToken': plain_token,
                'encryptedToken': plain_token  # En producción encriptar con SHA256
            })
        
        # Procesar evento de participante
        if event_type == 'meeting.participant_joined':
            meeting_id = payload.get('payload', {}).get('object', {}).get('id')  # ID reunión
            participant_name = payload.get('payload', {}).get('object', {}).get('participant', {}).get('user_name')  # Nombre
            
            # Actualizar asistencia en base de datos
            try:
                reunion = Reunion.objects.get(zoom_meeting_id=meeting_id)  # Busca reunión
                participante = Participante.objects.filter(  # Busca participante
                    reunion=reunion,
                    nombre__icontains=participant_name  # Coincidencia parcial
                ).first()
                
                if participante:
                    participante.asistio = True  # Marca asistencia
                    participante.save()  # Guarda en BD
            except Reunion.DoesNotExist:
                pass  # Reunión no encontrada
        
        # Responder con éxito a Zoom
        return JsonResponse({'status': 'success'}, status=200)  # Zoom espera 200 OK
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)  # Solo POST permitido