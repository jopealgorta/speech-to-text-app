import uuid
from datetime import datetime

from django.core.files.base import ContentFile
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import Pregunta, Auditoria, Respuesta, Media, Incidente, Sucursal
from audio.natural_language_processing import split
from auditoria.serializers import PreguntaSerializer, AuditoriaSerializer, RespuestaSerializer, \
    MediaSerializer, RespuestaMultimediaSerializer, IncidenteSerializer, MinRespuestaSerializer
from base64 import b64decode
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from audio.speech_to_text import get_transcription
from server.storage_backends import PublicMediaStorage
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

        respuestas = Respuesta.objects.filter(auditoria__exact=pk)
        serializer = MinRespuestaSerializer(respuestas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def resultado(self, request, pk):
        # Check if Auditoria exists.
        auditoria = get_object_or_404(Auditoria, id=pk)

        respuestas = Respuesta.objects.filter(auditoria__exact=pk)
        preguntas = Pregunta.objects.all()

        auditoria.finalizada = len(preguntas) == len(respuestas)

        preguntas_digefe = [p for p in preguntas if p.categoria == 'DIGEFE']

        aprobada = True
        for preg in preguntas_digefe:
            respuesta = next((r for r in respuestas if r.pregunta.id == preg.id), None)
            if not respuesta or preg.respuesta_correcta != respuesta.respuesta:
                aprobada = False

        auditoria.aprobada = aprobada
        auditoria.save()

        serializer = AuditoriaSerializer(auditoria, many=False)
        return Response(serializer.data)


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

    def create(self, request):
        serializer = RespuestaSerializer(data=request.data)
        if serializer.is_valid():
            is_adui_not_finished=Auditoria.objects.filter(id=request.data.get("auditoria"),finalizada=False).exists()
            is_respuesta=Respuesta.objects.filter(auditoria=request.data.get("auditoria")).exists()
            if is_adui_not_finished and  is_respuesta :
                respuesta=Respuesta.objects.filter(auditoria=request.data.get("auditoria"),pregunta=request.data.get("pregunta"))[0]
                respuesta.respuesta=request.data.get("respuesta")
                respuesta.notas=request.data.get("notas")
                respuesta.save(update_fields=['respuesta','notas'])
                return Response(RespuestaSerializer(respuesta).data,status=status.HTTP_202_ACCEPTED)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True,)
    def transcribir(self, request, pk=None):
        audio = request.data.get("audio")
        audio = audio.replace('data:audio/mpeg;base64,', '')
        missing_padding = len(audio) % 4
        if missing_padding:
            audio += b'=' * (4 - missing_padding)
        audio_data = b64decode(audio)
        nombre_audio = str(datetime.now())  # todo: cambiar nombre
        file = ContentFile(content=audio_data, name=f'{nombre_audio}.mp3')
        try:
            resVector = split(get_transcription(file))
        except:  # no se puedo transcripibr el audio
            return Response("No se puedo procesar el audio", status=status.HTTP_418_IM_A_TEAPOT)
        """
        if settings.USE_S3:
           # path = PublicMediaStorage.save('/audios', file)
        else:
           # path = default_storage.save('files/audios_de_respuesta/', file)
        # media = MediaSerializer(data={'url': path, 'respuesta': pk, 'tipo': 'Audio'})
        """
        if resVector['note'] is not None:
            return Response({'respuesta': resVector['response'], 'notas': resVector['note']}, status=status.HTTP_200_OK)
        return Response({'respuesta': resVector['response']}, status=status.HTTP_200_OK)

class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer


class IncidenteViewSet(viewsets.ModelViewSet):
    queryset = Incidente.objects.all()
    serializer_class = IncidenteSerializer

    def create(self, request):
        datosSerializados = IncidenteSerializer(data=request.data)
        datos = request.data.copy()
        datos["reporta"] = request.user.id #Usuario logeado
        datos["pregunta"] = request.data.get('pregunta') #obtiene de donde se manda la request
        datos["asignado"] = request.data.get('asignado') #obtiene del audio
        datos["accion"] = request.data.get('accion')   #obtiene del audio
        datos["sucursal"] = request.data.get('sucursal')   #obtiene de donde se manda la request
        datos["pregnta"] = request.data.get('pregnta')   #obtiene de donde se manda la request
        datosSerializados = IncidenteSerializer(data=datos)
        if datosSerializados.is_valid():
            return Response(datosSerializados.data, status=status.HTTP_201_CREATED)
        return Response(datosSerializados.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(method=get)
    def cerrarIncidente(self,request,pk):
            incidente = Incidente.objects.filter(id__exact=pk) # le van apegar a una url que sea auditoria/cierre/{id}, ese id que pasan va a ser por el cual se filtra
            incidente["estatus"] = 2
            incidente.save()
            return #redirecciona a la url para responder la pregunta incidente["pregnta"] en la sucursal incidente["sucursal"]

    def solucionarIncidente(incidente_id):
            incidente = Incidente.objects.filter(id__exact=datosSerializados.validated_data.get('id')) # le van apegar a una url que sea auditoria/cierre/{id}, ese id que pasan va a ser por el cual se filtra
            incidente["estatus"] = 1
            return #redirecciona a la url para responder la pregunta incidente["pregnta"] en la sucursal incidente["sucursal"]

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
