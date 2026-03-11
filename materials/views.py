from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import StudyMaterial, MaterialFile
from .serializers import StudyMaterialSerializer
from courses.models import Chapter


class ChapterMaterials(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, chapter_id):

        materials = StudyMaterial.objects.filter(
            chapter_id=chapter_id
        ).prefetch_related("files")

        serializer = StudyMaterialSerializer(materials, many=True)

        return Response(serializer.data)


class UploadStudyMaterial(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, chapter_id):

        chapter = get_object_or_404(Chapter, id=chapter_id)

        material = StudyMaterial.objects.create(
            chapter=chapter,
            title=request.data.get("title"),
            description=request.data.get("description", ""),
            uploaded_by=request.user
        )

        files = request.FILES.getlist("files")

        for f in files:
            MaterialFile.objects.create(
                material=material,
                file=f
            )

        return Response(
            {"detail": "Material uploaded successfully"},
            status=status.HTTP_201_CREATED
        )
