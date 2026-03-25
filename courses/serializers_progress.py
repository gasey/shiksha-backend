from rest_framework import serializers
from .models_progress import VideoProgress


class VideoProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoProgress
        fields = [
            "recording",
            "last_position",
            "completed"
        ]
