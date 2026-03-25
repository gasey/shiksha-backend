from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models_progress import VideoProgress
from .models_recordings import SessionRecording


class GetVideoProgressView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, recording_id):

        progress = VideoProgress.objects.filter(
            student=request.user,
            recording_id=recording_id
        ).first()

        if not progress:
            return Response({"last_position": 0})

        return Response({
            "last_position": progress.last_position
        })


class SaveVideoProgressView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, recording_id):

        recording = get_object_or_404(SessionRecording, id=recording_id)

        progress, _ = VideoProgress.objects.get_or_create(
            student=request.user,
            recording=recording
        )

        progress.last_position = request.data.get("last_position", 0)
        progress.completed = request.data.get("completed", False)

        progress.save()

        return Response({"status": "ok"})
