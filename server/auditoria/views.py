from server.storage_backends import PublicMediaStorage
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import Pregunta, Auditoria, Respuesta, Media, Incidente, Sucursal
from audio.natural_language_processing import split
from auditoria.serializers import PreguntaSerializer, AuditoriaSerializer, RespuestaSerializer, \
    MediaSerializer, RespuestaMultimediaSerializer, IncidenteSerializer
from base64 import b64decode
from audio.speech_to_text import get_transcription
from django.core.files.storage import default_storage

# Recordar que fue seteada la autenticacion por token por default rest_framework.permissions.IsAuthenticated
from server import settings


class AuditoriaViewSet(viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer

    def create(self, request):
        serializer = AuditoriaSerializer(data=request.data)
        if serializer.is_valid():
            sucursal = serializer.validated_data.get('sucursal')

            # Ultimo responsable cuando se hace la auditoria.
            sucursal = get_object_or_404(Sucursal, id=sucursal.id)
            sucursal.ultimo_responsable = request.user
            sucursal.save()

            is_auditoria = Auditoria.objects.filter(sucursal=sucursal, finalizada=False).exists()

            if is_auditoria:
                auditoria = Auditoria.objects.filter(sucursal__exact=sucursal).order_by('-fecha_creacion').first()
                serializer2 = AuditoriaSerializer(auditoria, many=False)
                return Response(serializer2.data, status=status.HTTP_201_CREATED)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # todo fijarse ese serialize
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True)
    def respuestas(self, request, pk):
        # Check if Auditoria exists.
        auditoria = get_object_or_404(Auditoria, id=pk)

        respuestas = Respuesta.objects.filter(auditoria=auditoria)
        serializer = RespuestaSerializer(respuestas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def resultado(self, request, pk):
        # Check if Auditoria exists.
        auditoria = get_object_or_404(Auditoria, id=pk)

        respuestas = Respuesta.objects.filter(auditoria=auditoria)
        preguntas = Pregunta.objects.all()

        is_incidente = Incidente.objects.filter(respuesta__auditoria=auditoria.id) \
            .exclude(status='Confirmado').exists()
        auditoria.finalizada = len(preguntas) == len(respuestas) and not is_incidente

        preguntas_digefe = [p for p in preguntas if p.categoria == 'DIGEFE']
        preguntas_extra = [p for p in preguntas if p.categoria == 'Extranormativa']
        preguntas_faltantes = []

        digefe_aprobada = True
        for preg in preguntas_digefe:
            respuesta = next((r for r in respuestas if r.pregunta.id == preg.id), None)
            if not respuesta or \
                    str(respuesta.respuesta).lower() not in \
                    [str(r).lower() for r in preg.respuestas_correctas]:
                digefe_aprobada = False
                preguntas_faltantes.append(preg)

        extra_aprobada = True
        for preg in preguntas_extra:
            respuesta = next((r for r in respuestas if r.pregunta.id == preg.id), None)
            if not respuesta or \
                    str(respuesta.respuesta).lower() not in \
                    [str(r).lower() for r in preg.respuestas_correctas]:
                extra_aprobada = False
                preguntas_faltantes.append(preg)

        auditoria.digefe_aprobada = digefe_aprobada
        auditoria.extra_aprobada = extra_aprobada
        auditoria.save()

        serializer = AuditoriaSerializer(auditoria, many=False)
        serializer_pregunta = PreguntaSerializer(preguntas_faltantes, many=True)

        data = serializer.data
        data['preguntas_faltantes'] = serializer_pregunta.data

        return Response(data)


class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer

    @action(methods=['get'], detail=True)
    def seccion(self, request, pk=None):
        Preguntas = Pregunta.objects.filter(seccion__exact=pk)
        return Response([(Pregunta.pregunta, Pregunta.id) for Pregunta in Preguntas])


class RespuestaViewSet(viewsets.ModelViewSet):
    queryset = Respuesta.objects.all()
    serializer_class = RespuestaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(methods=['post'], detail=False)
    def transcribir(self, request):
        audio = request.data.get("audio")
        if not audio:
            return Response({"detail": "Bad Request."}, status=status.HTTP_400_BAD_REQUEST)
        audio = audio.replace('data:image/*;charset=utf-8;base64,', '')
        audio_data = b64decode(audio)
        nombre_audio = "audio_" + str(datetime.now()) + '.m4a'
        file = ContentFile(content=audio_data, name=nombre_audio)

        if settings.DEBUG == 1:
            if settings.USE_S3:
                instance = PublicMediaStorage()
                path = instance.save(f'audios/debug/{nombre_audio}', file)
            else:
                path = default_storage.save('files/audios/', file)
        try:
            resVector = split(get_transcription(file))
        except:
            return Response("No se puedo procesar el audio", status=status.HTTP_400_BAD_REQUEST)

        if settings.USE_S3:
            instance = PublicMediaStorage()
            path = instance.save(f'audios/{nombre_audio}', file)
        else:
            path = default_storage.save('files/audios/', file)

        if 'note' in resVector:
            return Response({'respuesta': resVector['response'], 'notas': resVector['note'], 'url_path': path}, status=status.HTTP_200_OK)
        return Response({'respuesta': resVector['response'], 'url_path': path}, status=status.HTTP_200_OK)


class ImagenView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ImagenView, self).dispatch(request, *args, **kwargs)

    @csrf_exempt
    def post(self, request, pk):
        queryset = Respuesta.objects.all()
        respuesta = get_object_or_404(queryset, pk=pk)

        if respuesta.usuario != request.user:
            return Response({"detail": "Unauthorized."}, status=status.HTTP_401_UNAUTHORIZED)

        imagen = request.data.get("imagen")

        if not imagen:
            return Response({"detail": "Bad Request."}, status=status.HTTP_400_BAD_REQUEST)

        imagen = imagen.replace('data:image/jpeg;base64,', '')
        imagen += '======='
        imagen_data = b64decode(imagen)
        nombre_imagen = str(pk) + "_image_" + str(datetime.now()) + '.jpeg'
        file = ContentFile(content=imagen_data, name=nombre_imagen)
        if settings.USE_S3:
            instance = PublicMediaStorage()
            path = instance.save(f'imagenes/{nombre_imagen}', file)
        else:
            path = default_storage.save('files/imagenes/', file)

        url = f'{settings.MEDIA_URL}{path}'
        Media.objects.create(url=url, respuesta=respuesta, tipo='Image')
        return Response({'respuesta': url}, status=status.HTTP_200_OK)


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer


