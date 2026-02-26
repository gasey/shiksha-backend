from django.conf import settings
from livekit.api import AccessToken, VideoGrants


def generate_livekit_token(user, session, is_teacher=False):
    token = AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET,
    )

    token.with_identity(str(user.id))
    token.with_name(user.email)

    grants = VideoGrants(
        room_join=True,
        room=session.room_name,
        can_publish=is_teacher,
        can_subscribe=True,
    )

    token.with_grants(grants)

    return token.to_jwt()
