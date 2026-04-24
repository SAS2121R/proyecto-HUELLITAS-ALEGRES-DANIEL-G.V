from django.http import HttpResponse


def lista_historiales(request):
    return HttpResponse("stub")


def crear_historial(request):
    return HttpResponse("stub")


def detalle_historial(request, pk):
    return HttpResponse("stub")


def editar_historial(request, pk):
    return HttpResponse("stub")


def historial_por_mascota(request, mascota_pk):
    return HttpResponse("stub")


def atender_cita(request, cita_pk):
    return HttpResponse("stub")