class IncidenteViewSet(viewsets.ModelViewSet):
    queryset = Incidente.objects.all()
    serializer_class = IncidenteSerializer

    def list(self, request):
        queryset_incidente = Incidente.objects.filter((Q(reporta=request.user.id) & ~Q(status='Confirmado')) | (Q(asignado=request.user.id) & ~Q(status='Resuelto') & ~Q(status='Confirmado')))
        incidente_serializer = IncidenteSerializer(queryset_incidente, many=True)
        # Añadir el nombre de la sucursal
        result = []
        for incidente in incidente_serializer.data:
            nombre_de_la_sucursal = None
            if Sucursal.objects.filter(pk=incidente.get("sucursal")).exists():
                nombre_de_la_sucursal = Sucursal.objects.filter(pk=incidente.get("sucursal")).first().nombre

            incidente["nombre_de_la_sucursal"] = nombre_de_la_sucursal
            result.append(incidente)

        return Response(result, status=status.HTTP_200_OK)

    def create(self, request):
        datos = request.data.copy()
        datos["reporta"] = request.user.id  # Usuario logeado
        datosSerializados = IncidenteSerializer(data=datos)
        if datosSerializados.is_valid() and (datos.get('asignado') is not None):
            return Response(datosSerializados.data, status=status.HTTP_201_CREATED)
        return Response(datosSerializados.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            int(pk)
        except:
            return Response({"detail:" "El ID tiene que ser un integer"}, status=status.HTTP_400_BAD_REQUEST)

        incidente = Incidente.objects.filter(reporta=request.user, pk=pk).first() or Incidente.objects.filter(
            asignado=request.user, pk=pk).first()

        if not incidente:
            return Response({"Detail:" "No se encontró un incidente relacionado al usuario de la request."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = IncidenteSerializer(incidente)

        dict_de_respuesta = {
            "incidente": serializer.data,
            "nombre_sucursal": incidente.sucursal.nombre,
            "nombre_del_usuario_asignado": incidente.asignado.username,
            "email_del_usuario_asignado": incidente.asignado.email
        }

        return Response(dict_de_respuesta, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def procesando(self, resquest, pk):
        is_incidente = Incidente.objects.filter(
            id__exact=pk).exists()  # le van apegar a una url que sea auditoria/{id}/procesando, ese id que pasan va a ser por el cual se filtra
        if is_incidente:
            incidente = Incidente.objects.filter(id__exact=pk).first()
            incidente.status = "Procesando"
            incidente.save(update_fields=['status'])
            serializer = IncidenteSerializer(incidente, many=False)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response("Incidente not found", status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True)
    def resolver(self, resquest, pk):
        is_incidente = Incidente.objects.filter(
            id__exact=pk).exists()  # le van apegar a una url que sea auditoria/{id}/resolver, ese id que pasan va a ser por el cual se filtra
        if is_incidente:
            incidente = Incidente.objects.filter(id__exact=pk).first()
            incidente.status = "Resuelto"
            incidente.save(update_fields=['status'])
            serializer = IncidenteSerializer(incidente, many=False)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response("Incidente not found", status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True)
    def confirmar(self, request, pk):
        is_incidente = Incidente.objects.filter(
            id__exact=pk).exists()  # le van apegar a una url que sea auditoria/{id}/confirmar, ese id que pasan va a ser por el cual se filtra
        if is_incidente:
            incidente = Incidente.objects.filter(id__exact=pk).first()
            # todo cmabiar la respuesta de la pregunta
            incidente.status = 'Confirmado'
            incidente.save(update_fields=['status'])
            serializer = IncidenteSerializer(incidente, many=False)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response("Incidente not found", status=status.HTTP_404_NOT_FOUND)


class RespuestaConAudio(RespuestaViewSet, viewsets.ModelViewSet):
    def get_queryset(self):
        return super().get_queryset()

    def create(self, request):
        serializer_global = RespuestaMultimediaSerializer(data=request.data)

        if serializer_global.is_valid():
            # Primero se crea la respuesta
            respuesta_dict = {
                "texto": serializer_global.texto,
                "auditoria": serializer_global.auditoria_id,
                "pregunta": serializer_global.pregunta_id,
                "usuario": serializer_global.usuario_id,
                "validez": serializer_global.validez,
                "audio": serializer_global.audio
            }
            serializer_respuesta = RespuestaSerializer(data=respuesta_dict)
            if not serializer_respuesta.is_valid():
                return Response(serializer_respuesta.errors, status=status.HTTP_400_BAD_REQUEST)
            respuesta_reciente = serializer_respuesta.save()

            # Una vez la respuesta esta creada, hay que crear la media y asociarla a la respuesta recientemente creada.
            media_agregada = []
            for url in serializer_global.lista_url:
                media_dict = {
                    "url": url,
                    "respuesta": respuesta_reciente.id,
                    "tipo": serializer_global.tipo
                }
                serializer_media = MediaSerializer(data=media_dict)
                if not serializer_media.is_valid():
                    # En caso de que la media este mal, hay que eliminar la respuesta creada anteriormente y
                    # todos los onjetos Media anteriores.
                    Respuesta.objects.filter(id=respuesta_reciente.id).delete()
                    for media in media_agregada:
                        Media.objects.filter(id=media.id).delete()
                    return Response(serializer_respuesta.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer_media.save()
                media_agregada.append(serializer_media.data)

            respuesta_con_audio_json = {
                "Detalle": "La siguiente respuesta junto con la correspondiente media fue persisitda correctamente",
                "Respuesta": serializer_respuesta.data,
                "Media": media_agregada,
            }
            return Response(respuesta_con_audio_json, status=status.HTTP_201_CREATED)

        return Response(serializer_global.errors, status=status.HTTP_400_BAD_REQUEST)
