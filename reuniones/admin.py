from django.contrib import admin
from .models import Reunion

@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    # Solo mostramos el ID por ahora para que no de error.
    # Una vez que veamos la tabla, sabremos qué nombres usar.
    list_display = ('id',)